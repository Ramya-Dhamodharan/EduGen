import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course_review import CourseReview


class CourseReviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        review_id: uuid.UUID,
    ) -> CourseReview | None:
        result = await self.db.execute(
            select(CourseReview).where(
                CourseReview.id == review_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[CourseReview]:
        result = await self.db.execute(
            select(CourseReview)
        )
        return result.scalars().all()

    async def get_by_course_id(
        self,
        course_id: uuid.UUID,
    ) -> list[CourseReview]:
        result = await self.db.execute(
            select(CourseReview).where(
                CourseReview.course_id == course_id
            )
        )
        return result.scalars().all()

    async def get_by_course_and_student(
        self,
        course_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> CourseReview | None:
        result = await self.db.execute(
            select(CourseReview).where(
                CourseReview.course_id == course_id,
                CourseReview.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        review: CourseReview,
    ) -> CourseReview:
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def update(
        self,
        review: CourseReview,
    ) -> CourseReview:
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def delete(
        self,
        review: CourseReview,
    ) -> None:
        await self.db.delete(review)
        await self.db.commit()