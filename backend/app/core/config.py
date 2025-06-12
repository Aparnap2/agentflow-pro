from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "AgentFlow Pro"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database (Aiven PostgreSQL)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None
    
    # LLM Providers
    OPENROUTER_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Qdrant Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "documents"
    QDRANT_DISTANCE_METRIC: str = "COSINE"  # COSINE, EUCLID, or DOT
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TOKEN: Optional[str] = None
    REDIS_TTL: int = 86400  # 24 hours in seconds
    
    # Crawl4AI
    CRAWL4AI_HEADLESS: bool = True
    CRAWL4AI_TIMEOUT: int = 30000  # 30 seconds
    CRAWL4AI_MAX_RETRIES: int = 3
    
    # Embedding Model (Gemini)
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    EMBEDDING_DIM: int = 768  # Dimension of Gemini's embedding vector
    
    # Langfuse Monitoring
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Update database URL if not set
if not settings.DATABASE_URL:
    settings.DATABASE_URL = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
