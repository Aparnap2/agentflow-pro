"""API endpoints for managing crews."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer

from app.services.crew_service import get_crew_service
from app.api.schemas.crew import (
    CrewCreate, CrewResponse, CrewListResponse, CrewUpdate,
    CrewExecutionRequest, CrewExecutionResponse, CrewStatsResponse,
    CrewMember, CrewMemberRole
)
from app.core.security import get_current_user

router = APIRouter(
    prefix="/crews",
    tags=["crews"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=CrewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new crew"
)
async def create_crew(
    crew_data: CrewCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new crew with the given configuration.
    
    - **name**: Name of the crew (must be unique)
    - **description**: Optional description of the crew
    - **members**: List of agent members with their roles
    - **workflow_id**: Optional ID of the workflow this crew will execute
    - **config**: Additional configuration for the crew
    - **is_active**: Whether the crew is active (default: true)
    - **tags**: Optional list of tags for categorization
    - **metadata**: Additional metadata for the crew
    """
    try:
        crew_service = get_crew_service()
        return await crew_service.create_crew(crew_data, current_user["sub"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create crew: {str(e)}"
        )

@router.get(
    "/{crew_id}",
    response_model=CrewResponse,
    summary="Get a crew by ID"
)
async def get_crew(
    crew_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a crew by its ID.
    
    - **crew_id**: The ID of the crew to retrieve
    """
    try:
        crew_service = get_crew_service()
        return await crew_service.get_crew(crew_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get crew: {str(e)}"
        )

@router.get(
    "/",
    response_model=CrewListResponse,
    summary="List crews"
)
async def list_crews(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    current_user: dict = Depends(get_current_user)
):
    """
    List all crews with optional filtering and pagination.
    
    - **page**: Page number (1-based)
    - **size**: Number of items per page (1-100)
    - **name**: Filter by name (case-insensitive contains)
    - **is_active**: Filter by active status
    - **tags**: Filter by tags (OR condition)
    """
    try:
        crew_service = get_crew_service()
        return await crew_service.list_crews(
            page=page,
            size=size,
            name=name,
            is_active=is_active,
            tags=tags
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list crews: {str(e)}"
        )

@router.put(
    "/{crew_id}",
    response_model=CrewResponse,
    summary="Update a crew"
)
async def update_crew(
    crew_id: str,
    crew_data: CrewUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing crew.
    
    - **crew_id**: The ID of the crew to update
    - **name**: New name for the crew (optional)
    - **description**: New description (optional)
    - **is_active**: New active status (optional)
    - **config**: Updated configuration (optional, merges with existing)
    - **metadata**: Updated metadata (optional, merges with existing)
    - **tags**: Updated list of tags (optional, replaces existing)
    """
    try:
        crew_service = get_crew_service()
        return await crew_service.update_crew(crew_id, crew_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update crew: {str(e)}"
        )

@router.delete(
    "/{crew_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a crew"
)
async def delete_crew(
    crew_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a crew by ID.
    
    - **crew_id**: The ID of the crew to delete
    """
    try:
        crew_service = get_crew_service()
        success = await crew_service.delete_crew(crew_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete crew"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete crew: {str(e)}"
        )

@router.post(
    "/{crew_id}/execute",
    response_model=CrewExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute a crew"
)
async def execute_crew(
    crew_id: str,
    execution_data: CrewExecutionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a crew with the given input data.
    
    - **crew_id**: The ID of the crew to execute
    - **input_data**: Input data for the execution
    - **context**: Additional context for the execution
    - **stream**: Whether to stream the execution results (not yet implemented)
    
    Returns an execution ID that can be used to track the execution status.
    """
    try:
        crew_service = get_crew_service()
        return await crew_service.execute_crew(
            crew_id=crew_id,
            execution_data=execution_data,
            user_id=current_user["sub"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute crew: {str(e)}"
        )

@router.get(
    "/{crew_id}/stats",
    response_model=CrewStatsResponse,
    summary="Get crew statistics"
)
async def get_crew_stats(
    crew_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics for a crew.
    
    - **crew_id**: The ID of the crew to get statistics for
    
    Returns execution statistics including success rate, average execution time,
    and member performance metrics.
    """
    try:
        crew_service = get_crew_service()
        return await crew_service.get_crew_stats(crew_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get crew stats: {str(e)}"
        )

@router.post(
    "/{crew_id}/members",
    response_model=CrewResponse,
    summary="Add a member to a crew"
)
async def add_crew_member(
    crew_id: str,
    member: CrewMember,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a member to a crew.
    
    - **crew_id**: The ID of the crew
    - **agent_id**: The ID of the agent to add
    - **role**: The role of the member in the crew
    - **permissions**: List of permissions for the member
    """
    try:
        crew_service = get_crew_service()
        # This is a simplified implementation - in a real app, you'd update the crew's members
        # and create the appropriate relationships
        crew = await crew_service.get_crew(crew_id)
        return crew
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add member to crew: {str(e)}"
        )

@router.delete(
    "/{crew_id}/members/{agent_id}",
    response_model=CrewResponse,
    summary="Remove a member from a crew"
)
async def remove_crew_member(
    crew_id: str,
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a member from a crew.
    
    - **crew_id**: The ID of the crew
    - **agent_id**: The ID of the agent to remove
    """
    try:
        crew_service = get_crew_service()
        # This is a simplified implementation - in a real app, you'd update the crew's members
        # and remove the appropriate relationships
        crew = await crew_service.get_crew(crew_id)
        return crew
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member from crew: {str(e)}"
        )
