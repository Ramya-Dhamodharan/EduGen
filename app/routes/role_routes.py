from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut
from app.services.role_service import RoleService

router = APIRouter()


@router.get("", response_model=List[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return RoleService(db).list_roles()


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return RoleService(db).get_role(role_id)


@router.post("", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    return RoleService(db).create_role(payload)


@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    return RoleService(db).update_role(role_id, payload)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    RoleService(db).delete_role(role_id)
