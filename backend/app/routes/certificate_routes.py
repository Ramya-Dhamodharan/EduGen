import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_instructor
from app.db.database import get_db
from app.models.user import User
from app.schemas.certificate_schemas import (
    CertificateCreate,
    CertificateOut,
    CertificateVerifyOut,
)
from app.services.certificate_service import CertificateService

router = APIRouter()


def _is_instructor(user: User) -> bool:
    return user.role.name.lower() == "instructor"


def _ensure_owner_or_instructor(user: User, owner_id: uuid.UUID) -> None:
    """Certificates are the student's own record, or Instructor's to manage.
    Admin has no business here - its job is users/roles only."""
    if _is_instructor(user) or user.id == owner_id:
        return
    raise HTTPException(
        status.HTTP_403_FORBIDDEN,
        "You do not have permission to access this resource",
    )


# ---- Public: verify a certificate by its number (no auth) ----
# Declared before /{certificate_id} so "verify" isn't captured as an id.
@router.get(
    "/verify/{certificate_number}",
    status_code=status.HTTP_200_OK,
    response_model=CertificateVerifyOut,
)
async def verify_certificate(
    certificate_number: str,
    db: AsyncSession = Depends(get_db),
):
    cert = await CertificateService(db).verify(certificate_number)

    if not cert:
        return CertificateVerifyOut(
            valid=False,
            certificate_number=certificate_number,
        )

    return CertificateVerifyOut(
        valid=True,
        certificate_number=cert.certificate_number,
        student_id=cert.student_id,
        course_id=cert.course_id,
        issued_at=cert.issued_at,
    )


# ---- Instructor only: list all ----
@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[CertificateOut],
    dependencies=[Depends(require_instructor)],
)
async def list_certificates(
    db: AsyncSession = Depends(get_db),
):
    return await CertificateService(db).list_all()


# ---- Owner (student) or Instructor: view one ----
@router.get(
    "/{certificate_id}", status_code=status.HTTP_200_OK, response_model=CertificateOut
)
async def get_certificate(
    certificate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = await CertificateService(db).get(certificate_id)
    _ensure_owner_or_instructor(current_user, cert.student_id)
    return cert


# ---- Instructor only: issue ----
@router.post(
    "",
    response_model=CertificateOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def issue_certificate(
    payload: CertificateCreate,
    db: AsyncSession = Depends(get_db),
):
    return await CertificateService(db).issue(payload)


# ---- Instructor only: delete ----
@router.delete(
    "/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_instructor)],
)
async def delete_certificate(
    certificate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await CertificateService(db).delete(certificate_id)
