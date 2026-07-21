from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
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