import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    UserOut,
    UserStatusUpdate,
    UserRoleUpdate,
)
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, require_admin

router = APIRouter()


def _ensure_admin_or_self(current_user: User, target_user_id: uuid.UUID) -> None:
    """Allow if the requester is an Admin or is acting on their own record."""
    if current_user.role.name.lower() == "admin":
        return
    if current_user.id == target_user_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this resource",
    )


# ==========================
# Admin-only management
# ==========================

# Admin only: list all users.
@router.get("", response_model=List[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    return UserService(db).list_users()


# Admin only: create a new user.
@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create_user(payload)


# Admin only: delete a user (admins cannot delete themselves).
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )
    UserService(db).delete_user(user_id)


# Admin only: activate or deactivate a user.
@router.patch(
    "/{user_id}/status",
    response_model=UserOut,
    dependencies=[Depends(require_admin)],
)
def update_user_status(
    user_id: uuid.UUID,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == user_id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )
    return UserService(db).set_status(user_id, payload.is_active)


# Admin only: assign a role to a user.
@router.patch(
    "/{user_id}/role",
    response_model=UserOut,
    dependencies=[Depends(require_admin)],
)
def assign_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
):
    return UserService(db).assign_role(user_id, payload.role_id)


# ==========================
# Admin or the user themselves
# ==========================

# Admin, or the user viewing their own profile.
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin_or_self(current_user, user_id)
    return UserService(db).get_user(user_id)


# Admin, or the user updating their own profile.
# Non-admins cannot change role_id or is_active (stripped below), so no self-promotion.
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin_or_self(current_user, user_id)

    if current_user.role.name.lower() != "admin":
        # Drop these from the "set" fields entirely. Assigning None marks
        # them as explicitly set, so model_dump(exclude_unset=True) would
        # write NULL into two NOT NULL columns.
        payload.__pydantic_fields_set__.discard("role_id")
        payload.__pydantic_fields_set__.discard("is_active")

    return UserService(db).update_user(user_id, payload)
