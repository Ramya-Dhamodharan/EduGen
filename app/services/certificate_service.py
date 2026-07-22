import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.models.course import Course
from app.models.user import User
from app.schemas.certificate_schemas import CertificateCreate


class CertificateService:
    def __init__(self, db: Session):
        self.db = db

    def _get(self, certificate_id: uuid.UUID) -> Certificate:
        c = self.db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not c:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Certificate {certificate_id} not found")
        return c

    def list_all(self) -> List[Certificate]:
        return self.db.query(Certificate).all()

    def get(self, certificate_id: uuid.UUID) -> Certificate:
        return self._get(certificate_id)

    def list_for_student(self, student_id: uuid.UUID) -> List[Certificate]:
        return self.db.query(Certificate).filter(Certificate.student_id == student_id).all()

    def verify(self, certificate_number: str) -> Certificate | None:
        return (
            self.db.query(Certificate)
            .filter(Certificate.certificate_number == certificate_number)
            .first()
        )

    def issue(self, data: CertificateCreate) -> Certificate:
        if not self.db.query(User).filter(User.id == data.student_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Student {data.student_id} does not exist")
        if not self.db.query(Course).filter(Course.id == data.course_id).first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Course {data.course_id} does not exist")

        existing = (
            self.db.query(Certificate)
            .filter(Certificate.certificate_number == data.certificate_number)
            .first()
        )
        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Certificate number already exists")

        cert = Certificate(
            student_id=data.student_id,
            course_id=data.course_id,
            certificate_number=data.certificate_number,
            certificate_url=data.certificate_url,
        )
        self.db.add(cert)
        self.db.commit()
        self.db.refresh(cert)
        return cert

    def delete(self, certificate_id: uuid.UUID) -> None:
        cert = self._get(certificate_id)
        self.db.delete(cert)
        self.db.commit()
