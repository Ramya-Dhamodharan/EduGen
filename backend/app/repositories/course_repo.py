import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.course import Course
from app.models.course_review import CourseReview
from app.models.enrollment import Enrollment
from app.models.module import Module
from app.models.quiz import Quiz
from app.schemas.course_schemas import CourseCreate, CourseUpdate


class CourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Course]:
        result = await self.db.execute(select(Course))
        return result.scalars().all()

    async def get_by_id(self, course_id: uuid.UUID) -> Optional[Course]:
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def category_exists(self, category_id: uuid.UUID) -> bool:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, data: CourseCreate) -> Course:
        course = Course(**data.model_dump())

        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def update(self,course: Course,data: CourseUpdate,) -> Course:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(course, field, value)

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def update_status(self,course: Course,is_active: bool,) -> Course:
        course.is_active = is_active

        await self.db.commit()
        await self.db.refresh(course)

        return course

    async def delete(self, course: Course) -> None:
        await self.db.delete(course)
        await self.db.commit()

    async def get_modules(
        self,
        course_id: uuid.UUID,
    ) -> List[Module]:
        result = await self.db.execute(
            select(Module).where(Module.course_id == course_id)
        )
        return result.scalars().all()

    async def get_reviews(
        self,
        course_id: uuid.UUID,
    ) -> List[CourseReview]:
        result = await self.db.execute(
            select(CourseReview).where(
                CourseReview.course_id == course_id
            )
        )
        return result.scalars().all()

    async def get_quizzes(
        self,
        course_id: uuid.UUID,
    ) -> List[Quiz]:
        result = await self.db.execute(
            select(Quiz).where(Quiz.course_id == course_id)
        )
        return result.scalars().all()

    async def get_enrollments(
        self,
        course_id: uuid.UUID,
    ) -> List[Enrollment]:
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.course_id == course_id
            )
        )
        return result.scalars().all()

    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[uuid.UUID] = None,
        level: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Course]:
        stmt = select(Course)

        if query:
            stmt = stmt.where(
                Course.title.ilike(f"%{query}%")
            )

        if category:
            stmt = stmt.where(
                Course.category_id == category
            )

        if level:
            stmt = stmt.where(
                Course.level == level
            )

        if language:
            stmt = stmt.where(
                Course.language == language
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()