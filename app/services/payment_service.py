<<<<<<< HEAD
import uuid
from datetime import datetime, timezone
from typing import List
=======
from uuid import UUID
>>>>>>> origin/dev

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
<<<<<<< HEAD
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.repositories.payment_repo import PaymentRepository


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_repo = PaymentRepository(db)

    def _get(self, payment_id: uuid.UUID) -> Payment:
        payment = self.payment_repo.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} not found",
            )

        return payment

    def list_all(self) -> List[Payment]:
        return self.payment_repo.get_all()

    def get(self, payment_id: uuid.UUID) -> Payment:
        return self._get(payment_id)

    def list_for_student(self, student_id: uuid.UUID) -> List[Payment]:
        return self.payment_repo.get_by_student_id(student_id)

    def initiate(self, student_id: uuid.UUID, data) -> Payment:
        course = (
            self.db.query(Course)
            .filter(Course.id == data.course_id)
            .first()
        )

        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {data.course_id} does not exist",
            )

        payment = Payment(
            student_id=student_id,
            course_id=data.course_id,
            transaction_id=f"TXN-{uuid.uuid4().hex[:16].upper()}",
            amount=data.amount,
            currency=data.currency or "INR",
            payment_method=PaymentMethod(data.payment_method),
            payment_gateway=data.payment_gateway,
            payment_status=PaymentStatus.PENDING,
            created_by=student_id,
        )

        return self.payment_repo.create(payment)

    def update_status(
        self,
        payment_id: uuid.UUID,
        new_status: str,
        transaction_id: str | None = None,
        receipt_url: str | None = None,
    ) -> Payment:

        payment = self._get(payment_id)

        payment.payment_status = PaymentStatus(new_status)

        if transaction_id:
            payment.transaction_id = transaction_id

        if receipt_url:
            payment.receipt_url = receipt_url

        if (
            payment.payment_status == PaymentStatus.SUCCESS
            and not payment.payment_date
        ):
            payment.payment_date = datetime.now(timezone.utc)

        return self.payment_repo.update(payment)

    def handle_webhook(
        self,
        transaction_id: str,
        new_status: str,
        receipt_url: str | None = None,
    ) -> Payment:

        payment = self.payment_repo.get_by_transaction_id(transaction_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No payment for transaction {transaction_id}",
            )

        payment.payment_status = PaymentStatus(new_status)

        if receipt_url:
            payment.receipt_url = receipt_url

        if (
            payment.payment_status == PaymentStatus.SUCCESS
            and not payment.payment_date
        ):
            payment.payment_date = datetime.now(timezone.utc)

        return self.payment_repo.update(payment)
=======
from app.models.user import User

from app.repositories import payment_repo
from app.schemas.payment_schemas import (
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
>>>>>>> origin/dev
