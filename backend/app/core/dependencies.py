from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "access":
            raise unauthorized

        user_id = payload.get("sub")
        if user_id is None:
            raise unauthorized

    except JWTError:
        raise unauthorized

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise unauthorized

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


class RoleChecker:
    """Usage: Depends(RoleChecker(["Admin"])) - case-insensitive role match."""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = [r.lower() for r in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name.lower() not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

# Admin only. Admin's job is user + role management - nothing else.
require_admin = RoleChecker(["Admin"])

# Instructor only. Course/module/lesson/quiz authoring, grading, feedback,
# enrollment management, certificates, payments oversight - all Instructor
# job, not Admin's and not Student's.
require_instructor = RoleChecker(["Instructor"])

# Student only. Enrolling, attempting quizzes, submitting answers, paying,
# and reviewing courses are the Student's job - not Admin's, not Instructor's.
require_student = RoleChecker(["Student"])

# Instructor OR Student, but never Admin. Use for read-only catalog/content
# endpoints (courses, modules, lessons, quizzes, categories, reviews) that
# both roles legitimately need to browse, while keeping Admin scoped to
# user + role management only.
require_non_admin = RoleChecker(["Instructor", "Student"])

# Any authenticated, active user (Admin, Instructor, or Student).
# This is just get_current_user; aliased for readability at call sites.
require_user = get_current_user