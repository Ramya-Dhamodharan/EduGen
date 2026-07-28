import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.repositories.payment_repo import PaymentRepository


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)

    async def _get(self, payment_id: uuid.UUID) -> Payment:
        payment = await self.payment_repo.get_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} not found",
            )

        return payment

    async def list_all(self) -> List[Payment]:
        return await self.payment_repo.get_all()

    async def get(self, payment_id: uuid.UUID) -> Payment:
        return await self._get(payment_id)

    async def list_for_student(
        self,
        student_id: uuid.UUID,
    ) -> List[Payment]:
        return await self.payment_repo.get_by_student_id(student_id)

    async def initiate(
        self,
        student_id: uuid.UUID,
        data,
    ) -> Payment:

        result = await self.db.execute(
            select(Course).where(Course.id == data.course_id)
        )
        course = result.scalar_one_or_none()

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

        return await self.payment_repo.create(payment)

    async def update_status(
        self,
        payment_id: uuid.UUID,
        new_status: str,
        transaction_id: str | None = None,
        receipt_url: str | None = None,
    ) -> Payment:

        payment = await self._get(payment_id)

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

        return await self.payment_repo.update(payment)

    async def handle_webhook(
        self,
        transaction_id: str,
        new_status: str,
        receipt_url: str | None = None,
    ) -> Payment:

        payment = await self.payment_repo.get_by_transaction_id(
            transaction_id
        )

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

        return await self.payment_repo.update(payment)