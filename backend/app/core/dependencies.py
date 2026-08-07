from fastapi import Depends, HTTPException, Request, status

from app.models.user import User


async def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
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


require_admin = RoleChecker(["Admin"])
require_instructor = RoleChecker(["Instructor"])
require_student = RoleChecker(["Student"])
require_non_admin = RoleChecker(["Instructor", "Student"])
require_user = get_current_user
