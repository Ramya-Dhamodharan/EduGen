from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# Create Quiz
# ==========================================

class QuizCreate(BaseModel):

    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    description: str | None = None

    course_id: int

    lessons_id: int | None = None

    total_marks: int | None = Field(
        default=None,
        ge=0
    )

    pass_marks: int | None = Field(
        default=None,
        ge=0
    )

    duration: int | None = Field(
        default=None,
        gt=0
    )

    is_active: bool = True


# ==========================================
# Update Quiz
# ==========================================

class QuizUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    description: str | None = None

    course_id: int | None = None

    lessons_id: int | None = None

    total_marks: int | None = Field(
        default=None,
        ge=0
    )

    pass_marks: int | None = Field(
        default=None,
        ge=0
    )

    duration: int | None = Field(
        default=None,
        gt=0
    )

    is_active: bool | None = None


# ==========================================
# Quiz Response
# ==========================================

class QuizResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    title: str

    description: str | None

    course_id: int

    lessons_id: int | None

    total_marks: int | None

    pass_marks: int | None

    duration: int | None

    is_active: bool

    created_by: UUID | None

    created_at: datetime

    updated_by: UUID | None

    updated_at: datetime | None