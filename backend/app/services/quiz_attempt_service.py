import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollment import Enrollment
from app.models.quiz import Quiz
from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import (
    QuizAttempt,
    QuizAttemptStatus,
    SubmissionStatus,
)
from app.repositories.quiz_attempt_repo import QuizAttemptRepository
from app.utils.exceptions import BadRequestError, NotFoundError


class QuizAttemptService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.attempt_repo = QuizAttemptRepository(db)

    async def _get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        attempt = await self.attempt_repo.get_by_id(attempt_id)

        if not attempt:
            raise NotFoundError(f"Attempt {attempt_id} not found")

        return attempt

    async def list_all(self) -> List[QuizAttempt]:
        return await self.attempt_repo.get_all()

    async def get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        return await self._get(attempt_id)

    async def list_for_student(
        self,
        student_id: uuid.UUID,
    ) -> List[QuizAttempt]:
        return await self.attempt_repo.get_by_student_id(student_id)

    async def list_answers(
        self,
        attempt_id: uuid.UUID,
    ) -> List[QuizAnswer]:
        await self._get(attempt_id)
        return await self.attempt_repo.get_answers(attempt_id)

    async def list_in_progress_for_student(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID | None = None,
    ) -> List[QuizAttempt]:
        return await self.attempt_repo.get_in_progress_for_student(
            student_id,
            quiz_id,
        )

    async def start(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID,
    ) -> QuizAttempt:
        """Start a quiz, or transparently resume an unfinished one."""

        result = await self.db.execute(select(Quiz).where(Quiz.id == quiz_id))
        quiz = result.scalar_one_or_none()

        if not quiz:
            raise BadRequestError(f"Quiz {quiz_id} does not exist")

        existing = await self.attempt_repo.get_in_progress_for_quiz(
            student_id,
            quiz_id,
        )

        if existing:
            return existing

        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            status=QuizAttemptStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            created_by=student_id,
        )

        return await self.attempt_repo.create(attempt)

    async def update(
        self,
        attempt_id: uuid.UUID,
        status_value: str | None,
    ) -> QuizAttempt:

        attempt = await self._get(attempt_id)

        if status_value:
            attempt.status = QuizAttemptStatus(status_value)

        return await self.attempt_repo.update(attempt)

    async def _resolve_deadline(
        self,
        quiz: Quiz,
        student_id: uuid.UUID,
    ) -> datetime | None:
        """The submission deadline for this student on this quiz, if any."""

        if not quiz.duration_days:
            return None

        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == quiz.course_id,
            )
        )
        enrollment = result.scalar_one_or_none()

        if not enrollment:
            return None

        return enrollment.enrolled_at + timedelta(days=quiz.duration_days)

    async def submit(
        self,
        attempt_id: uuid.UUID,
    ) -> QuizAttempt:

        attempt = await self._get(attempt_id)

        if attempt.status == QuizAttemptStatus.COMPLETED:
            raise BadRequestError("Attempt already submitted")

        answers = await self.attempt_repo.get_answers(attempt_id)

        total = Decimal("0")

        for answer in answers:
            if answer.marks_obtained is not None:
                total += answer.marks_obtained

        result = await self.db.execute(select(Quiz).where(Quiz.id == attempt.quiz_id))
        quiz = result.scalar_one_or_none()

        completed_at = datetime.now(timezone.utc)

        attempt.score = total
        attempt.status = QuizAttemptStatus.COMPLETED
        attempt.completed_at = completed_at

        if quiz is not None:
            deadline = await self._resolve_deadline(
                quiz,
                attempt.student_id,
            )

            if deadline is not None:
                attempt.submission_status = (
                    SubmissionStatus.ON_TIME
                    if completed_at <= deadline
                    else SubmissionStatus.DELAYED
                )

        return await self.attempt_repo.update(attempt)

    async def add_feedback(
        self,
        attempt_id: uuid.UUID,
        feedback: str,
        instructor_id: uuid.UUID,
    ) -> QuizAttempt:

        attempt = await self._get(attempt_id)

        if attempt.status != QuizAttemptStatus.COMPLETED:
            raise BadRequestError("Feedback can only be given on a submitted attempt")

        attempt.feedback = feedback
        attempt.feedback_by = instructor_id
        attempt.feedback_at = datetime.now(timezone.utc)

        return await self.attempt_repo.update(attempt)
