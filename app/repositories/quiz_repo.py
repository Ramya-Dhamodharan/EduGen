import uuid

from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion


class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, quiz_id: uuid.UUID) -> Quiz | None:
        return (
            self.db.query(Quiz)
            .filter(Quiz.id == quiz_id)
            .first()
        )

    def get_all(self) -> list[Quiz]:
        return self.db.query(Quiz).all()

    def get_questions(self, quiz_id: uuid.UUID) -> list[QuizQuestion]:
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.quiz_id == quiz_id)
            .order_by(QuizQuestion.position)
            .all()
        )

    def create(self, quiz: Quiz) -> Quiz:
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def update(self, quiz: Quiz) -> Quiz:
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete(self, quiz: Quiz) -> None:
        self.db.delete(quiz)
        self.db.commit()
