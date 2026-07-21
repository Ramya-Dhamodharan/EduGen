from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.course_review import (
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