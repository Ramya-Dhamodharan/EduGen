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

# As you build each remaining resource, wire its router in here the same way, e.g.:
#
# from app.routes.auth_routes import router as auth_router
# app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#quiz answer
from app.routes.quiz_answer_routes import router as quiz_answer_router

from app.models import quiz
from app.models import quiz_attempt
from app.models import quiz_question
from app.models import quiz_answer

app.include_router(
    quiz_answer_router,
    tags=["Quiz Answers"]
)
#-------------------------------------------------------------------------------
#-----------------------------certificates-------------------------------------------
from app.routes.certificate_routes import router as certificate_router
app.include_router(
    certificate_router,
    tags=["Certificates"]
)
#-----------------------------------------------------------------------------------
#-----------------------------course_review-----------------------------------------
from app.routes.course_review_routes import router as course_review_router
app.include_router(course_review_router)
#-----------------------------------------------------------------------------------
#------------------------------Payments---------------------------------------------
from app.routes.payment_routes import router as payment_router
app.include_router(payment_router)
# --- Routers ---
from app.routes.role_routes import router as role_router
from app.routes.user_routes import router as user_router
from app.routes.category_routes import router as category_router
from app.routes.course_routes import router as course_router
from app.routes.module_routes import router as module_router
from app.routes.lesson_routes import router as lesson_router

app.include_router(role_router, prefix="/api/roles", tags=["Roles"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(course_router, prefix="/api/courses", tags=["Courses"])
app.include_router(module_router, prefix="/api/modules", tags=["Modules"])
app.include_router(lesson_router, prefix="/api/lessons", tags=["Lessons"])

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
