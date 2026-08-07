import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_non_admin, require_student
from app.db.database import get_db
from app.models.user import User
from app.schemas.course_review_schemas import (
    CourseReviewCreate,
    CourseReviewOut,
    CourseReviewUpdate,
)
from app.services.course_review_service import CourseReviewService

# Instructor/Student can read reviews; Admin has no business here.
# Write rules are enforced per-endpoint below.
router = APIRouter(dependencies=[Depends(require_non_admin)])


def _is_instructor(user: User) -> bool:
    return user.role.name.lower() == "instructor"


def _ensure_author_or_instructor(user: User, author_id: uuid.UUID) -> None:
    if _is_instructor(user) or user.id == author_id:
        return
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You can only modify your own review",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=List[CourseReviewOut])
async def list_reviews(
    db: AsyncSession = Depends(get_db),
):
    return await CourseReviewService(db).list_all()


@router.get(
    "/{review_id}", status_code=status.HTTP_200_OK, response_model=CourseReviewOut
)
async def get_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await CourseReviewService(db).get(review_id)


# ---- Student only: writes a review (author = current user) ----
@router.post(
    "",
    response_model=CourseReviewOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_student)],
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


# ---- Author (student) or Instructor: update (moderation) ----
@router.put(
    "/{review_id}", status_code=status.HTTP_200_OK, response_model=CourseReviewOut
)
async def update_review(
    review_id: uuid.UUID,
    payload: CourseReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = await CourseReviewService(db).get(review_id)

    _ensure_author_or_instructor(
        current_user,
        review.student_id,
    )

    return await CourseReviewService(db).update(
        review_id,
        payload,
    )


# ---- Author (student) or Instructor: delete (moderation) ----
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

    _ensure_author_or_instructor(
        current_user,
        review.student_id,
    )

    await CourseReviewService(db).delete(review_id)
