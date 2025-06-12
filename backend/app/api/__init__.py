from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

# Import and include all endpoint routers
from .endpoints import agents as agents_endpoints
from .endpoints import rag as rag_endpoints
from .endpoints import crews as crews_endpoints
from .endpoints import workflows as workflows_endpoints

# Include routers with versioning
api_router.include_router(agents_endpoints.router, prefix="/v1/agents", tags=["agents"])
api_router.include_router(rag_endpoints.router, prefix="/v1/rag", tags=["RAG"])
api_router.include_router(crews_endpoints.router, prefix="/v1/crews", tags=["crews"])
api_router.include_router(workflows_endpoints.router, prefix="/v1/workflows", tags=["workflows"])
