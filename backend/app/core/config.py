from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central place for all environment-driven configuration.
    Values are loaded from the .env file at project root.
    """
    APP_NAME: str = "EduGen"
    DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SMTP (optional). If host+user+password are set, password-reset OTPs
    # are emailed; otherwise they are printed to the terminal (dev mode).
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_USE_TLS: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
