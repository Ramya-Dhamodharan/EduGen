import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.core.security import hash_password


class UserRepository:
    """Pure data-access layer for the users table."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, data: UserCreate) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role_id=data.role_id,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
