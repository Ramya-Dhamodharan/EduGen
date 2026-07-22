<<<<<<< HEAD
from datetime import datetime
from uuid import UUID
from typing import Optional
=======
from uuid import UUID
from datetime import datetime
>>>>>>> origin/dev

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
<<<<<<< HEAD
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
=======
    course_id: UUID
    student_id: UUID
    certificate_number: str = Field(
        max_length=100
    )
    certificate_url: str | None = Field(
        default=None,
        max_length=500
    )


class CertificateResponse(BaseModel):
    id: UUID
    course_id: UUID
    student_id: UUID
    certificate_number: str
    issued_at: datetime
    certificate_url: str | None

    class Config:
        from_attributes = True
>>>>>>> origin/dev
