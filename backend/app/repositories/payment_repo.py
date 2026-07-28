import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        payment_id: uuid.UUID,
    ) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(
                Payment.id == payment_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Payment]:
        result = await self.db.execute(
            select(Payment)
        )
        return result.scalars().all()

    async def get_by_student_id(
        self,
        student_id: uuid.UUID,
    ) -> list[Payment]:
        result = await self.db.execute(
            select(Payment).where(
                Payment.student_id == student_id
            )
        )
        return result.scalars().all()

    async def get_by_transaction_id(
        self,
        transaction_id: str,
    ) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(
                Payment.transaction_id == transaction_id
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        payment: Payment,
    ) -> Payment:
        self.db.add(payment)

        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def update(
        self,
        payment: Payment,
    ) -> Payment:
        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def delete(
        self,
        payment: Payment,
    ) -> None:
        await self.db.delete(payment)
        await self.db.commit()