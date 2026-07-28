import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_staff
from app.db.database import get_db
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.schemas.quiz_answer_schemas import (
    QuizAnswerCreate,
    QuizAnswerOut,
    QuizAnswerUpdate,
)
from app.services.quiz_answer_service import QuizAnswerService

router = APIRouter()


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


async def _owner_of_answer(
    db: AsyncSession,
    attempt_id: uuid.UUID,
) -> uuid.UUID | None:
    result = await db.execute(
        select(QuizAttempt).where(QuizAttempt.id == attempt_id)
    )
    attempt = result.scalar_one_or_none()
    return attempt.student_id if attempt else None


# ---- Staff: list all answers ----
@router.get(
    "",
    response_model=List[QuizAnswerOut],
    dependencies=[Depends(require_staff)],
)
async def list_answers(
    db: AsyncSession = Depends(get_db),
):
    return await QuizAnswerService(db).list_all()


# ---- Owner or staff: view one ----
@router.get("/{answer_id}", response_model=QuizAnswerOut)
async def get_answer(
    answer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = await QuizAnswerService(db).get(answer_id)

    owner = await _owner_of_answer(
        db,
        answer.attempt_id,
    )

    if not _is_staff(current_user) and current_user.id != owner:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You do not have permission to access this resource",
        )

    return answer


# ---- Student submits their own answer ----
@router.post(
    "",
    response_model=QuizAnswerOut,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    payload: QuizAnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner = await _owner_of_answer(
        db,
        payload.attempt_id,
    )

    if owner is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Attempt {payload.attempt_id} does not exist",
        )

    if not _is_staff(current_user) and current_user.id != owner:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You can only submit answers for your own attempt",
        )

    return await QuizAnswerService(db).submit(
        payload.attempt_id,
        payload.question_id,
        payload.selected_option,
        current_user.id,
    )


# ---- Owner or staff: update an answer ----
@router.put("/{answer_id}", response_model=QuizAnswerOut)
async def update_answer(
    answer_id: uuid.UUID,
    payload: QuizAnswerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = await QuizAnswerService(db).get(answer_id)

    owner = await _owner_of_answer(
        db,
        answer.attempt_id,
    )

    if not _is_staff(current_user) and current_user.id != owner:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You do not have permission to access this resource",
        )

    return await QuizAnswerService(db).update(
        answer_id,
        payload.selected_option,
    )