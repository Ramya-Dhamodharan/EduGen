import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    language = Column(String(50), nullable=True)
    duration = Column(String(50), nullable=True)
    level = Column(String(30), nullable=True)

    price = Column(Numeric(10, 2), nullable=True)

    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    is_active = Column(Boolean, default=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="courses")
    modules = relationship("Module", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    quizzes = relationship("Quiz", back_populates="course")
    reviews = relationship("CourseReview", back_populates="course")
    certificates = relationship("Certificate", back_populates="course")
    payments = relationship("Payment", back_populates="course")
