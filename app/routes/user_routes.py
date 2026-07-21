from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user_schemas import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService
from app.database import get_db
from app.crud.enrollment import get_student_enrollments
from app.schemas.enrollment import EnrollmentResponse

router = APIRouter(
    prefix="/api/v1/students",
    tags=["Students"]
)


@router.get(
    "/{student_id}/enrollments",
    response_model=list[EnrollmentResponse]
)
def student_enrollments(
    student_id: int,
    db: Session = Depends(get_db)
):
    return get_student_enrollments(
        db,
        student_id
    )