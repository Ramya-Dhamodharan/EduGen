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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.role import Role


class User(Base):
    """
    Stores application users including students,
    instructors, and administrators.
    """

    __tablename__ = "users"

    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_users"),

        UniqueConstraint(
            "email",
            name="uq_users_email",
        ),

        CheckConstraint(
            "char_length(username) >= 3",
            name="ck_users_username_length",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the user.",
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display username.",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Unique email address used for login.",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hashed user password.",
    )

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "roles.id",
            name="fk_users_role_id_roles",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Role assigned to the user.",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Indicates whether the account is active.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_users_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created this account.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the account was created.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_users_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated this account.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the account was last updated.",
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
        foreign_keys=[role_id],
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"