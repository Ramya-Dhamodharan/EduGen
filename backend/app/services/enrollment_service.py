import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.repositories.enrollment_repo import EnrollmentRepository


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)

    def _get(self, enrollment_id: uuid.UUID) -> Enrollment:
        enrollment = self.enrollment_repo.get_by_id(enrollment_id)

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrollment {enrollment_id} not found",
            )

        return enrollment

    def list_all(self) -> List[Enrollment]:
        return self.enrollment_repo.get_all()

    def get(self, enrollment_id: uuid.UUID) -> Enrollment:
        return self._get(enrollment_id)

    def list_for_student(self, student_id: uuid.UUID) -> List[Enrollment]:
        return self.enrollment_repo.get_by_student_id(student_id)

    def enroll(
        self,
        student_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> Enrollment:

        course = (
            self.db.query(Course)
            .filter(Course.id == course_id)
            .first()
        )

        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {course_id} does not exist",
            )

        existing = self.enrollment_repo.get_by_student_and_course(
            student_id,
            course_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course",
            )

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
        )

        return self.enrollment_repo.create(enrollment)

    def update(
        self,
        enrollment_id: uuid.UUID,
        status_value: str | None,
    ) -> Enrollment:

        enrollment = self._get(enrollment_id)

        if status_value:
            enrollment.status = EnrollmentStatus(status_value)

        return self.enrollment_repo.update(enrollment)

    def update_progress(
        self,
        enrollment_id: uuid.UUID,
        status_value: str,
    ) -> Enrollment:

        enrollment = self._get(enrollment_id)

        enrollment.status = EnrollmentStatus(status_value)

        if (
            enrollment.status == EnrollmentStatus.COMPLETED
            and not enrollment.completed_at
        ):
            enrollment.completed_at = datetime.now(timezone.utc)

        return self.enrollment_repo.update(enrollment)

    def mark_complete(self, enrollment_id: uuid.UUID) -> Enrollment:
        enrollment = self._get(enrollment_id)

        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completed_at = datetime.now(timezone.utc)

        return self.enrollment_repo.update(enrollment)

    def delete(self, enrollment_id: uuid.UUID) -> None:
        enrollment = self._get(enrollment_id)
        self.enrollment_repo.delete(enrollment)