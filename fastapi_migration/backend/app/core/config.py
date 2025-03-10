import os
from pathlib import Path
from datetime import timedelta
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Zando Genomic Analysis"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "zando")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str) and v:
            return v
        
        return (
            f"postgresql+asyncpg://"
            f"{values.data.get('POSTGRES_USER')}:"
            f"{values.data.get('POSTGRES_PASSWORD')}@"
            f"{values.data.get('POSTGRES_SERVER')}:"
            f"{values.data.get('POSTGRES_PORT')}/"
            f"{values.data.get('POSTGRES_DB')}"
        )
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ALGORITHM: str = "HS256"
    
    # File storage settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", BASE_DIR / "cache"))
    REPORTS_DIR: Path = Path(os.getenv("REPORTS_DIR", BASE_DIR / "reports"))
    UPLOADS_DIR: Path = Path(os.getenv("UPLOADS_DIR", BASE_DIR / "uploads"))
    UPLOADS_CACHE_DIR: Path = Path(os.getenv("UPLOADS_CACHE_DIR", CACHE_DIR / "uploads"))
    CACHE_EXPIRY: timedelta = timedelta(days=int(os.getenv("CACHE_EXPIRY_DAYS", "7")))
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.CACHE_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_CACHE_DIR, exist_ok=True)