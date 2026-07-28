import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion


class QuizRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        quiz_id: uuid.UUID,
    ) -> Quiz | None:
        result = await self.db.execute(
            select(Quiz).where(
                Quiz.id == quiz_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Quiz]:
        result = await self.db.execute(
            select(Quiz)
        )
        return result.scalars().all()

    async def get_questions(
        self,
        quiz_id: uuid.UUID,
    ) -> list[QuizQuestion]:
        result = await self.db.execute(
            select(QuizQuestion).where(
                QuizQuestion.quiz_id == quiz_id
            )
        )
        return result.scalars().all()

    async def create(
        self,
        quiz: Quiz,
    ) -> Quiz:
        self.db.add(quiz)

        await self.db.commit()
        await self.db.refresh(quiz)

        return quiz

    async def update(
        self,
        quiz: Quiz,
    ) -> Quiz:
        await self.db.commit()
        await self.db.refresh(quiz)

        return quiz

    async def delete(
        self,
        quiz: Quiz,
    ) -> None:
        await self.db.delete(quiz)
        await self.db.commit()