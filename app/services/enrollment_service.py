import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.course import Course


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, enrollment_id: uuid.UUID) -> Enrollment:
        e = self.db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
        if not e:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Enrollment {enrollment_id} not found")
        return e

    def list_all(self) -> List[Enrollment]:
        return self.db.query(Enrollment).all()

    def get(self, enrollment_id: uuid.UUID) -> Enrollment:
        return self._get(enrollment_id)

    def list_for_student(self, student_id: uuid.UUID) -> List[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.student_id == student_id).all()

    def enroll(self, student_id: uuid.UUID, course_id: uuid.UUID) -> Enrollment:
        if not self.db.query(Course).filter(Course.id == course_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Course {course_id} does not exist")

        existing = (
            self.db.query(Enrollment)
            .filter(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
            .first()
        )
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already enrolled in this course")

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def update(self, enrollment_id: uuid.UUID, status_value: str | None) -> Enrollment:
        e = self._get(enrollment_id)
        if status_value:
            e.status = EnrollmentStatus(status_value)
        self.db.commit()
        self.db.refresh(e)
        return e

    def update_progress(self, enrollment_id: uuid.UUID, status_value: str) -> Enrollment:
        e = self._get(enrollment_id)
        e.status = EnrollmentStatus(status_value)
        if e.status == EnrollmentStatus.COMPLETED and not e.completed_at:
            e.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(e)
        return e

    def mark_complete(self, enrollment_id: uuid.UUID) -> Enrollment:
        e = self._get(enrollment_id)
        e.status = EnrollmentStatus.COMPLETED
        e.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(e)
        return e

    def delete(self, enrollment_id: uuid.UUID) -> None:
        e = self._get(enrollment_id)
        self.db.delete(e)
        self.db.commit()
