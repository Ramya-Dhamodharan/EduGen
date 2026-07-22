import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff
from app.schemas.payment_schemas import (
    PaymentCreate,
    PaymentStatusUpdate,
    PaymentWebhook,
    PaymentOut,
    ReceiptOut,
)
from app.services.payment_service import PaymentService

router = APIRouter()


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _ensure_owner_or_staff(user: User, owner_id: uuid.UUID) -> None:
    if _is_staff(user) or user.id == owner_id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")


# ---- Gateway webhook: NO auth (the gateway calls this, not a user) ----
# NOTE: in production, verify the gateway's signature header here before trusting it.
@router.post("/webhook")
def payment_webhook(payload: PaymentWebhook, db: Session = Depends(get_db)):
    PaymentService(db).handle_webhook(
        payload.transaction_id, payload.payment_status, payload.receipt_url
    )
    return {"received": True}


# ---- Staff: list all ----
@router.get("", response_model=List[PaymentOut], dependencies=[Depends(require_staff)])
def list_payments(db: Session = Depends(get_db)):
    return PaymentService(db).list_all()


# ---- Owner or staff: view one ----
@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: uuid.UUID, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    payment = PaymentService(db).get(payment_id)
    _ensure_owner_or_staff(current_user, payment.student_id)
    return payment


# ---- Student initiates their own payment ----
@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def initiate_payment(payload: PaymentCreate, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return PaymentService(db).initiate(current_user.id, payload)


# ---- Status update (webhook-style): NO user auth ----
# Called by the gateway/back-office with the payment id.
@router.patch("/{payment_id}/status", response_model=PaymentOut)
def update_payment_status(payment_id: uuid.UUID, payload: PaymentStatusUpdate,
                          db: Session = Depends(get_db)):
    return PaymentService(db).update_status(
        payment_id, payload.payment_status, payload.transaction_id, payload.receipt_url
    )


# ---- Owner or staff: receipt ----
@router.get("/{payment_id}/receipt", response_model=ReceiptOut)
def get_receipt(payment_id: uuid.UUID, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    payment = PaymentService(db).get(payment_id)
    _ensure_owner_or_staff(current_user, payment.student_id)
    return ReceiptOut(
        payment_id=payment.id,
        transaction_id=payment.transaction_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_status=payment.payment_status.value if hasattr(payment.payment_status, "value") else payment.payment_status,
        receipt_url=payment.receipt_url,
        payment_date=payment.payment_date,
    )