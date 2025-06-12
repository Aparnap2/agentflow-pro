"""API endpoints for managing workflows."""
from datetime import datetime, timezone
import logging
from typing import List, Optional

# Set up logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer

from app.services.workflow_service import get_workflow_service
from app.db.models import Relationship, RelationshipType
from app.api.schemas.workflow import (
    WorkflowCreate, WorkflowResponse, WorkflowListResponse, WorkflowUpdate,
    WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowStatsResponse,
    TaskCreate, TaskResponse, WorkflowStatus
)
from app.core.security import get_current_user

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    dependencies=[Depends(get_current_user)]
)

@router.post(
    "/",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workflow"
)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new workflow with the given configuration.
    
    - **name**: Name of the workflow (must be unique)
    - **description**: Optional description of the workflow
    - **status**: Initial status of the workflow (draft, active, archived, paused)
    - **is_template**: Whether this is a template workflow
    - **tags**: Optional list of tags for categorization
    - **config**: Additional configuration for the workflow
    - **tasks**: List of tasks in the workflow
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.create_workflow(workflow_data, current_user["sub"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )

@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get a workflow by ID"
)
async def get_workflow(
    workflow_id: str,
    include_tasks: bool = Query(True, description="Whether to include tasks in the response"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a workflow by its ID.
    
    - **workflow_id**: The ID of the workflow to retrieve
    - **include_tasks**: Whether to include the workflow's tasks in the response
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.get_workflow(workflow_id, include_tasks=include_tasks)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}"
        )

@router.get(
    "/",
    response_model=WorkflowListResponse,
    summary="List workflows"
)
async def list_workflows(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by name"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by status"),
    is_template: Optional[bool] = Query(None, description="Filter by template status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    current_user: dict = Depends(get_current_user)
):
    """
    List all workflows with optional filtering and pagination.
    
    - **page**: Page number (1-based)
    - **size**: Number of items per page (1-100)
    - **name**: Filter by name (case-insensitive contains)
    - **status**: Filter by status
    - **is_template**: Filter by template status
    - **tags**: Filter by tags (OR condition)
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.list_workflows(
            page=page,
            size=size,
            name=name,
            status=status,
            is_template=is_template,
            tags=tags
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )

@router.put(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Update a workflow"
)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing workflow.
    
    - **workflow_id**: The ID of the workflow to update
    - **name**: New name for the workflow (optional)
    - **description**: New description (optional)
    - **status**: New status (optional)
    - **is_template**: Whether this is a template workflow (optional)
    - **config**: Updated configuration (optional, merges with existing)
    - **metadata**: Updated metadata (optional, merges with existing)
    - **tags**: Updated list of tags (optional, replaces existing)
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.update_workflow(workflow_id, workflow_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )

@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workflow"
)
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a workflow by ID.
    
    - **workflow_id**: The ID of the workflow to delete
    
    Note: Cannot delete a workflow that is in use by any crews.
    """
    try:
        workflow_service = get_workflow_service()
        success = await workflow_service.delete_workflow(workflow_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete workflow"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workflow: {str(e)}"
        )

