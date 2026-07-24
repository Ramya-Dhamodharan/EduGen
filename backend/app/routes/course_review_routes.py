import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_user
from app.schemas.course_review_schemas import (
    CourseReviewCreate,
    CourseReviewUpdate,
    CourseReviewOut,
)
from app.services.course_review_service import CourseReviewService

# Any logged-in user can read reviews; write rules are enforced per-endpoint.
router = APIRouter(dependencies=[Depends(require_user)])


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _ensure_author_or_staff(user: User, author_id: uuid.UUID) -> None:
    if _is_staff(user) or user.id == author_id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only modify your own review")


@router.get("", response_model=List[CourseReviewOut])
def list_reviews(db: Session = Depends(get_db)):
    return CourseReviewService(db).list_all()


@router.get("/{review_id}", response_model=CourseReviewOut)
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db)):
    return CourseReviewService(db).get(review_id)


# ---- Student writes a review (author = current user) ----
@router.post("", response_model=CourseReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: CourseReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CourseReviewService(db).create(current_user.id, payload)


# ---- Author or staff: update ----
@router.put("/{review_id}", response_model=CourseReviewOut)
def update_review(
    review_id: uuid.UUID,
    payload: CourseReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = CourseReviewService(db).get(review_id)
    _ensure_author_or_staff(current_user, review.student_id)
    return CourseReviewService(db).update(review_id, payload)


# ---- Author or staff: delete (staff moderation) ----
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = CourseReviewService(db).get(review_id)
    _ensure_author_or_staff(current_user, review.student_id)
    CourseReviewService(db).delete(review_id)