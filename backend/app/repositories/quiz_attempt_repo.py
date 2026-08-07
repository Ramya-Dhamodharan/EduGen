import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus


class QuizAttemptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        attempt_id: uuid.UUID,
    ) -> QuizAttempt | None:
        result = await self.db.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        return result.scalar_one_or_none()

    async def get_in_progress_for_quiz(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID,
    ) -> QuizAttempt | None:
        """The student's current unfinished attempt at this quiz, if any.

        Used to resume a quiz instead of starting a duplicate attempt.
        """
        result = await self.db.execute(
            select(QuizAttempt)
            .where(
                QuizAttempt.student_id == student_id,
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.status == QuizAttemptStatus.IN_PROGRESS,
            )
            .order_by(QuizAttempt.started_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_in_progress_for_student(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID | None = None,
    ) -> list[QuizAttempt]:
        """All of a student's unfinished attempts (optionally for one quiz)."""

        stmt = select(QuizAttempt).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.status == QuizAttemptStatus.IN_PROGRESS,
        )

        if quiz_id is not None:
            stmt = stmt.where(QuizAttempt.quiz_id == quiz_id)

        stmt = stmt.order_by(QuizAttempt.started_at.desc())

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all(self) -> list[QuizAttempt]:
        result = await self.db.execute(select(QuizAttempt))
        return result.scalars().all()

    async def get_by_student_id(
        self,
        student_id: uuid.UUID,
    ) -> list[QuizAttempt]:
        result = await self.db.execute(
            select(QuizAttempt).where(QuizAttempt.student_id == student_id)
        )
        return result.scalars().all()

    async def get_answers(
        self,
        attempt_id: uuid.UUID,
    ) -> list[QuizAnswer]:
        result = await self.db.execute(
            select(QuizAnswer).where(QuizAnswer.attempt_id == attempt_id)
        )
        return result.scalars().all()

    async def create(
        self,
        attempt: QuizAttempt,
    ) -> QuizAttempt:
        self.db.add(attempt)

        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def update(
        self,
        attempt: QuizAttempt,
    ) -> QuizAttempt:
        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def delete(
        self,
        attempt: QuizAttempt,
    ) -> None:
        await self.db.delete(attempt)
        await self.db.commit()
