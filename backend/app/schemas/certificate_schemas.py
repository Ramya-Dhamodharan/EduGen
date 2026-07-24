from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
    student_id: UUID
    course_id: UUID
    certificate_number: str = Field(..., min_length=1, max_length=100)
    certificate_url: Optional[str] = None


class CertificateOut(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    certificate_number: str
    certificate_url: Optional[str] = None
    issued_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CertificateVerifyOut(BaseModel):
    """Public verification response - confirms validity without exposing internals."""
    valid: bool
    certificate_number: str
    student_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    issued_at: Optional[datetime] = None