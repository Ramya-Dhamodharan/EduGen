import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.repositories.enrollment_repo import EnrollmentRepository
from app.utils.exceptions import BadRequestError, NotFoundError


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)

    async def _get(self, enrollment_id: uuid.UUID) -> Enrollment:
        enrollment = await self.enrollment_repo.get_by_id(enrollment_id)

        if not enrollment:
            raise NotFoundError(f"Enrollment {enrollment_id} not found")

        return enrollment

    async def list_all(self) -> List[Enrollment]:
        return await self.enrollment_repo.get_all()

    async def get(self, enrollment_id: uuid.UUID) -> Enrollment:
        return await self._get(enrollment_id)

    async def list_for_student(
        self,
        student_id: uuid.UUID,
    ) -> List[Enrollment]:
        return await self.enrollment_repo.get_by_student_id(student_id)

    async def enroll(
        self,
        student_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> Enrollment:

        result = await self.db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()

        if not course:
            raise BadRequestError(f"Course {course_id} does not exist")

        existing = await self.enrollment_repo.get_by_student_and_course(
            student_id,
            course_id,
        )

        if existing:
            raise BadRequestError("Already enrolled in this course")

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE,
            started_at=datetime.now(timezone.utc),
        )

        return await self.enrollment_repo.create(enrollment)

    async def update(
        self,
        enrollment_id: uuid.UUID,
        status_value: str | None,
    ) -> Enrollment:

        enrollment = await self._get(enrollment_id)

        if status_value:
            enrollment.status = EnrollmentStatus(status_value)

        return await self.enrollment_repo.update(enrollment)

    async def update_progress(
        self,
        enrollment_id: uuid.UUID,
        status_value: str,
    ) -> Enrollment:

        enrollment = await self._get(enrollment_id)

        enrollment.status = EnrollmentStatus(status_value)

        if (
            enrollment.status == EnrollmentStatus.COMPLETED
            and not enrollment.completed_at
        ):
            enrollment.completed_at = datetime.now(timezone.utc)

        return await self.enrollment_repo.update(enrollment)

    async def mark_complete(
        self,
        enrollment_id: uuid.UUID,
    ) -> Enrollment:

        enrollment = await self._get(enrollment_id)

        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completed_at = datetime.now(timezone.utc)

        return await self.enrollment_repo.update(enrollment)

    async def delete(
        self,
        enrollment_id: uuid.UUID,
    ) -> None:

        enrollment = await self._get(enrollment_id)
        await self.enrollment_repo.delete(enrollment)
