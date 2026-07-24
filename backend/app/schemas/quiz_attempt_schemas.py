from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class QuizAttemptCreate(BaseModel):
    quiz_id: UUID
    # student_id comes from the authenticated user.


class QuizAttemptUpdate(BaseModel):
    status: Optional[str] = None


class QuizAttemptOut(BaseModel):
    id: UUID
    quiz_id: UUID
    student_id: UUID
    score: Optional[Decimal] = None
    status: str
    submission_status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    feedback: Optional[str] = None
    feedback_by: Optional[UUID] = None
    feedback_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuizAttemptFeedback(BaseModel):
    """Body for PATCH /quiz-attempts/{attempt_id}/feedback - instructor feedback."""
    feedback: str = Field(..., min_length=1)
