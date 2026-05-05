import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "NeuroPlan AI"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str  # Mandatory in prod
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "neuroplan"
    DATABASE_URL: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # AI Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Custom/Fine-tuned AI Settings
    CUSTOM_AI_URL: Optional[str] = "http://localhost:11434/v1" # Standard Ollama port
    CUSTOM_AI_MODEL: Optional[str] = "neuroplan"
    USE_CUSTOM_AI: bool = False
    
    CUSTOM_AI_GUIDED_JSON: bool = True
    AI_CACHE_TTL: int = 3600
    AI_MAX_RETRIES: int = 3

    # ML & RAG Settings
    CHROMADB_PATH: str = "./data/chromadb"
    DKT_MODEL_PATH: str = "./ml/models/dkt_checkpoint.pt"
    DKT_ENABLED: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
