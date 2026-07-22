import uuid

from sqlalchemy.orm import Session

from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_answer import QuizAnswer


class QuizAttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attempt_id: uuid.UUID) -> QuizAttempt | None:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.id == attempt_id)
            .first()
        )

    def get_all(self) -> list[QuizAttempt]:
        return self.db.query(QuizAttempt).all()

    def get_by_student_id(
        self,
        student_id: uuid.UUID,
    ) -> list[QuizAttempt]:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.student_id == student_id)
            .all()
        )

    def get_answers(
        self,
        attempt_id: uuid.UUID,
    ) -> list[QuizAnswer]:
        return (
            self.db.query(QuizAnswer)
            .filter(QuizAnswer.attempt_id == attempt_id)
            .all()
        )

    def create(self, attempt: QuizAttempt) -> QuizAttempt:
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def update(self, attempt: QuizAttempt) -> QuizAttempt:
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def delete(self, attempt: QuizAttempt) -> None:
        self.db.delete(attempt)
        self.db.commit()