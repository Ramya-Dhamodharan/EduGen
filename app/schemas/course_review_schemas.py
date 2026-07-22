from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class CourseReviewCreate(BaseModel):
    course_id: UUID
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None
    # student_id comes from the authenticated user.


class CourseReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    review: Optional[str] = None


class CourseReviewOut(BaseModel):
    id: UUID
    course_id: UUID
    student_id: UUID
    rating: int
    review: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