@router.post(
    "/{workflow_id}/execute",
    response_model=WorkflowExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute a workflow"
)
async def execute_workflow(
    workflow_id: str,
    execution_data: WorkflowExecutionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a workflow with the given input data.
    
    - **workflow_id**: The ID of the workflow to execute
    - **input_data**: Input data for the execution
    - **context**: Additional context for the execution
    - **start_task_id**: Optional ID of the task to start execution from
    - **override_config**: Optional configuration overrides for the execution
    
    Returns an execution ID that can be used to track the execution status.
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.execute_workflow(
            workflow_id=workflow_id,
            execution_data=execution_data,
            user_id=current_user["sub"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )

@router.get(
    "/{workflow_id}/stats",
    response_model=WorkflowStatsResponse,
    summary="Get workflow statistics"
)
async def get_workflow_stats(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics for a workflow.
    
    - **workflow_id**: The ID of the workflow to get statistics for
    
    Returns execution statistics including success rate, average execution time,
    and task performance metrics.
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.get_workflow_stats(workflow_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow stats: {str(e)}"
        )

@router.post(
    "/{workflow_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a task to a workflow"
)
async def create_task(
    workflow_id: str,
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new task to a workflow.
    
    - **workflow_id**: The ID of the workflow to add the task to
    - **name**: Name of the task
    - **description**: Optional description of the task
    - **config**: Configuration for the task
    - **dependencies**: List of task dependencies
    """
    try:
        workflow_service = get_workflow_service()
        return await workflow_service.create_task(workflow_id, task_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.get(
    "/{workflow_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID"
)
async def get_task(
    workflow_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a task by its ID within a workflow.
    
    - **workflow_id**: The ID of the workflow
    - **task_id**: The ID of the task to retrieve
    """
    try:
        workflow_service = get_workflow_service()
        # In a real implementation, you'd have a get_task method in the service
        workflow = await workflow_service.get_workflow(workflow_id, include_tasks=True)
        task = next((t for t in workflow.tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found in workflow {workflow_id}"
            )
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )

@router.delete(
    "/{workflow_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task from a workflow"
)
async def delete_task(
    workflow_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a task from a workflow.
    
    - **workflow_id**: The ID of the workflow
    - **task_id**: The ID of the task to delete
    
    Note: Cannot delete a task that is a dependency for other tasks.
    """
    try:
        # In a real implementation, you'd have a delete_task method in the service
        # that would handle the deletion and dependency checks
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Task deletion is not yet implemented"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )

@router.get(
    "/executions/{execution_id}",
    response_model=WorkflowExecutionResponse,
    summary="Get workflow execution status"
)
async def get_workflow_execution(
    execution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the status of a workflow execution.
    
    - **execution_id**: The ID of the execution to retrieve
    
    Returns the current status, result (if completed), and any errors.
    """
    try:
        # In a real implementation, you'd have a get_execution method in the service
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Execution status retrieval is not yet implemented"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution status: {str(e)}"
        )

@router.post(
    "/templates/{template_id}/instantiate",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow from a template"
)
async def instantiate_workflow_template(
    template_id: str,
    name: str = Body(..., embed=True, description="Name for the new workflow"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new workflow from a template.
    
    - **template_id**: The ID of the template to instantiate
    - **name**: Name for the new workflow
    
    Creates a copy of the template workflow with the given name.
    """
    try:
        workflow_service = get_workflow_service()
        # In a real implementation, you'd have an instantiate_template method
        # that would create a copy of the template with the given name
        template = await workflow_service.get_workflow(template_id)
        if not template.is_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workflow {template_id} is not a template"
            )
        
        # Get the template tasks to include in the new workflow
        template_tasks = []
        if hasattr(template, 'tasks') and template.tasks:
            for task in template.tasks:
                # Convert task response back to create model
                task_create = TaskCreate(
                    name=task.name,
                    description=task.description,
                    config=TaskConfig(
                        task_type=TaskType(task.config.task_type),
                        assignee=task.config.assignee,
                        due_date=task.config.due_date,
                        priority=task.config.priority,
                        retry_count=task.config.retry_count,
                        timeout=task.config.timeout,
                        input_schema=task.config.input_schema,
                        output_schema=task.config.output_schema,
                        metadata=task.config.metadata
                    ),
                    dependencies=task.dependencies if hasattr(task, 'dependencies') else []
                )
                template_tasks.append(task_create)
        
        # Create a new workflow based on the template
        workflow_data = WorkflowCreate(
            name=name,
            description=f"Created from template: {template.name}\n\n{template.description}",
            status=WorkflowStatus.DRAFT,  # New workflows start as drafts
            is_template=False,  # The copy is not a template
            tags=template.tags + ["template_instantiated"],  # Add a tag to indicate this was created from a template
            config=template.config,
            tasks=template_tasks  # Include all tasks from the template
        )
        
        # Create the new workflow
        new_workflow = await workflow_service.create_workflow(workflow_data, current_user["sub"])
        
        # Add a relationship to track the template this was created from
        try:
            # Create a relationship between the new workflow and the template
            relationship = Relationship(
                source_id=new_workflow.id,
                target_id=template_id,
                type=RelationshipType.CREATED_FROM,
                properties={
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": current_user["sub"]
                }
            )
            await workflow_service.repo.create_relationship(relationship)
        except Exception as rel_error:
            logger.warning(f"Failed to create template relationship: {rel_error}")
            # Don't fail the whole operation if relationship creation fails
            
        return new_workflow
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to instantiate template: {str(e)}"
        )
