import uuid

from sqlalchemy.orm import Session

from app.models.course_review import CourseReview


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
