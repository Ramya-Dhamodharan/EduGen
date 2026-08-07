import uuid
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus
from app.models.quiz_question import QuizQuestion
from app.repositories.quiz_answer_repo import QuizAnswerRepository
from app.utils.exceptions import BadRequestError, NotFoundError


class QuizAnswerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.answer_repo = QuizAnswerRepository(db)

    async def _get(self, answer_id: uuid.UUID) -> QuizAnswer:
        answer = await self.answer_repo.get_by_id(answer_id)

        if not answer:
            raise NotFoundError(f"Answer {answer_id} not found")

        return answer

    async def list_all(self) -> List[QuizAnswer]:
        return await self.answer_repo.get_all()

    async def get(self, answer_id: uuid.UUID) -> QuizAnswer:
        return await self._get(answer_id)

    async def _grade(
        self,
        question_id: uuid.UUID,
        selected_option: str | None,
    ) -> tuple[bool, Decimal]:

        result = await self.db.execute(
            select(QuizQuestion).where(QuizQuestion.id == question_id)
        )
        question = result.scalar_one_or_none()

        if not question:
            raise BadRequestError(f"Question {question_id} does not exist")

        is_correct = (
            selected_option is not None
            and selected_option.strip().upper()
            == question.correct_option.strip().upper()
        )

        marks = Decimal(str(question.marks)) if is_correct else Decimal("0")

        return is_correct, marks

    async def submit(
        self,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        selected_option: str | None,
        created_by: uuid.UUID,
    ) -> QuizAnswer:

        result = await self.db.execute(
            select(QuizAttempt).where(QuizAttempt.id == attempt_id)
        )
        attempt = result.scalar_one_or_none()

        if not attempt:
            raise BadRequestError(f"Attempt {attempt_id} does not exist")

        if attempt.status == QuizAttemptStatus.COMPLETED:
            raise BadRequestError(
                "This quiz has already been submitted and cannot be modified."
            )

        result = await self.db.execute(
            select(QuizAnswer).where(
                QuizAnswer.attempt_id == attempt_id,
                QuizAnswer.question_id == question_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise BadRequestError(
                (
                    "This question has already been answered for this attempt. "
                    "Use PUT /api/quiz-answers/{id} to change the answer."
                )
            )

        is_correct, marks = await self._grade(
            question_id,
            selected_option,
        )

        answer = QuizAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            marks_obtained=marks,
            created_by=created_by,
        )

        return await self.answer_repo.create(answer)

    async def update(
        self,
        answer_id: uuid.UUID,
        selected_option: str | None,
    ) -> QuizAnswer:

        answer = await self._get(answer_id)

        if answer.attempt.status == QuizAttemptStatus.COMPLETED:
            raise BadRequestError(
                "This quiz has already been submitted and cannot be modified."
            )

        is_correct, marks = await self._grade(
            answer.question_id,
            selected_option,
        )

        answer.selected_option = selected_option
        answer.is_correct = is_correct
        answer.marks_obtained = marks

        return await self.answer_repo.update(answer)
