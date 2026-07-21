from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.payment_schemas import (
    PaymentCreate,
    PaymentStatusUpdate,
    PaymentResponse,
)
from app.services import payment_service

router = APIRouter(
    prefix="/api",
    tags=["Payments"]
)


@router.get(
    "/payments",
    response_model=list[PaymentResponse]
)
def get_all_payments(
    db: Session = Depends(get_db)
):
    return payment_service.get_all_payments(db)


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse
)
def get_payment_by_id(
    payment_id: UUID,
    db: Session = Depends(get_db)
):
    return payment_service.get_payment_by_id(
        db,
        payment_id
    )


@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    return payment_service.create_payment(
        db,
        payment
    )


@router.patch(
    "/payments/{payment_id}/status",
    response_model=PaymentResponse
)
def update_payment_status(
    payment_id: UUID,
    payment: PaymentStatusUpdate,
    db: Session = Depends(get_db)
):
    return payment_service.update_payment_status(
        db,
        payment_id,
        payment
    )


@router.get(
    "/payments/{payment_id}/receipt"
)
def get_payment_receipt(
    payment_id: UUID,
    db: Session = Depends(get_db)
):
    return payment_service.get_payment_receipt(
        db,
        payment_id
    )


@router.get(
    "/students/{student_id}/payments",
    response_model=list[PaymentResponse]
)
def get_student_payments(
    student_id: UUID,
    db: Session = Depends(get_db)
):
    return payment_service.get_student_payments(
        db,
        student_id
    )


@router.post(
    "/payments/webhook",
    response_model=PaymentResponse
)
def payment_webhook(
    transaction_id: str,
    payment: PaymentStatusUpdate,
    db: Session = Depends(get_db)
):
    return payment_service.payment_webhook(
        db,
        transaction_id,
        payment
    )