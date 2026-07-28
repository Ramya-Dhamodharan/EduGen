import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.repositories.quiz_question_repo import QuizQuestionRepository
from app.schemas.quiz_question_schemas import (
    QuizQuestionCreate,
    QuizQuestionUpdate,
)


class QuizQuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.question_repo = QuizQuestionRepository(db)

    async def _get(self, question_id: uuid.UUID) -> QuizQuestion:
        question = await self.question_repo.get_by_id(question_id)

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found",
            )

        return question

    async def _validate_quiz(self, quiz_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )
        quiz = result.scalar_one_or_none()

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quiz {quiz_id} does not exist",
            )

    async def list_all(self) -> List[QuizQuestion]:
        return await self.question_repo.get_all()

    async def get(self, question_id: uuid.UUID) -> QuizQuestion:
        return await self._get(question_id)

    async def create(
        self,
        data: QuizQuestionCreate,
        created_by: uuid.UUID,
    ) -> QuizQuestion:

        await self._validate_quiz(data.quiz_id)

        question = QuizQuestion(
            **data.model_dump(),
            created_by=created_by,
        )

        return await self.question_repo.create(question)

    async def create_under_quiz(
        self,
        quiz_id: uuid.UUID,
        data,
        created_by: uuid.UUID,
    ) -> QuizQuestion:

        await self._validate_quiz(quiz_id)

        question = QuizQuestion(
            quiz_id=quiz_id,
            **data.model_dump(),
            created_by=created_by,
        )

        return await self.question_repo.create(question)

    async def update(
        self,
        question_id: uuid.UUID,
        data: QuizQuestionUpdate,
    ) -> QuizQuestion:

        question = await self._get(question_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(question, field, value)

        return await self.question_repo.update(question)

    async def delete(
        self,
        question_id: uuid.UUID,
    ) -> None:

        question = await self._get(question_id)
        await self.question_repo.delete(question)