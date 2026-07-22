import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.repositories.quiz_question_repo import QuizQuestionRepository
from app.schemas.quiz_question_schemas import (
    QuizQuestionCreate,
    QuizQuestionUpdate,
)


class QuizQuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.question_repo = QuizQuestionRepository(db)

    def _get(self, question_id: uuid.UUID) -> QuizQuestion:
        question = self.question_repo.get_by_id(question_id)

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found",
            )

        return question

    def _validate_quiz(self, quiz_id: uuid.UUID) -> None:
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

    def list_all(self) -> List[QuizQuestion]:
        return self.question_repo.get_all()

    def get(self, question_id: uuid.UUID) -> QuizQuestion:
        return self._get(question_id)

    def create(
        self,
        data: QuizQuestionCreate,
        created_by: uuid.UUID,
    ) -> QuizQuestion:

        self._validate_quiz(data.quiz_id)

        question = QuizQuestion(
            **data.model_dump(),
            created_by=created_by,
        )

        return self.question_repo.create(question)

    def create_under_quiz(
        self,
        quiz_id: uuid.UUID,
        data,
        created_by: uuid.UUID,
    ) -> QuizQuestion:

        self._validate_quiz(quiz_id)

        question = QuizQuestion(
            quiz_id=quiz_id,
            **data.model_dump(),
            created_by=created_by,
        )

        return self.question_repo.create(question)

    def update(
        self,
        question_id: uuid.UUID,
        data: QuizQuestionUpdate,
    ) -> QuizQuestion:

        question = self._get(question_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(question, field, value)

        return self.question_repo.update(question)

    def delete(self, question_id: uuid.UUID) -> None:
        question = self._get(question_id)
        self.question_repo.delete(question)