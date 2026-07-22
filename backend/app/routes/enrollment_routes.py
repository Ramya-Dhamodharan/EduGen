import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff
from app.schemas.enrollment_schemas import (
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentProgressUpdate,
    EnrollmentOut,
)
from app.services.enrollment_service import EnrollmentService

router = APIRouter()


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _ensure_owner_or_staff(user: User, owner_id: uuid.UUID) -> None:
    if _is_staff(user) or user.id == owner_id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")


# ---- Staff: list all ----
@router.get("", response_model=List[EnrollmentOut], dependencies=[Depends(require_staff)])
def list_enrollments(db: Session = Depends(get_db)):
    return EnrollmentService(db).list_all()


# ---- Owner or staff: view one ----
@router.get("/{enrollment_id}", response_model=EnrollmentOut)
def get_enrollment(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    e = EnrollmentService(db).get(enrollment_id)
    _ensure_owner_or_staff(current_user, e.student_id)
    return e


# ---- Student self-enrolls (student_id from token, not body) ----
@router.post("", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EnrollmentService(db).enroll(current_user.id, payload.course_id)


# ---- Staff: update / delete ----
@router.put("/{enrollment_id}", response_model=EnrollmentOut, dependencies=[Depends(require_staff)])
def update_enrollment(enrollment_id: uuid.UUID, payload: EnrollmentUpdate, db: Session = Depends(get_db)):
    return EnrollmentService(db).update(enrollment_id, payload.status)


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_staff)])
def delete_enrollment(enrollment_id: uuid.UUID, db: Session = Depends(get_db)):
    EnrollmentService(db).delete(enrollment_id)


# ---- Owner or staff: progress / complete ----
@router.patch("/{enrollment_id}/progress", response_model=EnrollmentOut)
def update_progress(
    enrollment_id: uuid.UUID,
    payload: EnrollmentProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    e = EnrollmentService(db).get(enrollment_id)
    _ensure_owner_or_staff(current_user, e.student_id)
    return EnrollmentService(db).update_progress(enrollment_id, payload.status)


@router.patch("/{enrollment_id}/complete", response_model=EnrollmentOut)
def mark_complete(
    enrollment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    e = EnrollmentService(db).get(enrollment_id)
    _ensure_owner_or_staff(current_user, e.student_id)
    return EnrollmentService(db).mark_complete(enrollment_id)