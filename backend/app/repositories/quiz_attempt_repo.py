import uuid

from sqlalchemy.orm import Session

from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus
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

    def get_in_progress_for_quiz(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID,
    ) -> QuizAttempt | None:
        """The student's current unfinished attempt at this quiz, if any.

        Used to resume a quiz instead of starting a duplicate attempt.
        """
        return (
            self.db.query(QuizAttempt)
            .filter(
                QuizAttempt.student_id == student_id,
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.status == QuizAttemptStatus.IN_PROGRESS,
            )
            .order_by(QuizAttempt.started_at.desc())
            .first()
        )

    def get_in_progress_for_student(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID | None = None,
    ) -> list[QuizAttempt]:
        """All of a student's unfinished attempts (optionally for one quiz).

        Lets the frontend show a "continue where you left off" list, e.g.
        after logging back in on the same account.
        """
        query = self.db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student_id,
            QuizAttempt.status == QuizAttemptStatus.IN_PROGRESS,
        )

        if quiz_id is not None:
            query = query.filter(QuizAttempt.quiz_id == quiz_id)

        return query.order_by(QuizAttempt.started_at.desc()).all()

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