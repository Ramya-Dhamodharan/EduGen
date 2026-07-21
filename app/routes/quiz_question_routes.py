from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy.orm import Session

from app.config.database import get_db

from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    CourseQuizCreate
)

from app.crud.quiz import (
    create_quiz,
    get_all_quizzes,
    get_quiz_by_id,
    update_quiz,
    delete_quiz,
    create_course_quiz,
    get_course_quizzes,
    activate_quiz,
    deactivate_quiz
)


router = APIRouter()


# ==========================================
# GET ALL QUIZZES
# ==========================================

@router.get(
    "",
    response_model=list[QuizResponse]
)
def get_quizzes(
    db: Session = Depends(get_db)
):

    return get_all_quizzes(db)


# ==========================================
# GET QUIZ BY ID
# ==========================================

@router.get(
    "/{quiz_id}",
    response_model=QuizResponse
)
def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db)
):

    return get_quiz_by_id(
        db,
        quiz_id
    )


# ==========================================
# CREATE QUIZ
# ==========================================

@router.post(
    "",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED
)
def create(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):

    return create_quiz(
        db,
        quiz_data
    )


# ==========================================
# UPDATE QUIZ
# ==========================================

@router.put(
    "/{quiz_id}",
    response_model=QuizResponse
)
def update(
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db)
):

    return update_quiz(
        db,
        quiz_id,
        quiz_data
    )


# ==========================================
# DELETE QUIZ
# ==========================================

@router.delete(
    "/{quiz_id}"
)
def delete(
    quiz_id: UUID,
    db: Session = Depends(get_db)
):

    return delete_quiz(
        db,
        quiz_id
    )


# ==========================================
# CREATE QUIZ UNDER COURSE
# ==========================================

@router.post(
    "/courses/{course_id}/quizzes",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED
)
def create_quiz_for_course(
    course_id: int,
    quiz_data: CourseQuizCreate,
    db: Session = Depends(get_db)
):

    return create_course_quiz(
        db,
        course_id,
        quiz_data
    )


# ==========================================
# GET COURSE QUIZZES
# ==========================================

@router.get(
    "/courses/{course_id}/quizzes",
    response_model=list[QuizResponse]
)
def get_quizzes_for_course(
    course_id: int,
    db: Session = Depends(get_db)
):

    return get_course_quizzes(
        db,
        course_id
    )


# ==========================================
# ACTIVATE QUIZ
# ==========================================

@router.patch(
    "/{quiz_id}/activate",
    response_model=QuizResponse
)
def activate(
    quiz_id: UUID,
    db: Session = Depends(get_db)
):

    return activate_quiz(
        db,
        quiz_id
    )


# ==========================================
# DEACTIVATE QUIZ
# ==========================================

@router.patch(
    "/{quiz_id}/deactivate",
    response_model=QuizResponse
)
def deactivate(
    quiz_id: UUID,
    db: Session = Depends(get_db)
):

    return deactivate_quiz(
        db,
        quiz_id
    )