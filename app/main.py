from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.routes.auth_routes import router as auth_router
from app.routes.role_routes import router as role_router
from app.routes.user_routes import router as user_router

from app.routes.quiz_routes import router as quiz_router
from app.routes.quiz_question_routes import router as quiz_question_router
from app.routes.quiz_attempt_routes import router as quiz_attempt_router


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


# ==================================================
# AUTH ROUTES
# ==================================================

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Auth"],
)


# ==================================================
# ROLE ROUTES
# ==================================================

app.include_router(
    role_router,
    prefix="/api/roles",
    tags=["Roles"],
)


# ==================================================
# USER ROUTES
# ==================================================

app.include_router(
    user_router,
    prefix="/api/users",
    tags=["Users"],
)


# ==================================================
# QUIZ ROUTES
# ==================================================

app.include_router(
    quiz_router,
    prefix="/api/quizzes",
    tags=["Quizzes"],
)


# ==================================================
# QUIZ QUESTION ROUTES
# ==================================================

app.include_router(
    quiz_question_router,
    prefix="/api/quiz-questions",
    tags=["Quiz Questions"],
)


# ==================================================
# QUIZ ATTEMPT ROUTES
# ==================================================

app.include_router(
    quiz_attempt_router,
    prefix="/api/quiz-attempts",
    tags=["Quiz Attempts"],
)