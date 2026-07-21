from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptSubmit,
    QuizAttemptResponse,
)

from app.crud.quiz_attempt import (
    start_quiz_attempt,
    get_quiz_attempt_by_id,
    update_quiz_attempt,
    submit_quiz_attempt,
    delete_quiz_attempt,
    get_student_quiz_attempts,
    get_quiz_attempts,
)


router = APIRouter()


# ==================================================
# 1. START QUIZ ATTEMPT
#
# POST /api/quiz-attempts/start
#
# Description:
# Start a new quiz attempt
# ==================================================

@router.post(
    "/start",
    response_model=QuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_attempt(
    attempt_data: QuizAttemptCreate,
    db: Session = Depends(get_db),
):

    return start_quiz_attempt(
        db=db,
        attempt_data=attempt_data,
    )


# ==================================================
# 2. GET QUIZ ATTEMPT BY ID
#
# GET /api/quiz-attempts/{attempt_id}
#
# Description:
# Get a quiz attempt by ID
# ==================================================

@router.get(
    "/{attempt_id}",
    response_model=QuizAttemptResponse,
)
def get_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
):

    return get_quiz_attempt_by_id(
        db=db,
        attempt_id=attempt_id,
    )


# ==================================================
# 3. UPDATE QUIZ ATTEMPT
#
# PUT /api/quiz-attempts/{attempt_id}
#
# Description:
# Update a quiz attempt
# ==================================================

@router.put(
    "/{attempt_id}",
    response_model=QuizAttemptResponse,
)
def update_attempt(
    attempt_id: UUID,
    attempt_data: QuizAttemptUpdate,
    db: Session = Depends(get_db),
):

    return update_quiz_attempt(
        db=db,
        attempt_id=attempt_id,
        attempt_data=attempt_data,
    )


# ==================================================
# 4. SUBMIT QUIZ ATTEMPT
#
# POST /api/quiz-attempts/{attempt_id}/submit
#
# Description:
# Submit and score a quiz attempt
# ==================================================

@router.post(
    "/{attempt_id}/submit",
    response_model=QuizAttemptResponse,
)
def submit_attempt(
    attempt_id: UUID,
    submit_data: QuizAttemptSubmit,
    db: Session = Depends(get_db),
):

    return submit_quiz_attempt(
        db=db,
        attempt_id=attempt_id,
        submit_data=submit_data,
    )


# ==================================================
# 5. DELETE QUIZ ATTEMPT
#
# DELETE /api/quiz-attempts/{attempt_id}
#
# Description:
# Delete a quiz attempt
# ==================================================

@router.delete(
    "/{attempt_id}",
)
def delete_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
):

    return delete_quiz_attempt(
        db=db,
        attempt_id=attempt_id,
    )


# ==================================================
# 6. GET QUIZ ATTEMPTS FOR STUDENT
#
# GET /api/users/{student_id}/quiz-attempts
#
# Description:
# List quiz attempts for a student
# ==================================================

@router.get(
    "/student/{student_id}",
    response_model=list[QuizAttemptResponse],
)
def get_student_attempts(
    student_id: UUID,
    db: Session = Depends(get_db),
):

    return get_student_quiz_attempts(
        db=db,
        student_id=student_id,
    )


# ==================================================
# 7. GET QUIZ ATTEMPTS
#
# GET /api/quizzes/{quiz_id}/attempts
#
# Description:
# List all attempts for a quiz
# ==================================================

@router.get(
    "/quiz/{quiz_id}",
    response_model=list[QuizAttemptResponse],
)
def get_attempts_for_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):

    return get_quiz_attempts(
        db=db,
        quiz_id=quiz_id,
    )