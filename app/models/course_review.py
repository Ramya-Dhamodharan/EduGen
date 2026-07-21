from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course


class CourseReview(Base):
    """
    Stores student reviews and ratings for courses.
    """

    __tablename__ = "course_reviews"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_course_reviews",
        ),

        UniqueConstraint(
            "course_id",
            "student_id",
            name="uq_course_reviews_course_student",
        ),

        CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="ck_course_reviews_rating",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the review.",
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            name="fk_course_reviews_course_courses",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Course being reviewed.",
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_course_reviews_student_users",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Student who submitted the review.",
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Rating given by the student (1 to 5).",
    )

    review: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Written review provided by the student.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_course_reviews_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created this review record.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the review was created.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_course_reviews_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated the review.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the review was last updated.",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="reviews",
    )

    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
    )

    def __repr__(self) -> str:
        return (
            f"<CourseReview(id={self.id}, rating={self.rating})>"
        )