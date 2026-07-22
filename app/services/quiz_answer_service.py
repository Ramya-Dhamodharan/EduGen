<<<<<<< HEAD
from uuid import UUID
=======
import uuid
from decimal import Decimal
from typing import List
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_question import QuizQuestion
<<<<<<< HEAD

from app.repositories import quiz_answer_repo
from app.schemas.quiz_answer_schemas import (
    QuizAnswerCreate,
    QuizAnswerUpdate,
)


def get_all_answers(db: Session):
    return quiz_answer_repo.get_all_answers(db)


def get_answer_by_id(db: Session, answer_id: UUID):
    answer = quiz_answer_repo.get_answer_by_id(db, answer_id)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz answer not found."
        )

    return answer


def get_answers_by_attempt(db: Session, attempt_id: UUID):
    return quiz_answer_repo.get_answers_by_attempt(db, attempt_id)


def create_answer(db: Session, answer: QuizAnswerCreate):

    attempt = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.id == answer.attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=404,
            detail="Quiz attempt not found."
        )

    question = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.id == answer.question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found."
        )

    existing_answer = (
        db.query(QuizAnswer)
        .filter(
            QuizAnswer.attempt_id == answer.attempt_id,
            QuizAnswer.question_id == answer.question_id
        )
        .first()
    )

    if existing_answer:
        raise HTTPException(
            status_code=409,
            detail="Answer already submitted."
        )

    is_correct = (
        answer.selected_option == question.correct_option
    )

    marks_obtained = (
        question.marks if is_correct else 0
    )

    return quiz_answer_repo.create_answer(
        db=db,
        answer=answer,
        is_correct=is_correct,
        marks_obtained=marks_obtained
    )


def update_answer(
    db: Session,
    answer_id: UUID,
    answer: QuizAnswerUpdate
):

    db_answer = quiz_answer_repo.get_answer_by_id(
        db,
        answer_id
    )

    if not db_answer:
        raise HTTPException(
            status_code=404,
            detail="Quiz answer not found."
        )

    question = (
        db.query(QuizQuestion)
        .filter(
            QuizQuestion.id == db_answer.question_id
        )
        .first()
    )

    is_correct = (
        answer.selected_option == question.correct_option
    )

    marks_obtained = (
        question.marks if is_correct else 0
    )

    return quiz_answer_repo.update_answer(
        db=db,
        db_answer=db_answer,
        answer=answer,
        is_correct=is_correct,
        marks_obtained=marks_obtained
    )


def delete_answer(
    db: Session,
    answer_id: UUID
):

    db_answer = quiz_answer_repo.get_answer_by_id(
        db,
        answer_id
    )

    if not db_answer:
        raise HTTPException(
            status_code=404,
            detail="Quiz answer not found."
        )

    quiz_answer_repo.delete_answer(
        db,
        db_answer
    )

    return {
        "message": "Quiz answer deleted successfully."
    }
=======
from app.repositories.quiz_answer_repo import QuizAnswerRepository


class QuizAnswerService:
    def __init__(self, db: Session):
        self.db = db
        self.answer_repo = QuizAnswerRepository(db)

    def _get(self, answer_id: uuid.UUID) -> QuizAnswer:
        answer = self.answer_repo.get_by_id(answer_id)

        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer {answer_id} not found",
            )

        return answer

    def list_all(self) -> List[QuizAnswer]:
        return self.answer_repo.get_all()

    def get(self, answer_id: uuid.UUID) -> QuizAnswer:
        return self._get(answer_id)

    def _grade(
        self,
        question_id: uuid.UUID,
        selected_option: str | None,
    ) -> tuple[bool, Decimal]:

        question = (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.id == question_id)
            .first()
        )

        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {question_id} does not exist",
            )

        is_correct = (
            selected_option is not None
            and selected_option.strip().upper()
            == question.correct_option.strip().upper()
        )

        marks = (
            Decimal(str(question.marks))
            if is_correct
            else Decimal("0")
        )

        return is_correct, marks

    def submit(
        self,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        selected_option: str | None,
        created_by: uuid.UUID,
    ) -> QuizAnswer:

        attempt = (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.id == attempt_id)
            .first()
        )

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Attempt {attempt_id} does not exist",
            )

        is_correct, marks = self._grade(
            question_id,
            selected_option,
        )

        answer = QuizAnswer(
            attempt_id=attempt_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            marks_obtained=marks,
            created_by=created_by,
        )

        return self.answer_repo.create(answer)

    def update(
        self,
        answer_id: uuid.UUID,
        selected_option: str | None,
    ) -> QuizAnswer:

        answer = self._get(answer_id)

        is_correct, marks = self._grade(
            answer.question_id,
            selected_option,
        )

        answer.selected_option = selected_option
        answer.is_correct = is_correct
        answer.marks_obtained = marks

        return self.answer_repo.update(answer)
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
