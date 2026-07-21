from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.user import User

from app.repositories import certificate_repo
from app.schemas.certificate_schemas import CertificateCreate


def get_all_certificates(db: Session):
    return certificate_repo.get_all_certificates(db)


def get_certificate_by_id(db: Session, certificate_id: UUID):
    certificate = certificate_repo.get_certificate_by_id(
        db,
        certificate_id
    )

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found."
        )

    return certificate


def create_certificate(db: Session, certificate: CertificateCreate):

    course = (
        db.query(Course)
        .filter(Course.id == certificate.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found."
        )

    student = (
        db.query(User)
        .filter(User.id == certificate.student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    existing_certificate = certificate_repo.verify_certificate(
        db,
        certificate.certificate_number
    )

    if existing_certificate:
        raise HTTPException(
            status_code=409,
            detail="Certificate number already exists."
        )

    return certificate_repo.create_certificate(
        db,
        certificate
    )


def delete_certificate(
    db: Session,
    certificate_id: UUID
):

    certificate = certificate_repo.get_certificate_by_id(
        db,
        certificate_id
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found."
        )

    certificate_repo.delete_certificate(
        db,
        certificate
    )

    return {
        "message": "Certificate deleted successfully."
    }


def verify_certificate(
    db: Session,
    certificate_number: str
):

    certificate = certificate_repo.verify_certificate(
        db,
        certificate_number
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found."
        )

    return certificate


def get_student_certificates(
    db: Session,
    student_id: UUID
):
    return certificate_repo.get_student_certificates(
        db,
        student_id
    )