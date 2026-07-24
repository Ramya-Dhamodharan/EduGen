import uuid

from sqlalchemy.orm import Session

from app.models.quiz_question import QuizQuestion


class QuizQuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: uuid.UUID) -> QuizQuestion | None:
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.id == question_id)
            .first()
        )

    def get_all(self) -> list[QuizQuestion]:
        return self.db.query(QuizQuestion).all()

    def create(self, question: QuizQuestion) -> QuizQuestion:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, question: QuizQuestion) -> QuizQuestion:
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question: QuizQuestion) -> None:
        self.db.delete(question)
        self.db.commit()
