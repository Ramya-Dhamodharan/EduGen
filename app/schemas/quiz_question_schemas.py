from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class QuizQuestionCreate(BaseModel):
    quiz_id: UUID
    position: int
    question: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: str = Field(..., description="e.g. 'A', 'B', 'C', 'D'")
    marks: int = 1


class QuizQuestionNestedCreate(BaseModel):
    """Body for POST /quizzes/{quizId}/questions - quiz_id comes from the path."""
    position: int
    question: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: str
    marks: int = 1


class QuizQuestionUpdate(BaseModel):
    position: Optional[int] = None
    question: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: Optional[str] = None
    marks: Optional[int] = None


class QuizQuestionOut(BaseModel):
    id: UUID
    quiz_id: UUID
    position: int
    question: str
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    marks: int

    class Config:
        from_attributes = True


class QuizQuestionWithAnswerOut(QuizQuestionOut):
    """Includes the correct option - only returned to staff."""
    correct_option: str
