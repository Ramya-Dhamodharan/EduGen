from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Fields required to register/create a user."""
    password: str = Field(..., min_length=8, description="Plain-text password; will be hashed before storing")
    role_id: int


class UserUpdate(BaseModel):
    """All fields optional — supports partial updates."""
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    """Shape returned to the client — never includes password_hash."""
    id: UUID
    role_id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
