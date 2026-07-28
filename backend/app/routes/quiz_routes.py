import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import (
    get_current_user,
    require_staff,
    require_user,
)
from app.schemas.quiz_schemas import (
    QuizCreate,
    QuizUpdate,
    QuizOut,
)
from app.schemas.quiz_question_schemas import (
    QuizQuestionOut,
    QuizQuestionNestedCreate,
)
from app.services.quiz_service import QuizService

# Reads open to any logged-in user; writes are staff-only per-endpoint.
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("", response_model=List[QuizOut])
async def list_quizzes(
    db: AsyncSession = Depends(get_db),
):
    return await QuizService(db).list_all()


@router.get("/{quiz_id}", response_model=QuizOut)
async def get_quiz(
    quiz_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await QuizService(db).get(quiz_id)


@router.get("/{quiz_id}/questions", response_model=List[QuizQuestionOut])
async def list_quiz_questions(
    quiz_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await QuizService(db).list_questions(quiz_id)


@router.post(
    "",
    response_model=QuizOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_staff)],
)
async def create_quiz(
    payload: QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await QuizService(db).create(
        payload,
        current_user.id,
    )


@router.put(
    "/{quiz_id}",
    response_model=QuizOut,
    dependencies=[Depends(require_staff)],
)
async def update_quiz(
    quiz_id: uuid.UUID,
    payload: QuizUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await QuizService(db).update(
        quiz_id,
        payload,
    )


@router.delete(
    "/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_staff)],
)
async def delete_quiz(
    quiz_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await QuizService(db).delete(quiz_id)


# Nested: create a question under a quiz (staff only)
@router.post(
    "/{quiz_id}/questions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_staff)],
)
async def create_question_under_quiz(
    quiz_id: uuid.UUID,
    payload: QuizQuestionNestedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.quiz_question_service import QuizQuestionService

    q = await QuizQuestionService(db).create_under_quiz(
        quiz_id,
        payload,
        current_user.id,
    )

    return {
        "id": str(q.id),
        "quiz_id": str(q.quiz_id),
        "question": q.question,
        "marks": q.marks,
    }