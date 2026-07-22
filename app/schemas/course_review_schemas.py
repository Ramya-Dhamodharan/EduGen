<<<<<<< HEAD
from datetime import datetime
from uuid import UUID
from typing import Optional
=======
from uuid import UUID
from datetime import datetime
>>>>>>> origin/dev

from pydantic import BaseModel, Field


class CourseReviewCreate(BaseModel):
    course_id: UUID
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/dev
