from uuid import UUID

from sqlalchemy.orm import Session

from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate


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