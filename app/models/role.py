from __future__ import annotations
from typing import TYPE_CHECKING


from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    """
    Master table containing all application roles
    such as Admin, Instructor and Student.
    """

    __tablename__ = "roles"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_roles"),
        Index("ix_roles_name", "name"),
        {
            "comment": "Stores all user roles available in the LMS."
        },
    )

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        comment="Primary key of the role.",
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Unique role name (Admin, Instructor, Student).",
    )

    created_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_roles_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
            use_alter=True,
        ),
        nullable=True,
        comment="User who created this role.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the role was created.",
    )

    updated_by: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_roles_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
            use_alter=True,
        ),
        nullable=True,
        comment="User who last updated this role.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the role was last updated.",
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
        foreign_keys="User.role_id",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"