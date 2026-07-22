<<<<<<< HEAD
import uuid
=======
from uuid import UUID
>>>>>>> origin/dev

from sqlalchemy.orm import Session

from app.models.course_review import CourseReview
<<<<<<< HEAD


class CourseReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: uuid.UUID) -> CourseReview | None:
        return (
            self.db.query(CourseReview)
            .filter(CourseReview.id == review_id)
            .first()
        )

    def get_all(self) -> list[CourseReview]:
        return self.db.query(CourseReview).all()

    def get_by_course_id(self, course_id: uuid.UUID) -> list[CourseReview]:
        return (
            self.db.query(CourseReview)
            .filter(CourseReview.course_id == course_id)
            .all()
        )

    def get_by_course_and_student(
        self,
        course_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> CourseReview | None:
        return (
            self.db.query(CourseReview)
            .filter(
                CourseReview.course_id == course_id,
                CourseReview.student_id == student_id,
            )
            .first()
        )

    def create(self, review: CourseReview) -> CourseReview:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update(self, review: CourseReview) -> CourseReview:
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review: CourseReview) -> None:
        self.db.delete(review)
        self.db.commit()
=======
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
>>>>>>> origin/dev
