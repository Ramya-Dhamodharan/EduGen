from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User


PUBLIC_PATHS = {
    "/",
    "/api/auth/register",
    "/api/auth/login",
    "/api/auth/refresh-token",
    "/api/auth/logout",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Let CORS preflight requests through untouched.
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            if payload.get("type") != "access":
                raise JWTError("Not an access token")

            user_id = payload.get("sub")
            if user_id is None:
                raise JWTError("Missing subject claim")

        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        async with SessionLocal() as db:
            result = await db.execute(
                select(User).options(selectinload(User.role)).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

        if user is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            return JSONResponse(
                status_code=403,
                content={"detail": "Account is deactivated"},
            )

        # Available to every downstream dependency/route via the Request.
        request.state.user = user

        return await call_next(request)
