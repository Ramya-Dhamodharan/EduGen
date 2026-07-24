import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.category import Category
from app.models.module import Module
from app.models.course_review import CourseReview
from app.models.quiz import Quiz
from app.models.enrollment import Enrollment
from app.schemas.course_schemas import CourseCreate, CourseUpdate


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Course]:
        return self.db.query(Course).all()

    def get_by_id(self, course_id: uuid.UUID) -> Optional[Course]:
        return self.db.query(Course).filter(Course.id == course_id).first()

    def category_exists(self, category_id: uuid.UUID) -> bool:
        return self.db.query(Category).filter(Category.id == category_id).first() is not None

    def create(self, data: CourseCreate) -> Course:
        course = Course(**data.model_dump())
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Course, data: CourseUpdate) -> Course:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(course, field, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update_status(self, course: Course, is_active: bool) -> Course:
        course.is_active = is_active
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.db.delete(course)
        self.db.commit()

    def get_modules(self, course_id: uuid.UUID) -> List[Module]:
        return self.db.query(Module).filter(Module.course_id == course_id).all()

    def get_reviews(self, course_id: uuid.UUID) -> List[CourseReview]:
        return self.db.query(CourseReview).filter(CourseReview.course_id == course_id).all()

    def get_quizzes(self, course_id: uuid.UUID) -> List[Quiz]:
        return self.db.query(Quiz).filter(Quiz.course_id == course_id).all()

    def get_enrollments(self, course_id: uuid.UUID) -> List[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).all()

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[uuid.UUID] = None,
        level: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Course]:
        q = self.db.query(Course)
        if query:
            q = q.filter(Course.title.ilike(f"%{query}%"))
        if category:
            q = q.filter(Course.category_id == category)
        if level:
            q = q.filter(Course.level == level)
        if language:
            q = q.filter(Course.language == language)
        return q.all()