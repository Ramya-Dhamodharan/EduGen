import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate import Certificate
from app.models.course import Course
from app.models.user import User
from app.repositories.certificate_repo import CertificateRepository
from app.schemas.certificate_schemas import CertificateCreate


class CertificateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.certificate_repo = CertificateRepository(db)

    async def _get(self, certificate_id: uuid.UUID) -> Certificate:
        certificate = await self.certificate_repo.get_by_id(certificate_id)

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certificate {certificate_id} not found",
            )

        return certificate

    async def list_all(self):
        return await self.certificate_repo.get_all()

    async def get(self, certificate_id: uuid.UUID):
        return await self._get(certificate_id)

    async def list_for_student(self, student_id: uuid.UUID):
        return await self.certificate_repo.get_by_student_id(student_id)

    async def verify(self, certificate_number: str):
        return await self.certificate_repo.get_by_certificate_number(
            certificate_number
        )

    async def issue(self, data: CertificateCreate):
        result = await self.db.execute(
            select(User).where(User.id == data.student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {data.student_id} does not exist",
            )

        result = await self.db.execute(
            select(Course).where(Course.id == data.course_id)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course {data.course_id} does not exist",
            )

        existing = await self.certificate_repo.get_by_certificate_number(
            data.certificate_number
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Certificate number already exists",
            )

        certificate = Certificate(
            student_id=data.student_id,
            course_id=data.course_id,
            certificate_number=data.certificate_number,
            certificate_url=data.certificate_url,
        )

        return await self.certificate_repo.create(certificate)

    async def delete(self, certificate_id: uuid.UUID):
        certificate = await self._get(certificate_id)
        await self.certificate_repo.delete(certificate)