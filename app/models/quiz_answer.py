from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.quiz_attempt import QuizAttempt
    from app.models.quiz_question import QuizQuestion

class QuizAnswer(Base):
    """
    Stores student answers for each quiz question.
    """

    __tablename__ = "quiz_answers"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_quiz_answers",
        ),

        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_quiz_answers_attempt_question",
        ),

        CheckConstraint(
            "selected_option IN ('A','B','C','D')",
            name="ck_quiz_answers_selected_option",
        ),

        CheckConstraint(
            "marks_obtained >= 0",
            name="ck_quiz_answers_marks_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the quiz answer.",
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "quiz_attempts.id",
            name="fk_quiz_answers_attempt_quiz_attempts",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Quiz attempt associated with this answer.",
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "quiz_questions.id",
            name="fk_quiz_answers_question_quiz_questions",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Question answered by the student.",
    )

    selected_option: Mapped[str | None] = mapped_column(
        CHAR(1),
        nullable=True,
        comment="Option selected by the student (A, B, C or D).",
    )

    is_correct: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        comment="Indicates whether the selected answer is correct.",
    )

    marks_obtained: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Marks awarded for this answer.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_answers_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created this record.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the answer was created.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_answers_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated this record.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the answer was last updated.",
    )

    attempt: Mapped["QuizAttempt"] = relationship(
        "QuizAttempt",
        back_populates="answers",
    )

    question: Mapped["QuizQuestion"] = relationship(
        "QuizQuestion",
        back_populates="answers",
    )

    def __repr__(self) -> str:
        return (
            f"<QuizAnswer(id={self.id}, attempt_id={self.attempt_id})>"
        )