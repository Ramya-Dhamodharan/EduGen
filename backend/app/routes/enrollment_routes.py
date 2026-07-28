import uuid
from typing import List
 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
 
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
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You do not have permission to access this resource",
    )
 
 
# ---- Staff: list all ----
@router.get("", response_model=List[EnrollmentOut], dependencies=[Depends(require_staff)])
async def list_enrollments(
    db: AsyncSession = Depends(get_db),
):
    return await EnrollmentService(db).list_all()
 
 
# ---- Owner or staff: view one ----
@router.get("/{enrollment_id}", response_model=EnrollmentOut)
async def get_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = await EnrollmentService(db).get(enrollment_id)
    _ensure_owner_or_staff(current_user, enrollment.student_id)
    return enrollment
 
 
# ---- Student self-enrolls ----
@router.post("", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await EnrollmentService(db).enroll(
        current_user.id,
        payload.course_id,
    )
 
 
# ---- Staff: update ----
@router.put(
    "/{enrollment_id}",
    response_model=EnrollmentOut,
    dependencies=[Depends(require_staff)],
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
 
 
# ---- Staff: delete ----
@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_staff)],
)
async def delete_enrollment(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await EnrollmentService(db).delete(enrollment_id)
 
 
# ---- Owner or staff: progress ----
@router.patch("/{enrollment_id}/progress", response_model=EnrollmentOut)
async def update_progress(
    enrollment_id: uuid.UUID,
    payload: EnrollmentProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = await EnrollmentService(db).get(enrollment_id)
 
    _ensure_owner_or_staff(
        current_user,
        enrollment.student_id,
    )
 
    return await EnrollmentService(db).update_progress(
        enrollment_id,
        payload.status,
    )
 
 
# ---- Owner or staff: complete ----
@router.patch("/{enrollment_id}/complete", response_model=EnrollmentOut)
async def mark_complete(
    enrollment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollment = await EnrollmentService(db).get(enrollment_id)
 
    _ensure_owner_or_staff(
        current_user,
        enrollment.student_id,
    )
 
    return await EnrollmentService(db).mark_complete(enrollment_id)