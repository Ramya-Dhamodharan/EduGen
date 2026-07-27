from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ==================================================
# START QUIZ ATTEMPT
# ==================================================

class QuizAttemptCreate(BaseModel):

    student_id: UUID

    quiz_id: UUID


# ==================================================
# UPDATE QUIZ ATTEMPT
# ==================================================

class QuizAttemptUpdate(BaseModel):

    score: int | None = Field(
        default=None,
        ge=0,
    )

    status: str | None = None


# ==================================================
# SUBMIT QUIZ ATTEMPT
# ==================================================

class QuizAttemptSubmit(BaseModel):

    score: int = Field(
        ...,
        ge=0,
    )


# ==================================================
# RESPONSE
# ==================================================

class QuizAttemptResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    student_id: UUID

    quiz_id: UUID

    attempt_number: int

    score: int | None

    status: str

    started_at: datetime

    submitted_at: datetime | None

    created_at: datetime

    updated_at: datetime | None