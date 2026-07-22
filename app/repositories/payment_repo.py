from uuid import UUID

from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.schemas.payment_schemas import (
    PaymentCreate,
    PaymentStatusUpdate,
)


def get_all_payments(db: Session):
    return db.query(Payment).all()


def get_payment_by_id(
    db: Session,
    payment_id: UUID
):
    return (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )


def create_payment(
    db: Session,
    payment: PaymentCreate
):
    db_payment = Payment(
        **payment.model_dump()
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


def update_payment_status(
    db: Session,
    db_payment: Payment,
    payment: PaymentStatusUpdate
):
    db_payment.payment_status = payment.payment_status

    db.commit()
    db.refresh(db_payment)

    return db_payment


def get_payment_receipt(
    db: Session,
    payment_id: UUID
):
    return (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )


def get_student_payments(
    db: Session,
    student_id: UUID
):
    return (
        db.query(Payment)
        .filter(Payment.student_id == student_id)
        .all()
    )


def get_payment_by_transaction_id(
    db: Session,
    transaction_id: str
):
    return (
        db.query(Payment)
        .filter(Payment.transaction_id == transaction_id)
        .first()
    )