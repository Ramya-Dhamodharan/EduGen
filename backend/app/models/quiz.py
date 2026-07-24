from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.quiz_attempt import QuizAttempt
    from app.models.quiz_question import QuizQuestion
    from app.models.course import Course


class Quiz(Base):
    """
    Stores quizzes associated with a course or lesson.
    """

    __tablename__ = "quizzes"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_quizzes",
        ),

        CheckConstraint(
            "total_marks >= 0",
            name="ck_quizzes_total_marks",
        ),

        CheckConstraint(
            "pass_marks >= 0",
            name="ck_quizzes_pass_marks_positive",
        ),

        CheckConstraint(
            "pass_marks <= total_marks",
            name="ck_quizzes_pass_marks_valid",
        ),

        CheckConstraint(
            "duration > 0",
            name="ck_quizzes_duration_positive",
        ),

        CheckConstraint(
            "duration_days > 0",
            name="ck_quizzes_duration_days_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the quiz.",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Quiz title.",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Quiz description.",
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            name="fk_quizzes_course_courses",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Course associated with the quiz.",
    )

    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "lessons.id",
            name="fk_quizzes_lesson_lessons",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="Lesson associated with the quiz.",
    )

    total_marks: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Maximum marks for the quiz.",
    )

    pass_marks: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Minimum marks required to pass.",
    )

    duration: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Quiz duration in minutes.",
    )

    duration_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment=(
            "Number of days, counted from a student's enrollment date, "
            "within which this quiz must be submitted. The submission "
            "deadline for a student is enrollment.enrolled_at + "
            "duration_days."
        ),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Whether the quiz is active.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quizzes_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created the quiz.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Quiz creation timestamp.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_quizzes_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated the quiz.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Quiz last update timestamp.",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="quizzes",
    )

    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="quizzes",
    )

    questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="quiz",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, title='{self.title}')>"