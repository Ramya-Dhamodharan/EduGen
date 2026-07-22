import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz_question import QuizQuestion
from app.models.quiz import Quiz
from app.schemas.quiz_question_schemas import QuizQuestionCreate, QuizQuestionUpdate


class QuizQuestionService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, question_id: uuid.UUID) -> QuizQuestion:
        q = self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
        if not q:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Question {question_id} not found")
        return q

    def _validate_quiz(self, quiz_id: uuid.UUID) -> None:
        if not self.db.query(Quiz).filter(Quiz.id == quiz_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Quiz {quiz_id} does not exist")

    def list_all(self) -> List[QuizQuestion]:
        return self.db.query(QuizQuestion).all()

    def get(self, question_id: uuid.UUID) -> QuizQuestion:
        return self._get(question_id)

    def create(self, data: QuizQuestionCreate, created_by: uuid.UUID) -> QuizQuestion:
        self._validate_quiz(data.quiz_id)
        q = QuizQuestion(**data.model_dump(), created_by=created_by)
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)
        return q

    def create_under_quiz(self, quiz_id: uuid.UUID, data, created_by: uuid.UUID) -> QuizQuestion:
        self._validate_quiz(quiz_id)
        q = QuizQuestion(quiz_id=quiz_id, **data.model_dump(), created_by=created_by)
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)
        return q

    def update(self, question_id: uuid.UUID, data: QuizQuestionUpdate) -> QuizQuestion:
        q = self._get(question_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(q, field, value)
        self.db.commit()
        self.db.refresh(q)
        return q

    def delete(self, question_id: uuid.UUID) -> None:
        q = self._get(question_id)
        self.db.delete(q)
        self.db.commit()
