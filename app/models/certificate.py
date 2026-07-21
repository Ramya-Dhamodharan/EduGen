from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Certificate(Base):
    """
    Stores certificates issued to students after
    successfully completing a course.
    """

    __tablename__ = "certificates"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_certificates",
        ),

        UniqueConstraint(
            "certificate_number",
            name="uq_certificates_certificate_number",
        ),

        UniqueConstraint(
            "student_id",
            "course_id",
            name="uq_certificates_student_course",
        ),

        Index(
            "ix_certificates_student_id",
            "student_id",
        ),

        Index(
            "ix_certificates_course_id",
            "course_id",
        ),

        Index(
            "ix_certificates_issued_at",
            "issued_at",
        ),

        {
            "comment": "Stores certificates issued after course completion."
        },
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the certificate.",
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_certificates_student_users",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Student who earned the certificate.",
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            name="fk_certificates_course_courses",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Course associated with the certificate.",
    )

    certificate_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Unique certificate number.",
    )

    certificate_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL of the generated certificate.",
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Date and time when the certificate was issued.",
    )

    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="certificates",
    )

    def __repr__(self) -> str:
        return (
            f"<Certificate(id={self.id}, "
            f"certificate_number='{self.certificate_number}')>"
        )