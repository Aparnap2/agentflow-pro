import os
from enum import Enum
from pydantic import BaseModel

class PlanType(str, Enum):
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")
    
    # Database connections
    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost/agentflow")
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
    
    # Stripe Configuration
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_...")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24
    
    # Rate Limiting per plan (per day)
    STARTER_PLAN_API_CALLS = 1000
    STARTER_PLAN_LLM_TOKENS = 100000
    PRO_PLAN_API_CALLS = 10000
    PRO_PLAN_LLM_TOKENS = 1000000
    ENTERPRISE_PLAN_API_CALLS = 100000
    ENTERPRISE_PLAN_LLM_TOKENS = 10000000
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)

settings = Settings()
