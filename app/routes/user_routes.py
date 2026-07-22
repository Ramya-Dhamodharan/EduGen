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
from app.schemas.enrollment_schemas import EnrollmentOut
from app.schemas.certificate_schemas import CertificateOut
from app.schemas.payment_schemas import PaymentOut
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

@router.get("", response_model=List[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    """List all users. Admin only."""
    return UserService(db).list_users()


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Admin only."""
    print(UserCreate)
    return UserService(db).create_user(payload)


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
    """Delete a user. Admin only. Admins cannot delete themselves."""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )
    UserService(db).delete_user(user_id)


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
    """Activate or deactivate a user. Admin only."""
    if current_user.id == user_id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )
    return UserService(db).set_status(user_id, payload.is_active)


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
    """Assign a role to a user. Admin only."""
    return UserService(db).assign_role(user_id, payload.role_id)


# ==========================
# Admin or the user themselves
# ==========================

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a user by ID. Admin, or the user viewing their own profile."""
    _ensure_admin_or_self(current_user, user_id)
    return UserService(db).get_user(user_id)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user. Admin, or the user updating their own profile.
    Non-admins cannot change role_id or is_active on their own account
    (those are stripped below), so they cannot self-promote.
    """
    _ensure_admin_or_self(current_user, user_id)

    if current_user.role.name.lower() != "admin":
        payload.role_id = None
        payload.is_active = None

    return UserService(db).update_user(user_id, payload)


@router.get("/{user_id}/enrollments", response_model=List[EnrollmentOut])
def list_user_enrollments(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List a user's enrollments. Admin, or the user themselves."""
    _ensure_admin_or_self(current_user, user_id)
    return UserService(db).list_enrollments(user_id)


@router.get("/{user_id}/certificates", response_model=List[CertificateOut])
def list_user_certificates(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List a user's certificates. Admin, or the user themselves."""
    _ensure_admin_or_self(current_user, user_id)
    return UserService(db).list_certificates(user_id)


@router.get("/{user_id}/payments", response_model=List[PaymentOut])
def list_user_payments(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List a user's payments. Admin, or the user themselves."""
    _ensure_admin_or_self(current_user, user_id)
    return UserService(db).list_payments(user_id)