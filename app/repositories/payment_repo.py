import uuid

from sqlalchemy.orm import Session

from app.models.payment import Payment


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
