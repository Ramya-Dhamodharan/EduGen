import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        enrollment_id: uuid.UUID,
    ) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.id == enrollment_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Enrollment]:
        result = await self.db.execute(
            select(Enrollment)
        )
        return result.scalars().all()

    async def get_by_student_id(
        self,
        student_id: uuid.UUID,
    ) -> list[Enrollment]:
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id
            )
        )
        return result.scalars().all()

    async def get_by_student_and_course(
        self,
        student_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        enrollment: Enrollment,
    ) -> Enrollment:
        self.db.add(enrollment)

        await self.db.commit()
        await self.db.refresh(enrollment)

        return enrollment

    async def update(
        self,
        enrollment: Enrollment,
    ) -> Enrollment:
        await self.db.commit()
        await self.db.refresh(enrollment)

        return enrollment

    async def delete(
        self,
        enrollment: Enrollment,
    ) -> None:
        await self.db.delete(enrollment)
        await self.db.commit()