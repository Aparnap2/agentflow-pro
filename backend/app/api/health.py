from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncpg
import redis.asyncio as redis
import logging

from ..core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {}
    }
    
    # Check database connection
    try:
        conn = await asyncpg.connect(settings.POSTGRES_URL)
        await conn.execute("SELECT 1")
        status["services"]["database"] = "ok"
        await conn.close()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        status["status"] = "degraded"
        status["services"]["database"] = "error"
    
    # Check Redis connection
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        status["services"]["redis"] = "ok"
        await r.close()
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        status["status"] = "degraded"
        status["services"]["redis"] = "error"
    
    # Check if any critical services are down
    if any(v == "error" for v in status["services"].values()):
        status["status"] = "unhealthy"
    
    return status

@router.get("/ready")
async def readiness_probe() -> Dict[str, str]:
    """Kubernetes readiness probe"""
    try:
        # Check database
        conn = await asyncpg.connect(settings.POSTGRES_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        
        # Check Redis
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service Unavailable")

@router.get("/startup")
async def startup_probe() -> Dict[str, str]:
    """Kubernetes startup probe"""
    try:
        # Check database
        conn = await asyncpg.connect(settings.POSTGRES_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        
        return {"status": "started"}
    except Exception as e:
        logger.error(f"Startup probe failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service Starting...")
