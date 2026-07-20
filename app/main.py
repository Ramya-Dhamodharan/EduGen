from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Allow the React (Vite) dev server to call this API.
# Tighten allow_origins before deploying to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API is running"}


# --- Routers ---
from app.routes.role_routes import router as role_router
from app.routes.user_routes import router as user_router

app.include_router(role_router, prefix="/api/roles", tags=["Roles"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])

# As you build each remaining resource, wire its router in here the same way, e.g.:
#
# from app.routes.auth_routes import router as auth_router
# app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
