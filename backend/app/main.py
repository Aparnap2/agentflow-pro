from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from typing import List
import asyncio

from .core.config import settings
from .api import api_router
from .db.config import init_db, close_db
from .db.repository import get_repository

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AgentFlow Pro API...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        
        # Test database connection
        repo = get_repository()
        with repo.driver.session() as session:
            result = session.run("RETURN 'Neo4j connection successful' AS message")
            logger.info(f"✓ {result.single()['message']}")
        
        # Initialize AI services
        from .services.ai.orchestrator import AIOrchestrator
        app.state.ai_orchestrator = AIOrchestrator()
        logger.info("✓ AI Orchestrator initialized")
        
        logger.info("✓ AgentFlow Pro API is ready")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start AgentFlow Pro API: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AgentFlow Pro API...")
        await close_db()
        logger.info("✓ Database connections closed")

app = FastAPI(
    title="AgentFlow Pro API",
    description="Backend API for AgentFlow Pro - AI Agent Automation Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint for the application."""
    try:
        # Test database connection
        repo = get_repository()
        with repo.driver.session() as session:
            session.run("RETURN 1")
        
        return {
            "status": "healthy",
            "version": app.version,
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "version": app.version,
                "error": str(e),
                "environment": settings.ENVIRONMENT
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
