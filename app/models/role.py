import uuid

from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base

from app.models.user import User

class Role(Base):

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4,

    )

    name: Mapped[str] = mapped_column(

        String(50),

        unique=True,

        nullable=False,

    )

    users: Mapped[list["User"]] = relationship(

        "User",

        back_populates="role",

    )
