import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_instructor, require_student
from app.schemas.enrollment_schemas import (
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentProgressUpdate,
    EnrollmentOut,
)
from app.services.enrollment_service import EnrollmentService

router = APIRouter()


def _is_instructor(user: User) -> bool:
    return user.role.name.lower() == "instructor"


def _ensure_owner_or_instructor(user: User, owner_id: uuid.UUID) -> None:
    """An enrollment is the student's own record, or Instructor's to manage.
    Admin has no business here - its job is users/roles only."""
    if _is_instructor(user) or user.id == owner_id:
        return
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You do not have permission to access this resource",
    )


# ---- Instructor only: list all ----
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[EnrollmentOut],
    dependencies=[Depends(require_instructor)],
)
async def list_enrollments(
    db: AsyncSession = Depends(get_db),
):
    return await EnrollmentService(db).list_all()


# ---- Owner (student) or Instructor: view one ----
@router.get(
    "/{enrollment_id}", status_code=status.HTTP_200_OK, response_model=EnrollmentOut
)
async def get_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = await EnrollmentService(db).get(enrollment_id)
    _ensure_owner_or_instructor(current_user, enrollment.student_id)
    return enrollment


# ---- Student only: self-enrolls ----
@router.post(
    "",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_student)],
)
async def create_enrollment(
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await EnrollmentService(db).enroll(
        current_user.id,
        payload.course_id,
    )


# ---- Instructor only: update ----
@router.put(
    "/{enrollment_id}",
    status_code=status.HTTP_200_OK,
    response_model=EnrollmentOut,
    dependencies=[Depends(require_instructor)],
)
async def update_enrollment(
    enrollment_id: uuid.UUID,
    payload: EnrollmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await EnrollmentService(db).update(
        enrollment_id,
        payload.status,
    )


# ---- Instructor only: delete ----
@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_instructor)],
)
async def delete_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await EnrollmentService(db).delete(enrollment_id)


# ---- Owner (student) or Instructor: progress ----
@router.patch(
    "/{enrollment_id}/progress",
    status_code=status.HTTP_200_OK,
    response_model=EnrollmentOut,
)
async def update_progress(
    enrollment_id: uuid.UUID,
    payload: EnrollmentProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = await EnrollmentService(db).get(enrollment_id)

    _ensure_owner_or_instructor(
        current_user,
        enrollment.student_id,
    )

    return await EnrollmentService(db).update_progress(
        enrollment_id,
        payload.status,
    )


# ---- Owner (student) or Instructor: complete ----
@router.patch(
    "/{enrollment_id}/complete",
    status_code=status.HTTP_200_OK,
    response_model=EnrollmentOut,
)
async def mark_complete(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = await EnrollmentService(db).get(enrollment_id)

    _ensure_owner_or_instructor(
        current_user,
        enrollment.student_id,
    )

    return await EnrollmentService(db).mark_complete(enrollment_id)
