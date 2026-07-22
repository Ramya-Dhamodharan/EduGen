import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.course import Course


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, payment_id: uuid.UUID) -> Payment:
        p = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not p:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Payment {payment_id} not found")
        return p

    def list_all(self) -> List[Payment]:
        return self.db.query(Payment).all()

    def get(self, payment_id: uuid.UUID) -> Payment:
        return self._get(payment_id)

    def list_for_student(self, student_id: uuid.UUID) -> List[Payment]:
        return self.db.query(Payment).filter(Payment.student_id == student_id).all()

    def initiate(self, student_id: uuid.UUID, data) -> Payment:
        if not self.db.query(Course).filter(Course.id == data.course_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Course {data.course_id} does not exist")

        # A fresh transaction id is generated; the gateway confirms it later.
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
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update_status(self, payment_id: uuid.UUID, new_status: str,
                      transaction_id: str | None = None,
                      receipt_url: str | None = None) -> Payment:
        payment = self._get(payment_id)
        payment.payment_status = PaymentStatus(new_status)
        if transaction_id:
            payment.transaction_id = transaction_id
        if receipt_url:
            payment.receipt_url = receipt_url
        if payment.payment_status == PaymentStatus.SUCCESS and not payment.payment_date:
            payment.payment_date = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def handle_webhook(self, transaction_id: str, new_status: str,
                       receipt_url: str | None = None) -> Payment:
        """Gateway callback: find the payment by transaction id and update it."""
        payment = (
            self.db.query(Payment)
            .filter(Payment.transaction_id == transaction_id)
            .first()
        )
        if not payment:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                f"No payment for transaction {transaction_id}")
        payment.payment_status = PaymentStatus(new_status)
        if receipt_url:
            payment.receipt_url = receipt_url
        if payment.payment_status == PaymentStatus.SUCCESS and not payment.payment_date:
            payment.payment_date = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(payment)
        return payment
