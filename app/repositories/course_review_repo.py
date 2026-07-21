from uuid import UUID

from sqlalchemy.orm import Session

from app.models.course_review import CourseReview
from app.schemas.course_review_schemas import (
    CourseReviewCreate,
    CourseReviewUpdate,
)


def get_all_reviews(db: Session):
    return db.query(CourseReview).all()


def get_review_by_id(db: Session, review_id: UUID):
    return (
        db.query(CourseReview)
        .filter(CourseReview.id == review_id)
        .first()
    )


def create_review(
    db: Session,
    review: CourseReviewCreate
):
    db_review = CourseReview(
        **review.model_dump()
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return db_review


def update_review(
    db: Session,
    db_review: CourseReview,
    review: CourseReviewUpdate
):
    update_data = review.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(db_review, key, value)

    db.commit()
    db.refresh(db_review)

    return db_review


def delete_review(
    db: Session,
    db_review: CourseReview
):
    db.delete(db_review)
    db.commit()


def get_reviews_by_course(
    db: Session,
    course_id: UUID
):
    return (
        db.query(CourseReview)
        .filter(CourseReview.course_id == course_id)
        .all()
    )