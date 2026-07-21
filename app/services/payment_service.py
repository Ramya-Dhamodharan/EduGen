from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.user import User

from app.repositories import payment_repo
from app.schemas.payment import (
    PaymentCreate,
    PaymentStatusUpdate,
)


def get_all_payments(db: Session):
    return payment_repo.get_all_payments(db)


def get_payment_by_id(
    db: Session,
    payment_id: UUID
):
    payment = payment_repo.get_payment_by_id(
        db,
        payment_id
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found."
        )

    return payment


def create_payment(
    db: Session,
    payment: PaymentCreate
):
    student = (
        db.query(User)
        .filter(User.id == payment.student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    course = (
        db.query(Course)
        .filter(Course.id == payment.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found."
        )

    existing_payment = payment_repo.get_payment_by_transaction_id(
        db,
        payment.transaction_id
    )

    if existing_payment:
        raise HTTPException(
            status_code=409,
            detail="Transaction ID already exists."
        )

    return payment_repo.create_payment(
        db,
        payment
    )


def update_payment_status(
    db: Session,
    payment_id: UUID,
    payment: PaymentStatusUpdate
):
    db_payment = payment_repo.get_payment_by_id(
        db,
        payment_id
    )

    if not db_payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found."
        )

    return payment_repo.update_payment_status(
        db,
        db_payment,
        payment
    )


def get_payment_receipt(
    db: Session,
    payment_id: UUID
):
    payment = payment_repo.get_payment_receipt(
        db,
        payment_id
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found."
        )

    return {
        "receipt_url": payment.receipt_url
    }


def get_student_payments(
    db: Session,
    student_id: UUID
):
    return payment_repo.get_student_payments(
        db,
        student_id
    )


def payment_webhook(
    db: Session,
    transaction_id: str,
    payment: PaymentStatusUpdate
):
    db_payment = payment_repo.get_payment_by_transaction_id(
        db,
        transaction_id
    )

    if not db_payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found."
        )

    return payment_repo.update_payment_status(
        db,
        db_payment,
        payment
    )