import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff
from app.schemas.certificate_schemas import (
    CertificateCreate,
    CertificateOut,
    CertificateVerifyOut,
)
from app.services.certificate_service import CertificateService

router = APIRouter()


def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


# ---- Public: verify a certificate by its number (no auth) ----
# Declared before /{certificate_id} so "verify" isn't captured as an id.
@router.get("/verify/{certificate_number}", response_model=CertificateVerifyOut)
def verify_certificate(certificate_number: str, db: Session = Depends(get_db)):
    cert = CertificateService(db).verify(certificate_number)
    if not cert:
        return CertificateVerifyOut(valid=False, certificate_number=certificate_number)
    return CertificateVerifyOut(
        valid=True,
        certificate_number=cert.certificate_number,
        student_id=cert.student_id,
        course_id=cert.course_id,
        issued_at=cert.issued_at,
    )


# ---- Staff: list all ----
@router.get("", response_model=List[CertificateOut], dependencies=[Depends(require_staff)])
def list_certificates(db: Session = Depends(get_db)):
    return CertificateService(db).list_all()


# ---- Owner or staff: view one ----
@router.get("/{certificate_id}", response_model=CertificateOut)
def get_certificate(
    certificate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = CertificateService(db).get(certificate_id)
    if not _is_staff(current_user) and current_user.id != cert.student_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")
    return cert


# ---- Staff: issue ----
@router.post("", response_model=CertificateOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def issue_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    return CertificateService(db).issue(payload)


# ---- Staff: delete ----
@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_staff)])
def delete_certificate(certificate_id: uuid.UUID, db: Session = Depends(get_db)):
    CertificateService(db).delete(certificate_id)