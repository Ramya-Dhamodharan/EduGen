import uuid
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)

    transaction_id = Column(String(100), nullable=False, unique=True)

    amount = Column(Numeric(10, 2), nullable=False)

    payment_method = Column(String(50), nullable=False)
    payment_gateway = Column(String(50), nullable=True)

    payment_status = Column(String(30), nullable=False)

    payment_date = Column(DateTime(timezone=True), nullable=True)

    currency = Column(String(10), nullable=True)
    receipt_url = Column(String(500), nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", back_populates="payments")
