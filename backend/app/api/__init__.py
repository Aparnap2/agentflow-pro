from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

# Import and include all endpoint routers
from .v1.endpoints import agents as agents_router

# Include versioned routers
api_router.include_router(agents_router.router, prefix="/v1")
