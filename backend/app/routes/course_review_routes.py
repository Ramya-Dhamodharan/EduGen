import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.course_review_schemas import (
    CourseReviewCreate,
    CourseReviewOut,
    CourseReviewUpdate,
)
from app.services.course_review_service import CourseReviewService

# Any logged-in user can read reviews; write rules are enforced per-endpoint.
router = APIRouter(dependencies=[Depends(require_user)])


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _ensure_author_or_staff(user: User, author_id: uuid.UUID) -> None:
    if _is_staff(user) or user.id == author_id:
        return
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You can only modify your own review",
    )


@router.get("", response_model=List[CourseReviewOut])
async def list_reviews(
    db: AsyncSession = Depends(get_db),
):
    return await CourseReviewService(db).list_all()


@router.get("/{review_id}", response_model=CourseReviewOut)
async def get_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await CourseReviewService(db).get(review_id)


# ---- Student writes a review (author = current user) ----
@router.post(
    "",
    response_model=CourseReviewOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    payload: CourseReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await CourseReviewService(db).create(
        current_user.id,
        payload,
    )


# ---- Author or staff: update ----
@router.put("/{review_id}", response_model=CourseReviewOut)
async def update_review(
    review_id: uuid.UUID,
    payload: CourseReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await CourseReviewService(db).get(review_id)

    _ensure_author_or_staff(
        current_user,
        review.student_id,
    )

    return await CourseReviewService(db).update(
        review_id,
        payload,
    )


# ---- Author or staff: delete (staff moderation) ----
@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await CourseReviewService(db).get(review_id)

    _ensure_author_or_staff(
        current_user,
        review.student_id,
    )

    await CourseReviewService(db).delete(review_id)