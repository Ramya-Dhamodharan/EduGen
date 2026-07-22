<<<<<<< HEAD
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
=======
from uuid import UUID
from datetime import datetime
from decimal import Decimal
>>>>>>> origin/dev

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
<<<<<<< HEAD
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
=======
    student_id: UUID
    course_id: UUID
    transaction_id: str = Field(max_length=100)
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(max_length=50)
    payment_gateway: str | None = Field(default=None, max_length=50)
    payment_status: str = Field(max_length=30)
    payment_date: datetime | None = None
    currency: str | None = Field(default=None, max_length=10)
    receipt_url: str | None = Field(default=None, max_length=500)


class PaymentStatusUpdate(BaseModel):
    payment_status: str = Field(max_length=30)


class PaymentResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    transaction_id: str
    amount: Decimal
    payment_method: str
    payment_gateway: str | None
    payment_status: str
    payment_date: datetime | None
    currency: str | None
    receipt_url: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
>>>>>>> origin/dev
