<<<<<<< HEAD
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.course_review_schemas import (
    CourseReviewCreate,
    CourseReviewUpdate,
    CourseReviewResponse,
)
from app.services import course_review_service


router = APIRouter(
    prefix="/api",
    tags=["Course Reviews"]
)


@router.get(
    "/course-reviews",
    response_model=list[CourseReviewResponse]
)
def get_all_reviews(
    db: Session = Depends(get_db)
):
    return course_review_service.get_all_reviews(db)


@router.get(
    "/course-reviews/{review_id}",
    response_model=CourseReviewResponse
)
def get_review_by_id(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    return course_review_service.get_review_by_id(
        db,
        review_id
    )


@router.post(
    "/course-reviews",
    response_model=CourseReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def create_review(
    review: CourseReviewCreate,
    db: Session = Depends(get_db)
):
    return course_review_service.create_review(
        db,
        review
    )


@router.put(
    "/course-reviews/{review_id}",
    response_model=CourseReviewResponse
)
def update_review(
    review_id: UUID,
    review: CourseReviewUpdate,
    db: Session = Depends(get_db)
):
    return course_review_service.update_review(
        db,
        review_id,
        review
    )


@router.delete(
    "/course-reviews/{review_id}"
)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    return course_review_service.delete_review(
        db,
        review_id
    )


@router.get(
    "/courses/{course_id}/reviews",
    response_model=list[CourseReviewResponse]
)
def get_reviews_by_course(
    course_id: UUID,
    db: Session = Depends(get_db)
):
    return course_review_service.get_reviews_by_course(
        db,
        course_id
    )
=======
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
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
