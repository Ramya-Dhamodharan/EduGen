from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
# Import all models so SQLAlchemy registers every mapper at startup
# (fixes 'failed to locate a name' for string-based relationships).
import app.models  # noqa: F401


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)


# ==================================================
# CORS CONFIGURATION
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {
        "message": f"{settings.APP_NAME} API is running"
    }


# --- Routers ---
from app.routes.auth_routes import router as auth_router
from app.routes.role_routes import router as role_router
from app.routes.user_routes import router as user_router
from app.routes.category_routes import router as category_router
from app.routes.course_routes import router as course_router
from app.routes.module_routes import router as module_router
from app.routes.lesson_routes import router as lesson_router
from app.routes.enrollment_routes import router as enrollment_router
from app.routes.quiz_routes import router as quiz_router
from app.routes.quiz_question_routes import router as quiz_question_router
from app.routes.quiz_attempt_routes import router as quiz_attempt_router
from app.routes.quiz_answer_routes import router as quiz_answer_router
from app.routes.certificate_routes import router as certificate_router
from app.routes.course_review_routes import router as course_review_router
from app.routes.payment_routes import router as payment_router
from app.routes.student_routes import router as student_router

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(role_router, prefix="/api/roles", tags=["Roles"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(course_router, prefix="/api/courses", tags=["Courses"])
app.include_router(module_router, prefix="/api/modules", tags=["Modules"])
app.include_router(lesson_router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(enrollment_router, prefix="/api/enrollments", tags=["Enrollments"])
app.include_router(quiz_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(quiz_question_router, prefix="/api/quiz-questions", tags=["Quiz Questions"])
app.include_router(quiz_attempt_router, prefix="/api/quiz-attempts", tags=["Quiz Attempts"])
app.include_router(quiz_answer_router, prefix="/api/quiz-answers", tags=["Quiz Answers"])
app.include_router(certificate_router, prefix="/api/certificates", tags=["Certificates"])
app.include_router(course_review_router, prefix="/api/course-reviews", tags=["Course Reviews"])
app.include_router(payment_router, prefix="/api/payments", tags=["Payments"])
app.include_router(student_router, prefix="/api/students", tags=["Students"])