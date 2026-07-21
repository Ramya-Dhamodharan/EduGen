from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import QuizAttempt
from app.models.quiz_question import QuizQuestion

from app.repositories import quiz_answer_repo
from app.schemas.quiz_answer import (
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