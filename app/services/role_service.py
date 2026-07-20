from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.role_repo import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """
    Business rules live here (e.g. duplicate-name checks).
    Routes call this layer; this layer calls the repository.
    """

    def __init__(self, db: Session):
        self.repo = RoleRepository(db)

    def list_roles(self) -> List[Role]:
        return self.repo.get_all()

    def get_role(self, role_id: int) -> Role:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found",
            )
        return role

    def create_role(self, data: RoleCreate) -> Role:
        if self.repo.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{data.name}' already exists",
            )
        return self.repo.create(data)

    def update_role(self, role_id: int, data: RoleUpdate) -> Role:
        role = self.get_role(role_id)  # raises 404 if missing
        return self.repo.update(role, data)

    def delete_role(self, role_id: int) -> None:
        role = self.get_role(role_id)  # raises 404 if missing
        self.repo.delete(role)
