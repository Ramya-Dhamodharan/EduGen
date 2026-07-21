from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.certificate import (
    CertificateCreate,
    CertificateResponse,
)
from app.services import certificate_service

router = APIRouter(
    prefix="/api",
    tags=["Certificates"]
)


@router.get(
    "/certificates",
    response_model=list[CertificateResponse]
)
def get_all_certificates(
    db: Session = Depends(get_db)
):
    return certificate_service.get_all_certificates(db)


@router.get(
    "/certificates/{certificate_id}",
    response_model=CertificateResponse
)
def get_certificate_by_id(
    certificate_id: UUID,
    db: Session = Depends(get_db)
):
    return certificate_service.get_certificate_by_id(
        db,
        certificate_id
    )


@router.post(
    "/certificates",
    response_model=CertificateResponse,
    status_code=201
)
def create_certificate(
    certificate: CertificateCreate,
    db: Session = Depends(get_db)
):
    return certificate_service.create_certificate(
        db,
        certificate
    )


@router.delete(
    "/certificates/{certificate_id}"
)
def delete_certificate(
    certificate_id: UUID,
    db: Session = Depends(get_db)
):
    return certificate_service.delete_certificate(
        db,
        certificate_id
    )


@router.get(
    "/certificates/verify/{certificate_number}",
    response_model=CertificateResponse
)
def verify_certificate(
    certificate_number: str,
    db: Session = Depends(get_db)
):
    return certificate_service.verify_certificate(
        db,
        certificate_number
    )


@router.get(
    "/students/{student_id}/certificates",
    response_model=list[CertificateResponse]
)
def get_student_certificates(
    student_id: UUID,
    db: Session = Depends(get_db)
):
    return certificate_service.get_student_certificates(
        db,
        student_id
    )