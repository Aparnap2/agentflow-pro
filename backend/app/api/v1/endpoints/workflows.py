"""
API endpoints for managing and executing agent workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import json
import logging
import uuid

from pydantic import BaseModel, Field

from app.ai.workflow.agent_workflow import AgentWorkflow, AgentWorkflowStep, AgentWorkflowStepType
from app.ai.agents.agent_factory import agent_factory

router = APIRouter(prefix="/workflows", tags=["workflows"])
logger = logging.getLogger(__name__)

# In-memory store for workflows (in production, use a database)
workflow_registry: Dict[str, AgentWorkflow] = {}

class WorkflowStepCreate(BaseModel):
    """Model for creating a workflow step."""
    step_id: str
    name: str
    step_type: AgentWorkflowStepType
    agent_type: Optional[str] = None
    task: Optional[str] = None
    input_template: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[float] = None

class WorkflowCreate(BaseModel):
    """Model for creating a workflow."""
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStepCreate]

class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    workflow_id: str
    name: str
    status: str
    created_at: str
    updated_at: str
    steps: List[Dict[str, Any]]

class ExecuteWorkflowRequest(BaseModel):
    """Request model for executing a workflow."""
    input_data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = False

class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution."""
    execution_id: str
    workflow_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

# In-memory store for workflow executions (in production, use a database)
workflow_executions: Dict[str, Dict[str, Any]] = {}

@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow_data: WorkflowCreate):
    """
    Create a new workflow with the given configuration.
    """
    try:
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        
        # Create a new workflow
        workflow = AgentWorkflow(
            workflow_id=workflow_id,
            name=workflow_data.name,
            agent_factory=agent_factory
        )
        
        # Add steps to the workflow
        for step_data in workflow_data.steps:
            step = AgentWorkflowStep(**step_data.dict())
            workflow.add_step(step)
        
        # Validate the workflow
        workflow.validate()
        
        # Store the workflow
        workflow_registry[workflow_id] = workflow
        
        # Prepare response
        return {
            "workflow_id": workflow_id,
            "name": workflow_data.name,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "step_type": step.step_type.value,
                    "agent_type": step.agent_type,
                    "depends_on": step.depends_on
                }
                for step in workflow_data.steps
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create workflow: {str(e)}"
        )

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """
    Get details of a specific workflow.
    """
    if workflow_id not in workflow_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID {workflow_id} not found"
        )
    
    workflow = workflow_registry[workflow_id]
    
    return {
        "workflow_id": workflow_id,
        "name": workflow.name,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "steps": [
            {
                "step_id": step.step_id,
                "name": step.name,
                "step_type": step.step_type.value,
                "agent_type": step.agent_type,
                "depends_on": step.depends_on
            }
            for step in workflow.steps.values()
        ]
    }

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a workflow with the given input data.
    
    If async_execution is True, the workflow will be executed in the background.
    """
    if workflow_id not in workflow_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID {workflow_id} not found"
        )
    
    workflow = workflow_registry[workflow_id]
    execution_id = f"exec_{uuid.uuid4().hex[:8]}"
    
    # Initialize execution record
    execution_record = {
        "execution_id": execution_id,
        "workflow_id": workflow_id,
        "status": "pending",
        "start_time": datetime.utcnow().isoformat(),
        "input_data": request.input_data,
        "context": request.context,
        "result": None,
        "error": None
    }
    
    workflow_executions[execution_id] = execution_record
    
    async def _execute_workflow():
        """Execute the workflow and update the execution record."""
        try:
            execution_record["status"] = "running"
            
            # Execute the workflow
            result = await workflow.execute(
                input_data=request.input_data,
                context=request.context
            )
            
            # Update execution record
            execution_record.update({
                "status": "completed" if result.success else "failed",
                "end_time": datetime.utcnow().isoformat(),
                "result": result.dict(),
                "execution_time_ms": result.execution_time_ms
            })
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            execution_record.update({
                "status": "failed",
                "end_time": datetime.utcnow().isoformat(),
                "error": str(e)
            })
    
    if request.async_execution:
        # Run in background
        background_tasks.add_task(_execute_workflow)
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "started",
            "result": None
        }
    else:
        # Run synchronously
        await _execute_workflow()
        
        execution = workflow_executions[execution_id]
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": execution["status"],
            "result": execution.get("result"),
            "error": execution.get("error"),
            "execution_time_ms": execution.get("execution_time_ms")
        }

@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(execution_id: str):
    """
    Get the status and result of a workflow execution.
    """
    if execution_id not in workflow_executions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with ID {execution_id} not found"
        )
    
    execution = workflow_executions[execution_id]
    
    return {
        "execution_id": execution_id,
        "workflow_id": execution["workflow_id"],
        "status": execution["status"],
        "result": execution.get("result"),
        "error": execution.get("error"),
        "execution_time_ms": execution.get("execution_time_ms")
    }

@router.get("/", response_model=List[Dict[str, Any]])
async def list_workflows():
    """
    List all available workflows.
    """
    return [
        {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "step_count": len(workflow.steps),
            "created_at": datetime.utcnow().isoformat()
        }
        for workflow_id, workflow in workflow_registry.items()
    ]

@router.get("/executions/", response_model=List[Dict[str, Any]])
async def list_workflow_executions(workflow_id: Optional[str] = None):
    """
    List all workflow executions, optionally filtered by workflow_id.
    """
    executions = []
    
    for exec_id, exec_data in workflow_executions.items():
        if workflow_id and exec_data["workflow_id"] != workflow_id:
            continue
            
        executions.append({
            "execution_id": exec_id,
            "workflow_id": exec_data["workflow_id"],
            "status": exec_data["status"],
            "start_time": exec_data["start_time"],
            "end_time": exec_data.get("end_time"),
            "execution_time_ms": exec_data.get("execution_time_ms")
        })
    
    # Sort by start time, newest first
    executions.sort(key=lambda x: x["start_time"], reverse=True)
    
    return executions
