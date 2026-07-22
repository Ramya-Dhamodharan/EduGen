from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class QuizCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: UUID
    lesson_id: Optional[UUID] = None
    total_marks: Optional[int] = None
    pass_marks: Optional[int] = None
    duration: Optional[int] = None


class QuizNestedCreate(BaseModel):
    """Body for POST /courses/{courseId}/quizzes - course_id comes from the path."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    lesson_id: Optional[UUID] = None
    total_marks: Optional[int] = None
    pass_marks: Optional[int] = None
    duration: Optional[int] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    total_marks: Optional[int] = None
    pass_marks: Optional[int] = None
    duration: Optional[int] = None
    is_active: Optional[bool] = None


class QuizOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    course_id: UUID
    lesson_id: Optional[UUID] = None
    total_marks: Optional[int] = None
    pass_marks: Optional[int] = None
    duration: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True
