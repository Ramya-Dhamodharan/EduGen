import uuid
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session  # type: ignore[import]

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.role_repo import RoleRepository
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
from app.models.payment import Payment


class UserService:
    """Business rules for users (uniqueness, role validation, etc.)."""

    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.role_repo = RoleRepository(db)  # to validate role_id exists

    def list_users(self) -> List[User]:
        return self.repo.get_all()

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user

    def create_user(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{data.email}' is already registered",
            )
        if not self.role_repo.get_by_id(data.role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with id {data.role_id} does not exist",
            )
        return self.repo.create(data)

    def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = self.get_user(user_id)  # raises 404 if missing
        if data.role_id is not None and not self.role_repo.get_by_id(data.role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with id {data.role_id} does not exist",
            )
        return self.repo.update(user, data)

    def set_status(self, user_id: uuid.UUID, is_active: bool) -> User:
        user = self.get_user(user_id)
        user.is_active = is_active
        self.repo.db.commit()
        self.repo.db.refresh(user)
        return user

    def assign_role(self, user_id: uuid.UUID, role_id: int) -> User:
        user = self.get_user(user_id)
        if not self.role_repo.get_by_id(role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with id {role_id} does not exist",
            )
        user.role_id = role_id
        self.repo.db.commit()
        self.repo.db.refresh(user)
        return user

    def list_enrollments(self, user_id: uuid.UUID) -> List[Enrollment]:
        self.get_user(user_id)  # 404 if missing
        return (
            self.repo.db.query(Enrollment)
            .filter(Enrollment.student_id == user_id)
            .all()
        )

    def list_certificates(self, user_id: uuid.UUID) -> List[Certificate]:
        self.get_user(user_id)
        return (
            self.repo.db.query(Certificate)
            .filter(Certificate.student_id == user_id)
            .all()
        )

    def list_payments(self, user_id: uuid.UUID) -> List[Payment]:
        self.get_user(user_id)
        return (
            self.repo.db.query(Payment)
            .filter(Payment.student_id == user_id)
            .all()
        )

    def delete_user(self, user_id: uuid.UUID) -> None:
        user = self.get_user(user_id)  # raises 404 if missing
        self.repo.delete(user)