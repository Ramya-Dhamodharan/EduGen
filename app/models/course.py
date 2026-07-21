from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
    Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.module import Module
    from app.models.quiz import Quiz
    from app.models.enrollment import Enrollment
    from app.models.course_review import CourseReview
    from app.models.certificate import Certificate
    from app.models.payment import Payment

class CourseLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Course(Base):
    """
    Stores course information available in the LMS.
    """

    __tablename__ = "courses"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_courses",
        ),

        CheckConstraint(
            "price >= 0",
            name="ck_courses_price_positive",
        ),

        Index(
            "ix_courses_category_id",
            "category_id",
        ),


        Index(
            "ix_courses_title",
            "title",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the course.",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Course title displayed to learners.",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed course description.",
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Primary language of the course.",
    )

    duration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Estimated course duration.",
    )

    level: Mapped[CourseLevel] = mapped_column(
        Enum(
            CourseLevel,
            name="course_level_enum",
        ),
        nullable=False,
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Course price.",
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "categories.id",
            name="fk_courses_category_id_categories",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Category associated with this course.",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Indicates whether the course is active.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_courses_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created this course.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the course was created.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_courses_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated this course.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the course was last updated.",
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="courses",
    )

    modules: Mapped[list["Module"]] = relationship(
        "Module",
        back_populates="course",
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="course",
    )

    quizzes: Mapped[list["Quiz"]] = relationship(
        "Quiz",
        back_populates="course",
    )

    reviews: Mapped[list["CourseReview"]] = relationship(
        "CourseReview",
        back_populates="course",
    )

    certificates: Mapped[list["Certificate"]] = relationship(
        "Certificate",
        back_populates="course",
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="course",
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title='{self.title}')>"