import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.enrollment_schemas import EnrollmentOut
from app.schemas.quiz_attempt_schemas import QuizAttemptOut
from app.schemas.certificate_schemas import CertificateOut
from app.schemas.payment_schemas import PaymentOut
from app.services.enrollment_service import EnrollmentService
from app.services.quiz_attempt_service import QuizAttemptService
from app.services.certificate_service import CertificateService
from app.services.payment_service import PaymentService

router = APIRouter()


def _ensure_owner_or_staff(user: User, student_id: uuid.UUID) -> None:
    if user.role.name.lower() in ("admin", "instructor") or user.id == student_id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")


# The student themselves, or staff (Admin/Instructor).
@router.get("/{student_id}/enrollments", response_model=List[EnrollmentOut])
def list_student_enrollments(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_owner_or_staff(current_user, student_id)
    return EnrollmentService(db).list_for_student(student_id)


# The student themselves, or staff (Admin/Instructor).
@router.get("/{student_id}/quiz-attempts", response_model=List[QuizAttemptOut])
def list_student_attempts(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_owner_or_staff(current_user, student_id)
    return QuizAttemptService(db).list_for_student(student_id)


# The student themselves, or staff (Admin/Instructor).
@router.get("/{student_id}/certificates", response_model=List[CertificateOut])
def list_student_certificates(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_owner_or_staff(current_user, student_id)
    return CertificateService(db).list_for_student(student_id)


# The student themselves, or staff (Admin/Instructor).
@router.get("/{student_id}/payments", response_model=List[PaymentOut])
def list_student_payments(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_owner_or_staff(current_user, student_id)
    return PaymentService(db).list_for_student(student_id)
