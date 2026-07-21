from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.user import User
    from app.models.quiz_answer import QuizAnswer

class QuizAttemptStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class QuizAttempt(Base):
    """
    Stores every quiz attempt made by students.
    """

    __tablename__ = "quiz_attempts"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_quiz_attempts",
        ),

        CheckConstraint(
            "score >= 0",
            name="ck_quiz_attempts_score_positive",
        ),

        Index(
            "ix_quiz_attempts_quiz_id",
            "quiz_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the quiz attempt.",
    )

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "quizzes.id",
            name="fk_quiz_attempts_quiz_quizzes",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Quiz attempted by the student.",
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_attempts_student_users",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Student who attempted the quiz.",
    )

    score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Score obtained in the quiz.",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Time when the quiz attempt started.",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when the quiz attempt was completed.",
    )

    status: Mapped[QuizAttemptStatus] = mapped_column(
        Enum(
            QuizAttemptStatus,
            name="quiz_attempt_status_enum",
        ),
        nullable=False,
        comment="Current status of the quiz attempt.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_attempts_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created this attempt record.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Attempt creation timestamp.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_attempts_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated the attempt.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Attempt last update timestamp.",
    )

    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="attempts",
    )

    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
    )

    answers: Mapped[list["QuizAnswer"]] = relationship(
        "QuizAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<QuizAttempt(id={self.id}, student_id={self.student_id})>"
        )