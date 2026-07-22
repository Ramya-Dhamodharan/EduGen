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