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


    # Cloud
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    INSTANCE_CONNECTION_NAME: str = os.getenv("INSTANCE_CONNECTION_NAME", "")

    # File storage setting
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

