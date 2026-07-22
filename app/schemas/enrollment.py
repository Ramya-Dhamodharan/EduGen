from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------
# Create Enrollment
# -----------------------------
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


# -----------------------------
# Update Enrollment
# -----------------------------
class EnrollmentUpdate(BaseModel):
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    progress: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[str] = None


# -----------------------------
# Update Progress
# -----------------------------
class ProgressUpdate(BaseModel):
    progress: Decimal = Field(..., ge=0, le=100)


# -----------------------------
# Update Status
# -----------------------------
class StatusUpdate(BaseModel):
    status: str


# -----------------------------
# Response Schema
# -----------------------------
class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    student_id: int

    course_id: int

    enrolled_at: datetime

    started_at: Optional[datetime]

    completed_at: Optional[datetime]

    progress: Decimal

    status: str

    created_at: datetime

    updated_at: datetime