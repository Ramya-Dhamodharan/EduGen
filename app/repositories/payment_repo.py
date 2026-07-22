<<<<<<< HEAD
from uuid import UUID
=======
import uuid
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6

from sqlalchemy.orm import Session

from app.models.payment import Payment
<<<<<<< HEAD
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
=======


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

    def get_all(self) -> list[Payment]:
        return self.db.query(Payment).all()

    def get_by_student_id(self, student_id: uuid.UUID) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.student_id == student_id)
            .all()
        )

    def get_by_transaction_id(
        self,
        transaction_id: str,
    ) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(Payment.transaction_id == transaction_id)
            .first()
        )

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update(self, payment: Payment) -> Payment:
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def delete(self, payment: Payment) -> None:
        self.db.delete(payment)
        self.db.commit()
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
