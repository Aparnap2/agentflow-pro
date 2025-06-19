import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional

# Import configurations and services
from .core.config import settings
from .db.database import DatabaseService
from .services.redis_service import RedisService
from .services.auth_service import AuthService, security

# Import routers
from .api import auth, tasks, agents, billing, health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
db = DatabaseService(settings.POSTGRES_URL)
redis_service = RedisService()
auth_service = AuthService(db=db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup event
    logger.info("Starting up...")
    
    try:
        # Initialize database connection
        await db.initialize()
        logger.info("Database initialized")
        
        # Add any other initialization here
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    finally:
        # Shutdown event
        logger.info("Shutting down...")
        # Cleanup resources if needed

# Create FastAPI app
app = FastAPI(
    title="AgentFlow Pro API",
    description="Backend API for AgentFlow Pro - AI Agent Orchestration Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(health.router, prefix="/health", tags=["Health"])

# Middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Dependency overrides for testing
def get_db():
    return db

def get_redis():
    return redis_service

def get_auth_service():
    return auth_service

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "status": "ok",
        "service": "AgentFlow Pro API",
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# This allows running with uvicorn directly: `uvicorn app.main:app`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
