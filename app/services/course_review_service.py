import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course_review import CourseReview
from app.models.course import Course
from app.schemas.course_review_schemas import CourseReviewCreate, CourseReviewUpdate


class CourseReviewService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, review_id: uuid.UUID) -> CourseReview:
        r = self.db.query(CourseReview).filter(CourseReview.id == review_id).first()
        if not r:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Review {review_id} not found")
        return r

    def list_all(self) -> List[CourseReview]:
        return self.db.query(CourseReview).all()

    def get(self, review_id: uuid.UUID) -> CourseReview:
        return self._get(review_id)

    def list_for_course(self, course_id: uuid.UUID) -> List[CourseReview]:
        return self.db.query(CourseReview).filter(CourseReview.course_id == course_id).all()

    def create(self, student_id: uuid.UUID, data: CourseReviewCreate) -> CourseReview:
        if not self.db.query(Course).filter(Course.id == data.course_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Course {data.course_id} does not exist")

        existing = (
            self.db.query(CourseReview)
            .filter(CourseReview.course_id == data.course_id, CourseReview.student_id == student_id)
            .first()
        )
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You have already reviewed this course")

        review = CourseReview(
            course_id=data.course_id,
            student_id=student_id,
            rating=data.rating,
            review=data.review,
            created_by=student_id,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update(self, review_id: uuid.UUID, data: CourseReviewUpdate) -> CourseReview:
        review = self._get(review_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(review, field, value)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete(self, review_id: uuid.UUID) -> None:
        review = self._get(review_id)
        self.db.delete(review)
        self.db.commit()
