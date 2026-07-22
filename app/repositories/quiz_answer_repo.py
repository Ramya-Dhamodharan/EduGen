<<<<<<< HEAD
import uuid

from sqlalchemy.orm import Session

from app.models.quiz_answer import QuizAnswer


class QuizAnswerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, answer_id: uuid.UUID) -> QuizAnswer | None:
        return (
            self.db.query(QuizAnswer)
            .filter(QuizAnswer.id == answer_id)
            .first()
        )

    def get_all(self) -> list[QuizAnswer]:
        return self.db.query(QuizAnswer).all()

    def create(self, answer: QuizAnswer) -> QuizAnswer:
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def update(self, answer: QuizAnswer) -> QuizAnswer:
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def delete(self, answer: QuizAnswer) -> None:
        self.db.delete(answer)
        self.db.commit()
=======
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.quiz_answer import QuizAnswer
from app.schemas.quiz_answer_schemas import (
    QuizAnswerCreate,
    QuizAnswerUpdate
)

def get_all_answers(db: Session):
    return db.query(QuizAnswer).all()


def get_answer_by_id(
    db: Session,
    answer_id: UUID
):
    return (
        db.query(QuizAnswer)
        .filter(QuizAnswer.id == answer_id)
        .first()
    )


def get_answers_by_attempt(
    db: Session,
    attempt_id: UUID
):
    return (
        db.query(QuizAnswer)
        .filter(QuizAnswer.attempt_id == attempt_id)
        .all()
    )


def create_answer(
    db: Session,
    answer: QuizAnswerCreate,
    is_correct: bool,
    marks_obtained: float
):
    db_answer = QuizAnswer(
        attempt_id=answer.attempt_id,
        question_id=answer.question_id,
        selected_option=answer.selected_option,
        is_correct=is_correct,
        marks_obtained=marks_obtained
    )

    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)

    return db_answer


def update_answer(
    db: Session,
    db_answer: QuizAnswer,
    answer: QuizAnswerUpdate,
    is_correct: bool,
    marks_obtained: float
):
    db_answer.selected_option = answer.selected_option
    db_answer.is_correct = is_correct
    db_answer.marks_obtained = marks_obtained

    db.commit()
    db.refresh(db_answer)

    return db_answer


def delete_answer(
    db: Session,
    db_answer: QuizAnswer
):
    db.delete(db_answer)
    db.commit()
>>>>>>> origin/dev
