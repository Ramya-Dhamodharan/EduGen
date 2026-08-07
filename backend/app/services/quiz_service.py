import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.module import Module
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.repositories.quiz_repo import QuizRepository
from app.schemas.quiz_schemas import QuizCreate, QuizUpdate
from app.utils.exceptions import BadRequestError, NotFoundError


class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.quiz_repo = QuizRepository(db)

    async def _get(self, quiz_id: uuid.UUID) -> Quiz:
        quiz = await self.quiz_repo.get_by_id(quiz_id)

        if quiz is None:
            raise NotFoundError("Quiz not found")

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

    async def _validate_course(self, course_id: uuid.UUID) -> Course:
        result = await self.db.execute(select(Course).where(Course.id == course_id))

        course = result.scalar_one_or_none()

        if course is None:
            raise NotFoundError("Course not found")

        return course

    async def _validate_lesson(
        self,
        lesson_id: uuid.UUID,
        course_id: uuid.UUID,
    ) -> Lesson:
        result = await self.db.execute(
            select(Lesson)
            .join(Module, Lesson.module_id == Module.id)
            .where(
                Lesson.id == lesson_id,
                Module.course_id == course_id,
            )
        )

        lesson = result.scalar_one_or_none()

        if lesson is None:
            raise BadRequestError("Lesson does not belong to the specified course.")

        return lesson

    async def create(
        self,
        data: QuizCreate,
        created_by: uuid.UUID,
    ) -> Quiz:

        await self._validate_course(data.course_id)
        await self._validate_lesson(
            data.lesson_id,
            data.course_id,
        )

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
        data: QuizCreate,
        created_by: uuid.UUID,
    ) -> Quiz:

        await self._validate_course(course_id)
        await self._validate_lesson(
            data.lesson_id,
            course_id,
        )

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

        update_data = data.model_dump(exclude_unset=True)

        course_id = update_data.get("course_id", quiz.course_id)
        lesson_id = update_data.get("lesson_id", quiz.lesson_id)

        if "course_id" in update_data:
            await self._validate_course(course_id)

        if "course_id" in update_data or "lesson_id" in update_data:
            await self._validate_lesson(
                lesson_id,
                course_id,
            )

        for field, value in update_data.items():
            setattr(quiz, field, value)

        return await self.quiz_repo.update(quiz)

    async def delete(
        self,
        quiz_id: uuid.UUID,
    ) -> None:

        quiz = await self._get(quiz_id)
        await self.quiz_repo.delete(quiz)
