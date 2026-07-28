import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff
from app.schemas.quiz_attempt_schemas import (
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptOut,
    QuizAttemptFeedback,
)
from app.schemas.quiz_answer_schemas import (
    QuizAnswerOut,
    QuizAnswerNestedCreate,
)
from app.services.quiz_attempt_service import QuizAttemptService

router = APIRouter()


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _ensure_owner_or_staff(user: User, owner_id: uuid.UUID) -> None:
    if _is_staff(user) or user.id == owner_id:
        return
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You do not have permission to access this resource",
    )


# ---- Staff: list all attempts ----
@router.get(
    "",
    response_model=List[QuizAttemptOut],
    dependencies=[Depends(require_staff)],
)
async def list_attempts(
    db: AsyncSession = Depends(get_db),
):
    return await QuizAttemptService(db).list_all()


# ---- Student: look up their own in-progress attempt(s) ----
@router.get("/in-progress", response_model=List[QuizAttemptOut])
async def list_in_progress_attempts(
    quiz_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await QuizAttemptService(db).list_in_progress_for_student(
        current_user.id,
        quiz_id,
    )


# ---- Owner or staff: view one ----
@router.get("/{attempt_id}", response_model=QuizAttemptOut)
async def get_attempt(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = await QuizAttemptService(db).get(attempt_id)

    _ensure_owner_or_staff(
        current_user,
        attempt.student_id,
    )

    return attempt


# ---- Student starts/resumes an attempt ----
@router.post(
    "",
    response_model=QuizAttemptOut,
    status_code=status.HTTP_201_CREATED,
)
async def start_attempt(
    payload: QuizAttemptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await QuizAttemptService(db).start(
        current_user.id,
        payload.quiz_id,
    )


# ---- Owner or staff: update ----

@router.put("/{attempt_id}", response_model=QuizAttemptOut)
async def update_attempt(
    attempt_id: uuid.UUID,
    payload: QuizAttemptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = await QuizAttemptService(db).get(attempt_id)

    _ensure_owner_or_staff(
        current_user,
        attempt.student_id,
    )

    return await QuizAttemptService(db).update(
        attempt_id,
        payload.status,
    )


# ---- Owner or staff: submit & score ----

@router.patch("/{attempt_id}/submit", response_model=QuizAttemptOut)
async def submit_attempt(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = await QuizAttemptService(db).get(attempt_id)

    _ensure_owner_or_staff(
        current_user,
        attempt.student_id,
    )

    return await QuizAttemptService(db).submit(attempt_id)


# ---- Staff: instructor feedback ----
@router.patch(
    "/{attempt_id}/feedback",
    response_model=QuizAttemptOut,
    dependencies=[Depends(require_staff)],
)
async def give_attempt_feedback(
    attempt_id: uuid.UUID,
    payload: QuizAttemptFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await QuizAttemptService(db).add_feedback(
        attempt_id,
        payload.feedback,
        current_user.id,
    )


# ---- Owner or staff: list answers ----
@router.get(
    "/{attempt_id}/answers",
    response_model=List[QuizAnswerOut],
)
async def list_attempt_answers(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = await QuizAttemptService(db).get(attempt_id)

    _ensure_owner_or_staff(
        current_user,
        attempt.student_id,
    )

    return await QuizAttemptService(db).list_answers(attempt_id)


# ---- Nested: submit answer ----
@router.post(
    "/{attempt_id}/answers",
    response_model=QuizAnswerOut,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer_under_attempt(
    attempt_id: uuid.UUID,
    payload: QuizAnswerNestedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.quiz_answer_service import QuizAnswerService

    attempt = await QuizAttemptService(db).get(attempt_id)

    _ensure_owner_or_staff(
        current_user,
        attempt.student_id,
    )

    return await QuizAnswerService(db).submit(
        attempt_id,
        payload.question_id,
        payload.selected_option,
        current_user.id,
    )