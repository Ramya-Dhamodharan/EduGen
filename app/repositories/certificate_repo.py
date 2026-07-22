import uuid

from sqlalchemy.orm import Session

from app.models.certificate import Certificate


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
