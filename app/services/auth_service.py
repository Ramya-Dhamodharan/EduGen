from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_otp,
    verify_otp,
)
from app.models.user import User
from app.repositories.role_repo import RoleRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth_schemas import RegisterRequest, LoginRequest, ResetPasswordRequest
from app.utils.email import send_otp_email

DEFAULT_ROLE = "Student"


class AuthService:
    """
    Business rules for authentication.
    Routes call this layer; this layer calls the repositories.
    """

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)

    # ---------- Register ----------
    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            )

        role = self.roles.get_by_name(DEFAULT_ROLE)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Default role '{DEFAULT_ROLE}' is missing. Seed the roles table first.",
            )

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=role.id,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ---------- Login ----------
    def login(self, data: LoginRequest) -> tuple[str, str]:
        """Returns (access_token, refresh_token)."""
        user = self.users.get_by_email(data.email)
        # Same error for unknown email and wrong password so attackers
        # cannot probe which emails are registered.
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        access = create_access_token({"sub": str(user.id), "role": user.role.name})
        refresh = create_refresh_token({"sub": str(user.id)})
        return access, refresh

    # ---------- Refresh ----------
    def refresh(self, refresh_token: str | None) -> str:
        """Validates the refresh cookie and returns a new access token."""
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token scope")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        # Re-check the user so a deactivated account cannot keep minting
        # access tokens, and so the new token carries the current role.
        user = self.db.query(User).filter(User.id == payload.get("sub")).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")

        return create_access_token({"sub": str(user.id), "role": user.role.name})

    # ---------- Forgot / Reset password ----------
    def forgot_password(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if not user:
            # Do not reveal whether the email exists.
            return
        otp = generate_otp(user.email)
        # Emails when SMTP is configured in .env, else prints to terminal.
        send_otp_email(user.email, otp)

    def reset_password(self, data: ResetPasswordRequest) -> None:
        if not verify_otp(data.email, data.otp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code",
            )
        user = self.users.get_by_email(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.password_hash = hash_password(data.new_password)
        self.db.commit()
