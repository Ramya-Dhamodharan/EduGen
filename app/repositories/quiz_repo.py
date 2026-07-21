from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.course import Course
from app.models.lesson import Lesson

from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
)


# ==========================================
# Create Quiz
# ==========================================

def create_quiz(
    db: Session,
    quiz_data: QuizCreate,
):
    # Check whether the course exists
    course = db.query(Course).filter(
        Course.id == quiz_data.course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # If lesson is provided, check whether it exists
    if quiz_data.lessons_id is not None:

        lesson = db.query(Lesson).filter(
            Lesson.id == quiz_data.lessons_id
        ).first()

        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

    # Validate pass marks
    if (
        quiz_data.pass_marks is not None
        and quiz_data.total_marks is not None
        and quiz_data.pass_marks > quiz_data.total_marks
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pass marks cannot be greater than total marks",
        )

    # Create quiz
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        course_id=quiz_data.course_id,
        lessons_id=quiz_data.lessons_id,
        total_marks=quiz_data.total_marks,
        pass_marks=quiz_data.pass_marks,
        duration=quiz_data.duration,
        is_active=quiz_data.is_active,
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


# ==========================================
# Get All Quizzes
# ==========================================

def get_all_quizzes(
    db: Session,
):
    return (
        db.query(Quiz)
        .order_by(Quiz.created_at.desc())
        .all()
    )


# ==========================================
# Get Quiz By ID
# ==========================================

def get_quiz_by_id(
    db: Session,
    quiz_id: UUID,
):
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id
    ).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    return quiz


# ==========================================
# Update Quiz
# ==========================================

def update_quiz(
    db: Session,
    quiz_id: UUID,
    quiz_data: QuizUpdate,
):
    # Get existing quiz
    quiz = get_quiz_by_id(
        db,
        quiz_id,
    )

    # Get only fields provided in request
    update_data = quiz_data.model_dump(
        exclude_unset=True
    )

    # Validate course if course_id is updated
    if "course_id" in update_data:

        course = db.query(Course).filter(
            Course.id == update_data["course_id"]
        ).first()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

    # Validate lesson if lessons_id is updated
    if (
        "lessons_id" in update_data
        and update_data["lessons_id"] is not None
    ):

        lesson = db.query(Lesson).filter(
            Lesson.id == update_data["lessons_id"]
        ).first()

        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

    # Calculate final marks
    total_marks = update_data.get(
        "total_marks",
        quiz.total_marks,
    )

    pass_marks = update_data.get(
        "pass_marks",
        quiz.pass_marks,
    )

    # Validate pass marks
    if (
        pass_marks is not None
        and total_marks is not None
        and pass_marks > total_marks
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pass marks cannot be greater than total marks",
        )

    # Update fields
    for field, value in update_data.items():
        setattr(
            quiz,
            field,
            value,
        )

    db.commit()
    db.refresh(quiz)

    return quiz


# ==========================================
# Delete Quiz
# ==========================================

def delete_quiz(
    db: Session,
    quiz_id: UUID,
):
    quiz = get_quiz_by_id(
        db,
        quiz_id,
    )

    db.delete(quiz)
    db.commit()

    return {
        "message": "Quiz deleted successfully",
        "quiz_id": str(quiz_id),
    }


# ==========================================
# Get Quizzes By Course
# ==========================================

def get_quizzes_by_course(
    db: Session,
    course_id: UUID,
):
    # Check course exists
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return (
        db.query(Quiz)
        .filter(
            Quiz.course_id == course_id
        )
        .order_by(Quiz.created_at.desc())
        .all()
    )


# ==========================================
# Create Quiz Under Course
# ==========================================

def create_quiz_under_course(
    db: Session,
    course_id: UUID,
    quiz_data: QuizCreate,
):
    # Check course exists
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Check lesson if provided
    if quiz_data.lessons_id is not None:

        lesson = db.query(Lesson).filter(
            Lesson.id == quiz_data.lessons_id
        ).first()

        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

    # Validate pass marks
    if (
        quiz_data.pass_marks is not None
        and quiz_data.total_marks is not None
        and quiz_data.pass_marks > quiz_data.total_marks
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pass marks cannot be greater than total marks",
        )

    # Create quiz
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        course_id=course_id,
        lessons_id=quiz_data.lessons_id,
        total_marks=quiz_data.total_marks,
        pass_marks=quiz_data.pass_marks,
        duration=quiz_data.duration,
        is_active=quiz_data.is_active,
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


# ==========================================
# Activate Quiz
# ==========================================

def activate_quiz(
    db: Session,
    quiz_id: UUID,
):
    quiz = get_quiz_by_id(
        db,
        quiz_id,
    )

    quiz.is_active = True

    db.commit()
    db.refresh(quiz)

    return quiz


# ==========================================
# Deactivate Quiz
# ==========================================

def deactivate_quiz(
    db: Session,
    quiz_id: UUID,
):
    quiz = get_quiz_by_id(
        db,
        quiz_id,
    )

    quiz.is_active = False

    db.commit()
    db.refresh(quiz)

    return quiz