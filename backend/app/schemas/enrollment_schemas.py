from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class EnrollmentCreate(BaseModel):
    course_id: UUID
    # student_id is taken from the authenticated user, not the body,
    # so a student can only enroll themselves.


class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None


class EnrollmentProgressUpdate(BaseModel):
    status: str = Field(..., description="ACTIVE or COMPLETED")


class EnrollmentOut(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    status: str
    enrolled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
