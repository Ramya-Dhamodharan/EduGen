<<<<<<< HEAD
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
=======
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentResponse,
    ProgressUpdate,
    StatusUpdate
)

from app.repositories.enrollment_repo import (
    create_enrollment,
    get_all_enrollments,
    get_enrollment_by_id,
    update_enrollment,
    delete_enrollment,
    update_progress,
    update_status,
    start_course,
    complete_course,
    get_student_enrollments,
    get_course_enrollments
)

router = APIRouter(
    prefix="/api/v1/enrollments",
    tags=["Enrollments"]
)


# -----------------------------------
# Create Enrollment
# -----------------------------------
@router.post(
    "",
    response_model=EnrollmentResponse,
    status_code=201
)
def create(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db)
):
    return create_enrollment(db, enrollment)


# -----------------------------------
# Get All Enrollments
# -----------------------------------
@router.get(
    "",
    response_model=list[EnrollmentResponse]
)
def get_all(
    db: Session = Depends(get_db)
):
    return get_all_enrollments(db)


# -----------------------------------
# Get Enrollment By ID
# -----------------------------------
@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse
)
def get_one(
    enrollment_id: UUID,
    db: Session = Depends(get_db)
):
    return get_enrollment_by_id(db, enrollment_id)


# -----------------------------------
# Update Enrollment
# -----------------------------------
@router.put(
    "/{enrollment_id}",
    response_model=EnrollmentResponse
)
def update(
    enrollment_id: UUID,
    enrollment: EnrollmentUpdate,
    db: Session = Depends(get_db)
):
    return update_enrollment(
        db,
        enrollment_id,
        enrollment
    )


# -----------------------------------
# Delete Enrollment
# -----------------------------------
@router.delete("/{enrollment_id}")
def delete(
    enrollment_id: UUID,
    db: Session = Depends(get_db)
):
    return delete_enrollment(
        db,
        enrollment_id
    )


# -----------------------------------
# Update Progress
# -----------------------------------
@router.patch(
    "/{enrollment_id}/progress",
    response_model=EnrollmentResponse
)
def progress(
    enrollment_id: UUID,
    progress: ProgressUpdate,
    db: Session = Depends(get_db)
):
    return update_progress(
        db,
        enrollment_id,
        progress
    )


# -----------------------------------
# Update Status
# -----------------------------------
@router.patch(
    "/{enrollment_id}/status",
    response_model=EnrollmentResponse
)
def status(
    enrollment_id: UUID,
    status_data: StatusUpdate,
    db: Session = Depends(get_db)
):
    return update_status(
        db,
        enrollment_id,
        status_data
    )


# -----------------------------------
# Start Course
# -----------------------------------
@router.patch(
    "/{enrollment_id}/start",
    response_model=EnrollmentResponse
)
def start(
    enrollment_id: UUID,
    db: Session = Depends(get_db)
):
    return start_course(
        db,
        enrollment_id
    )


# -----------------------------------
# Complete Course
# -----------------------------------
@router.patch(
    "/{enrollment_id}/complete",
    response_model=EnrollmentResponse
)
def complete(
    enrollment_id: UUID,
    db: Session = Depends(get_db)
):
    return complete_course(
        db,
        enrollment_id
    )
>>>>>>> origin/dev
