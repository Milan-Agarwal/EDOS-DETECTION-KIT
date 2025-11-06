"""
Configuration settings for the EDoS Security Dashboard
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "EDoS Security Dashboard"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "edos-security-dashboard-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./edos_security.db"

    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # WebSocket
    WS_MAX_CONNECTIONS: int = 100

    # Data Generation
    GENERATE_SAMPLE_DATA: bool = True
    DATA_GENERATION_INTERVAL: int = 3  # seconds

    class Config:
        env_file = ".env"


settings = Settings()
