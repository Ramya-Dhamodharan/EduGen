from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.user import User
from app.models.course_review import CourseReview

from app.repositories import course_review_repo
from app.schemas.course_review import (
    CourseReviewCreate,
    CourseReviewUpdate,
)


def get_all_reviews(db: Session):
    return course_review_repo.get_all_reviews(db)


def get_review_by_id(
    db: Session,
    review_id: UUID
):
    review = course_review_repo.get_review_by_id(
        db,
        review_id
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found."
        )

    return review


def create_review(
    db: Session,
    review: CourseReviewCreate
):
    course = (
        db.query(Course)
        .filter(Course.id == review.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found."
        )

    student = (
        db.query(User)
        .filter(User.id == review.student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return course_review_repo.create_review(
        db,
        review
    )


def update_review(
    db: Session,
    review_id: UUID,
    review: CourseReviewUpdate
):
    db_review = course_review_repo.get_review_by_id(
        db,
        review_id
    )

    if not db_review:
        raise HTTPException(
            status_code=404,
            detail="Review not found."
        )

    return course_review_repo.update_review(
        db,
        db_review,
        review
    )


def delete_review(
    db: Session,
    review_id: UUID
):
    db_review = course_review_repo.get_review_by_id(
        db,
        review_id
    )

    if not db_review:
        raise HTTPException(
            status_code=404,
            detail="Review not found."
        )

    course_review_repo.delete_review(
        db,
        db_review
    )

    return {
        "message": "Review deleted successfully."
    }


def get_reviews_by_course(
    db: Session,
    course_id: UUID
):
    return course_review_repo.get_reviews_by_course(
        db,
        course_id
    )