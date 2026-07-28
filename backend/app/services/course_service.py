import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.module import Module
from app.models.course_review import CourseReview
from app.models.quiz import Quiz
from app.models.enrollment import Enrollment
from app.repositories.course_repo import CourseRepository
from app.schemas.course_schemas import (
    CourseCreate,
    CourseUpdate,
    CourseStatusUpdate,
)


class CourseService:
    def __init__(self, db: AsyncSession):
        self.repo = CourseRepository(db)

    async def list_courses(self) -> List[Course]:
        return await self.repo.get_all()

    async def get_course(self, course_id: uuid.UUID) -> Course:
        course = await self.repo.get_by_id(course_id)

        if not course:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Course {course_id} not found",
            )

        return course

    async def create_course(
        self,
        data: CourseCreate,
    ) -> Course:
        if not await self.repo.category_exists(data.category_id):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Category {data.category_id} does not exist",
            )

        return await self.repo.create(data)

    async def update_course(
        self,
        course_id: uuid.UUID,
        data: CourseUpdate,
    ) -> Course:
        course = await self.get_course(course_id)

        return await self.repo.update(
            course,
            data,
        )

    async def update_course_status(
        self,
        course_id: uuid.UUID,
        data: CourseStatusUpdate,
    ) -> Course:
        course = await self.get_course(course_id)

        return await self.repo.update_status(
            course,
            data.is_active,
        )

    async def delete_course(
        self,
        course_id: uuid.UUID,
    ) -> None:
        course = await self.get_course(course_id)

        await self.repo.delete(course)

    async def get_modules(
        self,
        course_id: uuid.UUID,
    ) -> List[Module]:
        await self.get_course(course_id)

        return await self.repo.get_modules(course_id)

    async def get_reviews(
        self,
        course_id: uuid.UUID,
    ) -> List[CourseReview]:
        await self.get_course(course_id)

        return await self.repo.get_reviews(course_id)

    async def get_quizzes(
        self,
        course_id: uuid.UUID,
    ) -> List[Quiz]:
        await self.get_course(course_id)

        return await self.repo.get_quizzes(course_id)

    async def get_enrollments(
        self,
        course_id: uuid.UUID,
    ) -> List[Enrollment]:
        await self.get_course(course_id)

        return await self.repo.get_enrollments(course_id)

    async def search_courses(
        self,
        query: Optional[str] = None,
        category: Optional[uuid.UUID] = None,
        level: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Course]:
        return await self.repo.search(
            query,
            category,
            level,
            language,
        )