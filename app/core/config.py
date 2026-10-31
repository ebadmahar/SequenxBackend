import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CANONICAL_DB_PATH = (BASE_DIR / "app.db").as_posix()

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        PROJECT_NAME: str = "Business Portal API"
        PROJECT_DESCRIPTION: str = (
            "FastAPI Backend for Blog, Careers, Applications, and Contact Management"
        )
        PROJECT_VERSION: str = "1.0.0"
        ENVIRONMENT: str = "development"
        DEBUG: bool = True

        # Database
        DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{CANONICAL_DB_PATH}")

        # Security & JWT
        SECRET_KEY: str = "development-secret-key-change-this-in-production-long-random-string"
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

        # Initial Admin Seed
        FIRST_ADMIN_NAME: str = "Super Administrator"
        FIRST_ADMIN_EMAIL: str = "admin@example.com"
        FIRST_ADMIN_PASSWORD: str = "AdminPassword123!"

        # Fallback HR Notification Email
        HR_EMAIL: str = ""

        # SMTP Email Configuration
        SMTP_HOST: str = ""
        SMTP_PORT: int = 587
        SMTP_USER: str = ""
        SMTP_PASSWORD: str = ""
        SMTP_FROM_EMAIL: str = ""
        SMTP_FROM_NAME: str = "SeQuenX"
        SMTP_TLS: bool = True

        # Upload Directories & Limits
        UPLOAD_DIR: str = "uploads"
        MAX_CV_SIZE_MB: int = 5
        MAX_IMAGE_SIZE_MB: int = 3

        # CORS Origins (comma separated)
        CORS_ORIGINS: str = (
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8000,"
            "https://sequenxx.ebadmahar.site,https://hisequenx.onrender.com"
        )

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
            case_sensitive=False,
        )

        @property
        def cors_origins_list(self) -> List[str]:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

except ImportError:
    from pydantic import BaseModel

    class Settings(BaseModel):
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Business Portal API")
        PROJECT_DESCRIPTION: str = os.getenv(
            "PROJECT_DESCRIPTION",
            "FastAPI Backend for Blog, Careers, Applications, and Contact Management",
        )
        PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

        SECRET_KEY: str = os.getenv(
            "SECRET_KEY", "development-secret-key-change-this-in-production-long-random-string"
        )
        ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        FIRST_ADMIN_NAME: str = os.getenv("FIRST_ADMIN_NAME", "Super Administrator")
        FIRST_ADMIN_EMAIL: str = os.getenv("FIRST_ADMIN_EMAIL", "admin@example.com")
        FIRST_ADMIN_PASSWORD: str = os.getenv("FIRST_ADMIN_PASSWORD", "AdminPassword123!")

        HR_EMAIL: str = os.getenv("HR_EMAIL", "")

        SMTP_HOST: str = os.getenv("SMTP_HOST", "")
        SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
        SMTP_USER: str = os.getenv("SMTP_USER", "")
        SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
        SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
        SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "SeQuenX")
        SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() in ("true", "1", "yes")

        UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
        MAX_CV_SIZE_MB: int = int(os.getenv("MAX_CV_SIZE_MB", "5"))
        MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "3"))

        CORS_ORIGINS: str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8000,"
            "https://sequenxx.ebadmahar.site,https://hisequenx.onrender.com",
        )

        @property
        def cors_origins_list(self) -> List[str]:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()

