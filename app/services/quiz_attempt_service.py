import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus
from app.repositories.quiz_attempt_repo import QuizAttemptRepository


class QuizAttemptService:
    def __init__(self, db: Session):
        self.db = db
        self.attempt_repo = QuizAttemptRepository(db)

    def _get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        attempt = self.attempt_repo.get_by_id(attempt_id)

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found",
            )

        return attempt

    def list_all(self) -> List[QuizAttempt]:
        return self.attempt_repo.get_all()

    def get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        return self._get(attempt_id)

    def list_for_student(
        self,
        student_id: uuid.UUID,
    ) -> List[QuizAttempt]:
        return self.attempt_repo.get_by_student_id(student_id)

    def list_answers(
        self,
        attempt_id: uuid.UUID,
    ) -> List[QuizAnswer]:
        self._get(attempt_id)
        return self.attempt_repo.get_answers(attempt_id)

    def start(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID,
    ) -> QuizAttempt:

        quiz = (
            self.db.query(Quiz)
            .filter(Quiz.id == quiz_id)
            .first()
        )

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quiz {quiz_id} does not exist",
            )

        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            status=QuizAttemptStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            created_by=student_id,
        )

        return self.attempt_repo.create(attempt)

    def update(
        self,
        attempt_id: uuid.UUID,
        status_value: str | None,
    ) -> QuizAttempt:

        attempt = self._get(attempt_id)

        if status_value:
            attempt.status = QuizAttemptStatus(status_value)

        return self.attempt_repo.update(attempt)

    def submit(
        self,
        attempt_id: uuid.UUID,
    ) -> QuizAttempt:

        attempt = self._get(attempt_id)

        if attempt.status == QuizAttemptStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attempt already submitted",
            )

        answers = self.attempt_repo.get_answers(attempt_id)

        total = Decimal("0")

        for answer in answers:
            if answer.marks_obtained is not None:
                total += answer.marks_obtained

        attempt.score = total
        attempt.status = QuizAttemptStatus.COMPLETED
        attempt.completed_at = datetime.now(timezone.utc)

        return self.attempt_repo.update(attempt)