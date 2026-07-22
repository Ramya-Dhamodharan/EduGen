import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.course import Course
from app.schemas.quiz_schemas import QuizCreate, QuizUpdate


class QuizService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, quiz_id: uuid.UUID) -> Quiz:
        q = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not q:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Quiz {quiz_id} not found")
        return q

    def list_all(self) -> List[Quiz]:
        return self.db.query(Quiz).all()

    def get(self, quiz_id: uuid.UUID) -> Quiz:
        return self._get(quiz_id)

    def list_questions(self, quiz_id: uuid.UUID) -> List[QuizQuestion]:
        self._get(quiz_id)
        return (
            self.db.query(QuizQuestion)
            .filter(QuizQuestion.quiz_id == quiz_id)
            .order_by(QuizQuestion.position)
            .all()
        )

    def _validate_course(self, course_id: uuid.UUID) -> None:
        if not self.db.query(Course).filter(Course.id == course_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Course {course_id} does not exist")

    def create(self, data: QuizCreate, created_by: uuid.UUID) -> Quiz:
        self._validate_course(data.course_id)
        quiz = Quiz(
            title=data.title,
            description=data.description,
            course_id=data.course_id,
            lesson_id=data.lesson_id,
            total_marks=data.total_marks,
            pass_marks=data.pass_marks,
            duration=data.duration,
            is_active=True,
            created_by=created_by,
        )
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def create_under_course(self, course_id: uuid.UUID, data, created_by: uuid.UUID) -> Quiz:
        self._validate_course(course_id)
        quiz = Quiz(
            title=data.title,
            description=data.description,
            course_id=course_id,
            lesson_id=data.lesson_id,
            total_marks=data.total_marks,
            pass_marks=data.pass_marks,
            duration=data.duration,
            is_active=True,
            created_by=created_by,
        )
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def update(self, quiz_id: uuid.UUID, data: QuizUpdate) -> Quiz:
        quiz = self._get(quiz_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(quiz, field, value)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def delete(self, quiz_id: uuid.UUID) -> None:
        quiz = self._get(quiz_id)
        self.db.delete(quiz)
        self.db.commit()
