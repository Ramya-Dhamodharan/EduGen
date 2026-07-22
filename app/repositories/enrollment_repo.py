<<<<<<< HEAD
import uuid

from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enrollment_id: uuid.UUID) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .filter(Enrollment.id == enrollment_id)
            .first()
        )

    def get_all(self) -> list[Enrollment]:
        return self.db.query(Enrollment).all()

    def get_by_student_id(self, student_id: uuid.UUID) -> list[Enrollment]:
        return (
            self.db.query(Enrollment)
            .filter(Enrollment.student_id == student_id)
            .all()
        )

    def get_by_student_and_course(
        self,
        student_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> Enrollment | None:
        return (
            self.db.query(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
            )
            .first()
        )

    def create(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def update(self, enrollment: Enrollment) -> Enrollment:
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def delete(self, enrollment: Enrollment) -> None:
        self.db.delete(enrollment)
        self.db.commit()
=======
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.course import Course

from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentUpdate,
    ProgressUpdate,
    StatusUpdate,
)


# -----------------------------------------
# Create Enrollment
# -----------------------------------------
def create_enrollment(db: Session, enrollment: EnrollmentCreate):

    # Check student exists
    student = db.query(Student).filter(
        Student.id == enrollment.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check course exists
    course = db.query(Course).filter(
        Course.id == enrollment.course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check duplicate enrollment
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == enrollment.student_id,
        Enrollment.course_id == enrollment.course_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already enrolled in this course"
        )

    new_enrollment = Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        progress=0,
        status="enrolled"
    )

    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return new_enrollment


# -----------------------------------------
# Get All Enrollments
# -----------------------------------------
def get_all_enrollments(db: Session):

    return db.query(Enrollment).all()


# -----------------------------------------
# Get Enrollment By ID
# -----------------------------------------
def get_enrollment_by_id(
    db: Session,
    enrollment_id: UUID
):

    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    return enrollment


# -----------------------------------------
# Update Enrollment
# -----------------------------------------
def update_enrollment(
    db: Session,
    enrollment_id: UUID,
    enrollment_data: EnrollmentUpdate
):

    enrollment = get_enrollment_by_id(
        db,
        enrollment_id
    )

    update_data = enrollment_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(enrollment, key, value)

    enrollment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(enrollment)

    return enrollment


# -----------------------------------------
# Delete Enrollment
# -----------------------------------------
def delete_enrollment(
    db: Session,
    enrollment_id: UUID
):

    enrollment = get_enrollment_by_id(
        db,
        enrollment_id
    )

    db.delete(enrollment)
    db.commit()

    return {
        "message": "Enrollment deleted successfully"
    }


# -----------------------------------------
# Update Progress
# -----------------------------------------
def update_progress(
    db: Session,
    enrollment_id: UUID,
    progress_data: ProgressUpdate
):

    enrollment = get_enrollment_by_id(
        db,
        enrollment_id
    )

    enrollment.progress = progress_data.progress
    enrollment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(enrollment)

    return enrollment


# -----------------------------------------
# Update Status
# -----------------------------------------
def update_status(
    db: Session,
    enrollment_id: UUID,
    status_data: StatusUpdate
):

    enrollment = get_enrollment_by_id(
        db,
        enrollment_id
    )

    enrollment.status = status_data.status
    enrollment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(enrollment)

    return enrollment


# -----------------------------------------
# Start Course
# -----------------------------------------
def start_course(
    db: Session,
    enrollment_id: UUID
):

    enrollment = get_enrollment_by_id(
        db,
        enrollment_id
    )

    enrollment.started_at = datetime.utcnow()
    enrollment.status = "in_progress"

    db.commit()
    db.refresh(enrollment)

    return enrollment


# -----------------------------------------
# Complete Course
# -----------------------------------------
def complete_course(
    db: Session,
    enrollment_id: UUID
):

    enrollment = get_enrollment_by_id(
        db,
        enrollment_id
    )

    enrollment.completed_at = datetime.utcnow()
    enrollment.progress = 100
    enrollment.status = "completed"

    db.commit()
    db.refresh(enrollment)

    return enrollment


# -----------------------------------------
# Get Student Enrollments
# -----------------------------------------
def get_student_enrollments(
    db: Session,
    student_id: int
):

    return db.query(Enrollment).filter(
        Enrollment.student_id == student_id
    ).all()


# -----------------------------------------
# Get Course Enrollments
# -----------------------------------------
def get_course_enrollments(
    db: Session,
    course_id: int
):

    return db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
>>>>>>> origin/dev
