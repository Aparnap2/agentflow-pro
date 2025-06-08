from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from typing import List

from .core.config import settings
from .api import api_router  # Updated import

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AgentFlow Pro API...")
    
    # Initialize services here
    from .services.ai.orchestrator import AIOrchestrator
    app.state.ai_orchestrator = AIOrchestrator()
    logger.info("AI Orchestrator initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AgentFlow Pro API...")

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
    return {
        "status": "healthy",
        "version": app.version,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
