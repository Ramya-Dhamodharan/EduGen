import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.repositories.quiz_repo import QuizRepository
from app.schemas.quiz_schemas import QuizCreate, QuizUpdate


class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.quiz_repo = QuizRepository(db)

    async def _get(self, quiz_id: uuid.UUID) -> Quiz:
        quiz = await self.quiz_repo.get_by_id(quiz_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz {quiz_id} not found",
            )

        return quiz

    async def list_all(self) -> List[Quiz]:
        return await self.quiz_repo.get_all()

    async def get(self, quiz_id: uuid.UUID) -> Quiz:
        return await self._get(quiz_id)

    async def list_questions(
        self,
        quiz_id: uuid.UUID,
    ) -> List[QuizQuestion]:

        await self._get(quiz_id)
        return await self.quiz_repo.get_questions(quiz_id)

    async def _validate_course(
        self,
        course_id: uuid.UUID,
    ) -> None:

        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {course_id} does not exist",
            )

    async def create(
        self,
        data: QuizCreate,
        created_by: uuid.UUID,
    ) -> Quiz:

        await self._validate_course(data.course_id)

        quiz = Quiz(
            title=data.title,
            description=data.description,
            course_id=data.course_id,
            lesson_id=data.lesson_id,
            total_marks=data.total_marks,
            pass_marks=data.pass_marks,
            duration=data.duration,
            duration_days=data.duration_days,
            is_active=True,
            created_by=created_by,
        )

        return await self.quiz_repo.create(quiz)

    async def create_under_course(
        self,
        course_id: uuid.UUID,
        data,
        created_by: uuid.UUID,
    ) -> Quiz:

        await self._validate_course(course_id)

        quiz = Quiz(
            title=data.title,
            description=data.description,
            course_id=course_id,
            lesson_id=data.lesson_id,
            total_marks=data.total_marks,
            pass_marks=data.pass_marks,
            duration=data.duration,
            duration_days=data.duration_days,
            is_active=True,
            created_by=created_by,
        )

        return await self.quiz_repo.create(quiz)

    async def update(
        self,
        quiz_id: uuid.UUID,
        data: QuizUpdate,
    ) -> Quiz:

        quiz = await self._get(quiz_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(quiz, field, value)

        return await self.quiz_repo.update(quiz)

    async def delete(
        self,
        quiz_id: uuid.UUID,
    ) -> None:

        quiz = await self._get(quiz_id)
        await self.quiz_repo.delete(quiz)