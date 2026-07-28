from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode the Bearer access token and load the active user."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            raise unauthorized
        user_id = payload.get("sub")
        if user_id is None:
            raise unauthorized
    except JWTError:
        raise unauthorized

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise unauthorized
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
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


# ==========================
# Reusable permission presets
# Import these directly instead of re-instantiating RoleChecker everywhere,
# so the whole app shares one consistent definition of each policy.
#
#   from app.core.dependencies import require_admin, require_staff
#   router = APIRouter(dependencies=[Depends(require_admin)])
# ==========================

# Admin only.
require_admin = RoleChecker(["Admin"])

# Admin OR Instructor ("staff"). Use for course content and catalog.
require_staff = RoleChecker(["Admin", "Instructor"])

# Any authenticated, active user (Admin, Instructor, or Student).
# This is just get_current_user; aliased for readability at call sites.
require_user = get_current_user