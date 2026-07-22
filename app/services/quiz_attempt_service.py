import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus
from app.models.quiz_answer import QuizAnswer
from app.models.quiz import Quiz


class QuizAttemptService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        a = self.db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
        if not a:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Attempt {attempt_id} not found")
        return a

    def list_all(self) -> List[QuizAttempt]:
        return self.db.query(QuizAttempt).all()

    def get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        return self._get(attempt_id)

    def list_for_student(self, student_id: uuid.UUID) -> List[QuizAttempt]:
        return self.db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()

    def list_answers(self, attempt_id: uuid.UUID) -> List[QuizAnswer]:
        self._get(attempt_id)
        return self.db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt_id).all()

    def start(self, student_id: uuid.UUID, quiz_id: uuid.UUID) -> QuizAttempt:
        if not self.db.query(Quiz).filter(Quiz.id == quiz_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Quiz {quiz_id} does not exist")
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            status=QuizAttemptStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            created_by=student_id,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def update(self, attempt_id: uuid.UUID, status_value: str | None) -> QuizAttempt:
        a = self._get(attempt_id)
        if status_value:
            a.status = QuizAttemptStatus(status_value)
        self.db.commit()
        self.db.refresh(a)
        return a

    def submit(self, attempt_id: uuid.UUID) -> QuizAttempt:
        """Score the attempt from its answers, mark it completed."""
        a = self._get(attempt_id)
        if a.status == QuizAttemptStatus.COMPLETED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Attempt already submitted")

        answers = self.db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt_id).all()
        total = Decimal("0")
        for ans in answers:
            if ans.marks_obtained is not None:
                total += ans.marks_obtained

        a.score = total
        a.status = QuizAttemptStatus.COMPLETED
        a.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(a)
        return a
