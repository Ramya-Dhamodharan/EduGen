import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", use_alter=True, name="fk_roles_created_by_users"),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", use_alter=True, name="fk_roles_updated_by_users"),
        nullable=True,
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="role", foreign_keys="User.role_id")

    def __repr__(self):
        return f"<Role id={self.id} name={self.name}>"
