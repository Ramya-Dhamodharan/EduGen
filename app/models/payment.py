from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.course import Course

class PaymentMethod(str, Enum):
    CARD = "CARD"
    UPI = "UPI"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base):
    """
    Stores payment transactions made by students for courses.
    """

    __tablename__ = "payments"

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            name="pk_payments",
        ),

        UniqueConstraint(
            "transaction_id",
            name="uq_payments_transaction_id",
        ),

        CheckConstraint(
            "amount > 0",
            name="ck_payments_amount_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key of the payment.",
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_payments_student_users",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Student who made the payment.",
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            name="fk_payments_course_courses",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="Course purchased by the student.",
    )

    transaction_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Unique transaction identifier from the payment gateway.",
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Amount paid.",
    )

    payment_method: Mapped[PaymentMethod] = mapped_column(
        String(50),
        nullable=False,
        comment="Payment method used.",
    )

    payment_gateway: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Payment gateway used (Stripe, Razorpay, PayPal, etc.).",
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        String(30),
        nullable=False,
        comment="Current payment status.",
    )

    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date and time the payment was completed.",
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        server_default="INR",
        comment="Currency used for the transaction.",
    )

    receipt_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL of the payment receipt.",
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_payments_created_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who created the payment record.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the payment record was created.",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_payments_updated_by_users",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        comment="User who last updated the payment record.",
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True,
        comment="Timestamp when the payment record was last updated.",
    )

    student: Mapped["User"] = relationship(
        "User",
        foreign_keys=[student_id],
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="payments",
    )

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, transaction_id='{self.transaction_id}')>"
        )