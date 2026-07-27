from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.lesson import Lesson


class Module(Base):
    """
    Stores modules that belong to a course.
    A course can contain multiple modules.
    """

    __tablename__ = "modules"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_modules",
        ),

        Index(
            "ix_modules_course_id",
            "course_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the module.",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Module title.",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Module description.",
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            name="fk_modules_course_id_courses",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Course that owns this module.",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Whether the module is active.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_modules_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created the module.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Module creation timestamp.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_modules_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated the module.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Module last update timestamp.",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="modules",
    )

    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Module(id={self.id}, title='{self.title}')>"