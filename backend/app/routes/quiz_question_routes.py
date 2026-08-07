import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import (
    get_current_user,
    require_instructor,
    require_non_admin,
)
from app.schemas.quiz_question_schemas import (
    QuizQuestionCreate,
    QuizQuestionUpdate,
    QuizQuestionOut,
    QuizQuestionWithAnswerOut,
)
from app.services.quiz_question_service import QuizQuestionService

# Reads (without the correct answer) open to Instructor/Student;
# writes are Instructor-only.
router = APIRouter(dependencies=[Depends(require_non_admin)])


@router.get("", status_code=status.HTTP_200_OK, response_model=List[QuizQuestionOut])
async def list_quiz_questions(
    db: AsyncSession = Depends(get_db),
):
    return await QuizQuestionService(db).list_all()


@router.get(
    "/{question_id}", status_code=status.HTTP_200_OK, response_model=QuizQuestionOut
)
async def get_quiz_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await QuizQuestionService(db).get(question_id)


@router.post(
    "",
    response_model=QuizQuestionWithAnswerOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def create_quiz_question(
    payload: QuizQuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await QuizQuestionService(db).create(
        payload,
        current_user.id,
    )


@router.put(
    "/{question_id}",
    status_code=status.HTTP_200_OK,
    response_model=QuizQuestionWithAnswerOut,
    dependencies=[Depends(require_instructor)],
)
async def update_quiz_question(
    question_id: uuid.UUID,
    payload: QuizQuestionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await QuizQuestionService(db).update(
        question_id,
        payload,
    )


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_instructor)],
)
async def delete_quiz_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await QuizQuestionService(db).delete(question_id)
