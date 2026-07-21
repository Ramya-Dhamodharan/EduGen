from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class QuizAnswerCreate(BaseModel):
    attempt_id: UUID
    question_id: UUID
    selected_option: str = Field(
        pattern="^[ABCD]$",
        description="Student selected option"
    )


class QuizAnswerUpdate(BaseModel):
    selected_option: str = Field(
        pattern="^[ABCD]$",
        description="Updated selected option"
    )


class QuizAnswerResponse(BaseModel):
    id: UUID
    attempt_id: UUID
    question_id: UUID
    selected_option: str
    is_correct: bool
    marks_obtained: Decimal

    class Config:
        from_attributes = True