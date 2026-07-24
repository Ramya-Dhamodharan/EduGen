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