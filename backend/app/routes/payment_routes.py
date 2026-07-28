import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_instructor, require_student
from app.db.database import get_db
from app.models.user import User
from app.schemas.payment_schemas import (
    PaymentCreate,
    PaymentOut,
    PaymentStatusUpdate,
    PaymentWebhook,
    ReceiptOut,
)
from app.services.payment_service import PaymentService

router = APIRouter()


def _is_instructor(user: User) -> bool:
    return user.role.name.lower() == "instructor"


def _ensure_owner_or_instructor(user: User, owner_id: uuid.UUID) -> None:
    """A payment is the student's own record, or Instructor's to oversee.
    Admin has no business here - its job is users/roles only."""
    if _is_instructor(user) or user.id == owner_id:
        return
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You do not have permission to access this resource",
    )


# ---- Gateway webhook: NO auth ----
@router.post("/webhook")
async def payment_webhook(
    payload: PaymentWebhook,
    db: AsyncSession = Depends(get_db),
):
    await PaymentService(db).handle_webhook(
        payload.transaction_id,
        payload.payment_status,
        payload.receipt_url,
    )
    return {"received": True}


# ---- Instructor only: list all ----
@router.get(
    "",
    response_model=List[PaymentOut],
    dependencies=[Depends(require_instructor)],
)
async def list_payments(
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService(db).list_all()


# ---- Owner (student) or Instructor: view one ----
@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await PaymentService(db).get(payment_id)

    _ensure_owner_or_instructor(
        current_user,
        payment.student_id,
    )

    return payment


# ---- Student only: initiates their own payment ----
@router.post(
    "",
    response_model=PaymentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_student)],
)
async def initiate_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await PaymentService(db).initiate(
        current_user.id,
        payload,
    )


# ---- Status update (webhook-style): NO user auth ----
@router.patch("/{payment_id}/status", response_model=PaymentOut)
async def update_payment_status(
    payment_id: uuid.UUID,
    payload: PaymentStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await PaymentService(db).update_status(
        payment_id,
        payload.payment_status,
        payload.transaction_id,
        payload.receipt_url,
    )


# ---- Owner (student) or Instructor: receipt ----
@router.get("/{payment_id}/receipt", response_model=ReceiptOut)
async def get_receipt(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await PaymentService(db).get(payment_id)

    _ensure_owner_or_instructor(
        current_user,
        payment.student_id,
    )

    return ReceiptOut(
        payment_id=payment.id,
        transaction_id=payment.transaction_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_status=(
            payment.payment_status.value
            if hasattr(payment.payment_status, "value")
            else payment.payment_status
        ),
        receipt_url=payment.receipt_url,
        payment_date=payment.payment_date,
    )