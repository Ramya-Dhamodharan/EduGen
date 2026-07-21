from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.quiz_answer import (
    QuizAnswerCreate,
    QuizAnswerUpdate,
    QuizAnswerResponse
)
from app.services import quiz_answer_service
router = APIRouter(
    prefix="/api",
    tags=["Quiz Answers"]
)


@router.get(
    "/quiz-answers",
    response_model=list[QuizAnswerResponse],
    status_code=status.HTTP_200_OK
)
def get_all_quiz_answers(
    db: Session = Depends(get_db)
):
    return quiz_answer_service.get_all_answers(db)


@router.get(
    "/quiz-answers/{answer_id}",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_200_OK
)
def get_quiz_answer(
    answer_id: UUID,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.get_answer_by_id(
        db,
        answer_id
    )


@router.post(
    "/quiz-answers",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_quiz_answer(
    answer: QuizAnswerCreate,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.create_answer(
        db,
        answer
    )


@router.put(
    "/quiz-answers/{answer_id}",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_200_OK
)
def update_quiz_answer(
    answer_id: UUID,
    answer: QuizAnswerUpdate,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.update_answer(
        db,
        answer_id,
        answer
    )


@router.delete(
    "/quiz-answers/{answer_id}",
    status_code=status.HTTP_200_OK
)
def delete_quiz_answer(
    answer_id: UUID,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.delete_answer(
        db,
        answer_id
    )


@router.get(
    "/quiz-attempts/{attempt_id}/answers",
    response_model=list[QuizAnswerResponse],
    status_code=status.HTTP_200_OK
)
def get_answers_by_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db)
):
    return quiz_answer_service.get_answers_by_attempt(
        db,
        attempt_id
    )


@router.post(
    "/quiz-attempts/{attempt_id}/answers",
    response_model=QuizAnswerResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_answer_under_attempt(
    attempt_id: UUID,
    answer: QuizAnswerCreate,
    db: Session = Depends(get_db)
):
    answer.attempt_id = attempt_id

    return quiz_answer_service.create_answer(
        db,
        answer
    )