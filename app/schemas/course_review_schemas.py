from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class CourseReviewCreate(BaseModel):
    course_id: UUID
    student_id: UUID
    rating: int = Field(ge=1, le=5)
    review: str | None = None


class CourseReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    review: str | None = None


class CourseReviewResponse(BaseModel):
    id: UUID
    course_id: UUID
    student_id: UUID
    rating: int | None
    review: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True