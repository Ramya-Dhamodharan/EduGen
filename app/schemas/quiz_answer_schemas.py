from decimal import Decimal
from uuid import UUID
from typing import Optional

from pydantic import BaseModel


class QuizAnswerCreate(BaseModel):
    attempt_id: UUID
    question_id: UUID
    selected_option: Optional[str] = None


class QuizAnswerNestedCreate(BaseModel):
    """Body for POST /quiz-attempts/{attemptId}/answers - attempt_id from path."""
    question_id: UUID
    selected_option: Optional[str] = None


class QuizAnswerUpdate(BaseModel):
    selected_option: Optional[str] = None


class QuizAnswerOut(BaseModel):
    id: UUID
    attempt_id: UUID
    question_id: UUID
    selected_option: Optional[str] = None
    is_correct: Optional[bool] = None
    marks_obtained: Optional[Decimal] = None

    class Config:
        from_attributes = True
