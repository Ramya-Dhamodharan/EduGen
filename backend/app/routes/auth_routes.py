from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth_schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user_schemas import UserOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await AuthService(db).register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    access_token, refresh_token = await AuthService(db).login(payload)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
)
async def refresh(
    refresh_token: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    new_access = await AuthService(db).refresh(refresh_token)
    return TokenResponse(access_token=new_access)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await AuthService(db).forgot_password(payload.email)

    return {
        "message": "If the email exists, an OTP code has been dispatched."
    }


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await AuthService(db).reset_password(payload)

    return {
        "message": "Password updated successfully!"
    }


@router.get(
    "/me",
    response_model=UserOut,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Return the currently authenticated user."""
    return current_user