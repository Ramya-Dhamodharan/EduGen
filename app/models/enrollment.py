from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from enum import Enum

class EnrollmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

if TYPE_CHECKING: 
    from app.models.course import Course
    from app.models.user import User


class Enrollment(Base):
    """
    Stores student enrollments for courses.
    """

    __tablename__ = "enrollments"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_enrollments",
        ),

        UniqueConstraint(
            "student_id",
            "course_id",
            name="uq_enrollments_student_course",
        ),

        Index(
            "ix_enrollments_course_id",
            "course_id",
        ),

    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the enrollment.",
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_enrollments_student_users",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Student enrolled in the course.",
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            name="fk_enrollments_course_courses",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Course in which the student is enrolled.",
    )

    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(
            EnrollmentStatus,
            name="enrollment_status_enum",
        ),
        nullable=False,
        comment="Current enrollment status.",
    )

    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Enrollment date.",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Course start date.",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Course completion date.",
    )

    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="enrollments",
    )

    def __repr__(self) -> str:
        return (
            f"<Enrollment(student={self.student_id}, "
            f"course={self.course_id})>"
        )