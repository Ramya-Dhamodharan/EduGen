import uuid
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz_answer import QuizAnswer
from app.models.quiz_question import QuizQuestion
from app.models.quiz_attempt import QuizAttempt


class QuizAnswerService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, answer_id: uuid.UUID) -> QuizAnswer:
        a = self.db.query(QuizAnswer).filter(QuizAnswer.id == answer_id).first()
        if not a:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Answer {answer_id} not found")
        return a

    def list_all(self) -> List[QuizAnswer]:
        return self.db.query(QuizAnswer).all()

    def get(self, answer_id: uuid.UUID) -> QuizAnswer:
        return self._get(answer_id)

    def _grade(self, question_id: uuid.UUID, selected_option: str | None):
        """Compare the selected option to the question's correct option."""
        question = self.db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
        if not question:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Question {question_id} does not exist")
        is_correct = (
            selected_option is not None
            and selected_option.strip().upper() == question.correct_option.strip().upper()
        )
        marks = Decimal(str(question.marks)) if is_correct else Decimal("0")
        return is_correct, marks

    def submit(self, attempt_id: uuid.UUID, question_id: uuid.UUID,
               selected_option: str | None, created_by: uuid.UUID) -> QuizAnswer:
        if not self.db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Attempt {attempt_id} does not exist")

        is_correct, marks = self._grade(question_id, selected_option)
        answer = QuizAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            marks_obtained=marks,
            created_by=created_by,
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def update(self, answer_id: uuid.UUID, selected_option: str | None) -> QuizAnswer:
        answer = self._get(answer_id)
        is_correct, marks = self._grade(answer.question_id, selected_option)
        answer.selected_option = selected_option
        answer.is_correct = is_correct
        answer.marks_obtained = marks
        self.db.commit()
        self.db.refresh(answer)
        return answer
