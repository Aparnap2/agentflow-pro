"""API endpoints for agent management."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from app.services.agent_service import get_agent_service, AgentService
from app.api.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse,
    ProcessTaskRequest, ProcessTaskResponse, AgentStatsResponse, AgentType
)

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
    description="Create a new agent with the given configuration."
)
async def create_agent(
    agent_data: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Create a new agent."""
    return await agent_service.create_agent(agent_data)

@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get agent by ID",
    description="Get detailed information about a specific agent."
)
async def get_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Get an agent by ID."""
    return await agent_service.get_agent(agent_id)

@router.get(
    "/",
    response_model=AgentListResponse,
    summary="List agents",
    description="List all agents with optional filtering and pagination."
)
async def list_agents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    agent_type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentListResponse:
    """List agents with optional filtering and pagination."""
    return await agent_service.list_agents(
        page=page,
        size=size,
        agent_type=agent_type.value if agent_type else None,
        is_active=is_active,
        tags=tags
    )

@router.put(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Update an agent",
    description="Update an existing agent's configuration."
)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponse:
    """Update an existing agent."""
    return await agent_service.update_agent(agent_id, agent_data)

@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
    description="Delete an agent by ID.",
    responses={
        204: {"description": "Agent deleted successfully"},
        404: {"description": "Agent not found"}
    }
)
async def delete_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> None:
    """Delete an agent by ID."""
    await agent_service.delete_agent(agent_id)
    return None

@router.post(
    "/{agent_id}/process",
    response_model=ProcessTaskResponse,
    summary="Process a task with an agent",
    description="Process a task using the specified agent.",
    responses={
        200: {"description": "Task processed successfully"},
        404: {"description": "Agent not found"},
        422: {"description": "Validation error"}
    }
)
async def process_task(
    agent_id: str,
    task_data: ProcessTaskRequest,
    agent_service: AgentService = Depends(get_agent_service)
) -> ProcessTaskResponse:
    """Process a task with the specified agent."""
    return await agent_service.process_task(agent_id, task_data)

@router.get(
    "/{agent_id}/stats",
    response_model=AgentStatsResponse,
    summary="Get agent statistics",
    description="Get statistics and metrics for an agent.",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        404: {"description": "Agent not found"}
    }
)
async def get_agent_stats(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service)
) -> AgentStatsResponse:
    """Get statistics for an agent."""
    return await agent_service.get_agent_stats(agent_id)
