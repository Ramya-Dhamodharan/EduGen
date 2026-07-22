<<<<<<< HEAD
from uuid import UUID
from datetime import datetime
=======
from datetime import datetime
from uuid import UUID
from typing import Optional
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
<<<<<<< HEAD
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
=======
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
>>>>>>> 4cc63f074f7848968be0acde5a8d625115aaebb6
