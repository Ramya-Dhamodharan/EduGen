from uuid import UUID
from app.repositories.quiz_question_repo import get_questions_by_quiz
from app.schemas.quiz_question import QuizQuestionResponse

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
)

from app.repositories.quiz_question_repo import (
    create_quiz,
    get_all_quizzes,
    get_quiz_by_id,
    update_quiz,
    delete_quiz,
    get_quizzes_by_course,
    create_quiz_under_course,
    activate_quiz,
    deactivate_quiz,
)


# ==================================================
# Quiz Router
# ==================================================

router = APIRouter()


# ==================================================
# GET ALL QUIZZES
# GET /api/quizzes
# ==================================================

@router.get(
    "",
    response_model=list[QuizResponse],
)
def get_quizzes(
    db: Session = Depends(get_db),
):
    return get_all_quizzes(db)


# ==================================================
# GET QUIZ BY ID
# GET /api/quizzes/{quiz_id}
# ==================================================

@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
)
def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return get_quiz_by_id(
        db,
        quiz_id,
    )


# ==================================================
# CREATE QUIZ
# POST /api/quizzes
# ==================================================

@router.post(
    "",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
):
    return create_quiz(
        db,
        quiz_data,
    )


# ==================================================
# UPDATE QUIZ
# PUT /api/quizzes/{quiz_id}
# ==================================================

@router.put(
    "/{quiz_id}",
    response_model=QuizResponse,
)
def update(
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    db: Session = Depends(get_db),
):
    return update_quiz(
        db,
        quiz_id,
        quiz_data,
    )


# ==================================================
# DELETE QUIZ
# DELETE /api/quizzes/{quiz_id}
# ==================================================

@router.delete(
    "/{quiz_id}",
)
def delete(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return delete_quiz(
        db,
        quiz_id,
    )


# ==================================================
# ACTIVATE QUIZ
# PATCH /api/quizzes/{quiz_id}/activate
# ==================================================

@router.patch(
    "/{quiz_id}/activate",
    response_model=QuizResponse,
)
def activate(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return activate_quiz(
        db,
        quiz_id,
    )


# ==================================================
# DEACTIVATE QUIZ
# PATCH /api/quizzes/{quiz_id}/deactivate
# ==================================================

@router.patch(
    "/{quiz_id}/deactivate",
    response_model=QuizResponse,
)
def deactivate(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):
    return deactivate_quiz(
        db,
        quiz_id,
    )


# ==================================================
# GET QUIZZES BY COURSE
# GET /api/courses/{course_id}/quizzes
# ==================================================

course_quiz_router = APIRouter()


@course_quiz_router.get(
    "/{course_id}/quizzes",
    response_model=list[QuizResponse],
)
def get_course_quizzes(
    course_id: UUID,
    db: Session = Depends(get_db),
):
    return get_quizzes_by_course(
        db,
        course_id,
    )


# ==================================================
# CREATE QUIZ UNDER COURSE
# POST /api/courses/{course_id}/quizzes
# ==================================================

@course_quiz_router.post(
    "/{course_id}/quizzes",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course_quiz(
    course_id: UUID,
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
):
    return create_quiz_under_course(
        db,
        course_id,
        quiz_data,
    )