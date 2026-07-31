import uuid
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4,


    )

    username: Mapped[str] = mapped_column(

        String(100),

        nullable=False,

    )

    email: Mapped[str] = mapped_column(

        String(255),

        unique=True,

        nullable=False,

    )

    password_hash: Mapped[str] = mapped_column(

        String(255),

        nullable=False,

    )

    is_active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,

        nullable=False,

    )

    role_id: Mapped[int] = mapped_column(

        ForeignKey("roles.id"),

        nullable=False,

    )

    role = relationship("Role", back_populates="users")
