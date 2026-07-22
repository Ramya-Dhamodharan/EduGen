<<<<<<< HEAD
import uuid
=======
from uuid import UUID
>>>>>>> origin/dev

from sqlalchemy.orm import Session

from app.models.certificate import Certificate
<<<<<<< HEAD


class CertificateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, certificate_id: uuid.UUID) -> Certificate | None:
        return (
            self.db.query(Certificate)
            .filter(Certificate.id == certificate_id)
            .first()
        )

    def get_all(self) -> list[Certificate]:
        return self.db.query(Certificate).all()

    def get_by_student_id(self, student_id: uuid.UUID) -> list[Certificate]:
        return (
            self.db.query(Certificate)
            .filter(Certificate.student_id == student_id)
            .all()
        )

    def get_by_certificate_number(
        self, certificate_number: str
    ) -> Certificate | None:
        return (
            self.db.query(Certificate)
            .filter(Certificate.certificate_number == certificate_number)
            .first()
        )

    def create(self, certificate: Certificate) -> Certificate:
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)
        return certificate

    def delete(self, certificate: Certificate) -> None:
        self.db.delete(certificate)
        self.db.commit()
=======
from app.schemas.certificate_schemas import CertificateCreate


def get_all_certificates(db: Session):
    return db.query(Certificate).all()


def get_certificate_by_id(db: Session, certificate_id: UUID):
    return (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )


def create_certificate(db: Session, certificate: CertificateCreate):
    db_certificate = Certificate(
        **certificate.model_dump()
    )

    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)

    return db_certificate


def delete_certificate(db: Session, db_certificate: Certificate):
    db.delete(db_certificate)
    db.commit()


def verify_certificate(db: Session, certificate_number: str):
    return (
        db.query(Certificate)
        .filter(
            Certificate.certificate_number == certificate_number
        )
        .first()
    )


def get_student_certificates(db: Session, student_id: UUID):
    return (
        db.query(Certificate)
        .filter(Certificate.student_id == student_id)
        .all()
    )
>>>>>>> origin/dev
