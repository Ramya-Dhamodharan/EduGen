from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.quiz_answer import QuizAnswer

class QuizQuestion(Base):
    """
    Stores questions belonging to a quiz.
    """

    __tablename__ = "quiz_questions"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_quiz_questions",
        ),

        

        CheckConstraint(
            "marks > 0",
            name="ck_quiz_questions_marks_positive",
        ),

       

        CheckConstraint(
            "correct_option IN ('A','B','C','D')",
            name="ck_quiz_questions_correct_option",
        ),

        Index(
            "ix_quiz_questions_quiz_id",
            "quiz_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the quiz question.",
    )

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "quizzes.id",
            name="fk_quiz_questions_quiz_quizzes",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Quiz to which this question belongs.",
    )

   

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Question text.",
    )

    option_a: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Option A.",
    )

    option_b: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Option B.",
    )

    option_c: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Option C.",
    )

    option_d: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Option D.",
    )

    correct_option: Mapped[str] = mapped_column(
        CHAR(1),
        nullable=False,
        comment="Correct option (A, B, C or D).",
    )

    marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Marks awarded for the correct answer.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_questions_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created the question.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Question creation timestamp.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quiz_questions_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated the question.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Question last update timestamp.",
    )

    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="questions",
    )

    answers: Mapped[list["QuizAnswer"]] = relationship(
        "QuizAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<QuizQuestion(id={self.id}, position={self.marks}, question='{self.question[:20]}...')>"
        )