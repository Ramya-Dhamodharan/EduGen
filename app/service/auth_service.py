from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.config.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_otp,
    verify_otp,
)
from app.models.user import User
from app.schema.user_schemas import UserOut
from app.repo.role_repo import RoleRepository
from app.repo.user_repo import UserRepository
from app.schema.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    ResetPasswordRequest,
)
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
    def register(self, data: RegisterRequest) -> UserOut:
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

        result = self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user.id)
        )

        user = result.scalar_one()

        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    # ---------- Login ----------
    def login(self, data: LoginRequest) -> tuple[str, str]:
        """Returns (access_token, refresh_token)."""

        user = self.users.get_by_email(data.email)

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

        access = create_access_token(
            {"sub": str(user.id), "role": user.role.name}
        )

        refresh = create_refresh_token(
            {"sub": str(user.id)}
        )

        return access, refresh

    # ---------- Refresh ----------
    def refresh(self, refresh_token: str | None) -> str:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing",
            )

        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token scope",
                )

            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user = self.users.get_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or not found",
            )

        return create_access_token(
            {"sub": str(user.id), "role": user.role.name}
        )

    # ---------- Forgot / Reset password ----------
    def forgot_password(self, email: str) -> None:
        user = self.users.get_by_email(email)

        if not user:
            return

        otp = generate_otp(user.email)
        send_otp_email(user.email, otp)

    def reset_password(
        self,
        data: ResetPasswordRequest,
    ) -> None:

        if not verify_otp(data.email, data.otp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code",
            )

        user = self.users.get_by_email(data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.password_hash = hash_password(data.new_password)

        self.db.commit()