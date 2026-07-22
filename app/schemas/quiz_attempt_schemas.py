from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


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
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
