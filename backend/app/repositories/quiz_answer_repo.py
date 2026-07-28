import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.quiz_answer import QuizAnswer


class QuizAnswerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        answer_id: uuid.UUID,
    ) -> QuizAnswer | None:
        result = await self.db.execute(
            select(QuizAnswer)
            .options(
                joinedload(QuizAnswer.attempt)
            )
            .where(
                QuizAnswer.id == answer_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[QuizAnswer]:
        result = await self.db.execute(
            select(QuizAnswer).options(
                joinedload(QuizAnswer.attempt),
                joinedload(QuizAnswer.question),
            )
        )
        return result.scalars().all()

    async def create(
        self,
        answer: QuizAnswer,
    ) -> QuizAnswer:
        self.db.add(answer)

        await self.db.commit()
        await self.db.refresh(answer)

        return answer

    async def update(
        self,
        answer: QuizAnswer,
    ) -> QuizAnswer:
        await self.db.commit()
        await self.db.refresh(answer)

        return answer

    async def delete(
        self,
        answer: QuizAnswer,
    ) -> None:
        await self.db.delete(answer)
        await self.db.commit()