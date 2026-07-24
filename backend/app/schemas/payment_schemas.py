from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    course_id: UUID
    amount: Decimal
    payment_method: str = Field(..., description="CARD, UPI, NET_BANKING, or WALLET")
    currency: Optional[str] = "INR"
    payment_gateway: Optional[str] = None
    # student_id comes from the authenticated user.


class PaymentStatusUpdate(BaseModel):
    payment_status: str = Field(..., description="PENDING, SUCCESS, FAILED, or REFUNDED")
    transaction_id: Optional[str] = None
    receipt_url: Optional[str] = None


class PaymentWebhook(BaseModel):
    """Gateway callback payload (shape depends on your provider)."""
    transaction_id: str
    payment_status: str
    receipt_url: Optional[str] = None


class PaymentOut(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    transaction_id: Optional[str] = None
    amount: Decimal
    currency: Optional[str] = None
    payment_method: str
    payment_gateway: Optional[str] = None
    payment_status: str
    payment_date: Optional[datetime] = None
    receipt_url: Optional[str] = None

    class Config:
        from_attributes = True


class ReceiptOut(BaseModel):
    payment_id: UUID
    transaction_id: Optional[str] = None
    amount: Decimal
    currency: Optional[str] = None
    payment_status: str
    receipt_url: Optional[str] = None
    payment_date: Optional[datetime] = None