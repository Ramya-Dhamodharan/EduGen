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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.module import Module
    from app.models.quiz import Quiz

class Lesson(Base):
    """
    Stores lessons that belong to a module.
    """

    __tablename__ = "lessons"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_lessons",
        ),




        
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the lesson.",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Lesson title.",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Lesson description.",
    )

    video_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Video URL associated with the lesson.",
    )


    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "modules.id",
            name="fk_lessons_module_id_modules",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Module that owns this lesson.",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Indicates whether the lesson is active.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_lessons_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created this lesson.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the lesson was created.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_lessons_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated this lesson.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the lesson was last updated.",
    )

    module: Mapped["Module"] = relationship(
        "Module",
        back_populates="lessons",
    )

    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz",
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title='{self.title}')>"