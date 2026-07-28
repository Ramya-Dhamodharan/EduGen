import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz_question import QuizQuestion


class QuizQuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        question_id: uuid.UUID,
    ) -> QuizQuestion | None:
        result = await self.db.execute(
            select(QuizQuestion).where(
                QuizQuestion.id == question_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[QuizQuestion]:
        result = await self.db.execute(
            select(QuizQuestion)
        )
        return result.scalars().all()

    async def create(
        self,
        question: QuizQuestion,
    ) -> QuizQuestion:
        self.db.add(question)

        await self.db.commit()
        await self.db.refresh(question)

        return question

    async def update(
        self,
        question: QuizQuestion,
    ) -> QuizQuestion:
        await self.db.commit()
        await self.db.refresh(question)

        return question

    async def delete(
        self,
        question: QuizQuestion,
    ) -> None:
        await self.db.delete(question)
        await self.db.commit()