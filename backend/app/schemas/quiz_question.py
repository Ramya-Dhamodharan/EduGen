from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ==================================================
# CREATE QUIZ QUESTION
# ==================================================

class QuizQuestionCreate(BaseModel):

    quiz_id: UUID

    question: str = Field(
        ...,
        min_length=1,
    )

    option_a: str | None = Field(
        default=None,
        max_length=255,
    )

    option_b: str | None = Field(
        default=None,
        max_length=255,
    )

    option_c: str | None = Field(
        default=None,
        max_length=255,
    )

    option_d: str | None = Field(
        default=None,
        max_length=255,
    )

    correct_option: str | None = None

    marks: int | None = Field(
        default=None,
        ge=0,
    )

    @field_validator("correct_option")
    @classmethod
    def validate_correct_option(cls, value):

        if value is not None:

            value = value.upper()

            if value not in ["A", "B", "C", "D"]:

                raise ValueError(
                    "correct_option must be A, B, C or D"
                )

        return value


# ==================================================
# CREATE QUESTION UNDER QUIZ
# ==================================================

class QuizQuestionNestedCreate(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
    )

    option_a: str | None = Field(
        default=None,
        max_length=255,
    )

    option_b: str | None = Field(
        default=None,
        max_length=255,
    )

    option_c: str | None = Field(
        default=None,
        max_length=255,
    )

    option_d: str | None = Field(
        default=None,
        max_length=255,
    )

    correct_option: str | None = None

    marks: int | None = Field(
        default=None,
        ge=0,
    )

    @field_validator("correct_option")
    @classmethod
    def validate_correct_option(cls, value):

        if value is not None:

            value = value.upper()

            if value not in ["A", "B", "C", "D"]:

                raise ValueError(
                    "correct_option must be A, B, C or D"
                )

        return value


# ==================================================
# UPDATE QUIZ QUESTION
# ==================================================

class QuizQuestionUpdate(BaseModel):

    question: str | None = None

    option_a: str | None = None

    option_b: str | None = None

    option_c: str | None = None

    option_d: str | None = None

    correct_option: str | None = None

    marks: int | None = Field(
        default=None,
        ge=0,
    )

    @field_validator("correct_option")
    @classmethod
    def validate_correct_option(cls, value):

        if value is not None:

            value = value.upper()

            if value not in ["A", "B", "C", "D"]:

                raise ValueError(
                    "correct_option must be A, B, C or D"
                )

        return value


# ==================================================
# RESPONSE
# ==================================================

class QuizQuestionResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    quiz_id: UUID

    question: str

    option_a: str | None

    option_b: str | None

    option_c: str | None

    option_d: str | None

    correct_option: str | None

    marks: int | None

    created_by: UUID | None

    created_at: datetime

    updated_by: UUID | None

    updated_at: datetime | None