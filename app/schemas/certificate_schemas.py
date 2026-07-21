from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
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