import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.course import Course
from app.models.user import User
from app.repositories.certificate_repo import CertificateRepository
from app.schemas.certificate_schemas import CertificateCreate


class CertificateService:
    def __init__(self, db: Session):
        self.db = db
        self.certificate_repo = CertificateRepository(db)

    def _get(self, certificate_id: uuid.UUID) -> Certificate:
        certificate = self.certificate_repo.get_by_id(certificate_id)

        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certificate {certificate_id} not found",
            )

        return certificate

    def list_all(self):
        return self.certificate_repo.get_all()

    def get(self, certificate_id: uuid.UUID):
        return self._get(certificate_id)

    def list_for_student(self, student_id: uuid.UUID):
        return self.certificate_repo.get_by_student_id(student_id)

    def verify(self, certificate_number: str):
        return self.certificate_repo.get_by_certificate_number(certificate_number)

    def issue(self, data: CertificateCreate):
        student = (
            self.db.query(User)
            .filter(User.id == data.student_id)
            .first()
        )

        if not student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {data.student_id} does not exist",
            )

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

        existing = self.certificate_repo.get_by_certificate_number(
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

        return self.certificate_repo.create(certificate)

    def delete(self, certificate_id: uuid.UUID):
        certificate = self._get(certificate_id)
        self.certificate_repo.delete(certificate)
