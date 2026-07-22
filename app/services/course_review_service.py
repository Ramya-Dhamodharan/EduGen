<<<<<<< HEAD
from uuid import UUID
=======
import uuid
from typing import List
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
<<<<<<< HEAD
from app.models.user import User
from app.models.course_review import CourseReview

from app.repositories import course_review_repo
=======
from app.models.course_review import CourseReview
from app.repositories.course_review_repo import CourseReviewRepository
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
from app.schemas.course_review_schemas import (
    CourseReviewCreate,
    CourseReviewUpdate,
)


<<<<<<< HEAD
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
=======
class CourseReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = CourseReviewRepository(db)

    def _get(self, review_id: uuid.UUID) -> CourseReview:
        review = self.review_repo.get_by_id(review_id)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review {review_id} not found",
            )

        return review

    def list_all(self) -> List[CourseReview]:
        return self.review_repo.get_all()

    def get(self, review_id: uuid.UUID) -> CourseReview:
        return self._get(review_id)

    def list_for_course(self, course_id: uuid.UUID) -> List[CourseReview]:
        return self.review_repo.get_by_course_id(course_id)

    def create(
        self,
        student_id: uuid.UUID,
        data: CourseReviewCreate,
    ) -> CourseReview:

        course = (
            self.db.query(Course)
            .filter(Course.id == data.course_id)
            .first()
        )

        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {data.course_id} does not exist",
            )

        existing = self.review_repo.get_by_course_and_student(
            data.course_id,
            student_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this course",
            )

        review = CourseReview(
            course_id=data.course_id,
            student_id=student_id,
            rating=data.rating,
            review=data.review,
            created_by=student_id,
        )

        return self.review_repo.create(review)

    def update(
        self,
        review_id: uuid.UUID,
        data: CourseReviewUpdate,
    ) -> CourseReview:

        review = self._get(review_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(review, field, value)

        return self.review_repo.update(review)

    def delete(self, review_id: uuid.UUID) -> None:
        review = self._get(review_id)
        self.review_repo.delete(review)
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
