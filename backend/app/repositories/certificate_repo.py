import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate


class CertificateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        certificate_id: uuid.UUID,
    ) -> Certificate | None:
        result = await self.db.execute(
            select(Certificate).where(Certificate.id == certificate_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Certificate]:
        result = await self.db.execute(select(Certificate))
        return result.scalars().all()

    async def get_by_student_id(
        self,
        student_id: uuid.UUID,
    ) -> list[Certificate]:
        result = await self.db.execute(
            select(Certificate).where(Certificate.student_id == student_id)
        )
        return result.scalars().all()

    async def get_by_certificate_number(
        self,
        certificate_number: str,
    ) -> Certificate | None:
        result = await self.db.execute(
            select(Certificate).where(
                Certificate.certificate_number == certificate_number
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        certificate: Certificate,
    ) -> Certificate:
        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)
        return certificate

    async def delete(
        self,
        certificate: Certificate,
    ) -> None:
        await self.db.delete(certificate)
        await self.db.commit()
