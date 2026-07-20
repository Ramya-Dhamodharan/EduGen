import uuid
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.role_repo import RoleRepository
from app.schemas.user import UserCreate, UserUpdate


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

    def delete_user(self, user_id: uuid.UUID) -> None:
        user = self.get_user(user_id)  # raises 404 if missing
        self.repo.delete(user)
