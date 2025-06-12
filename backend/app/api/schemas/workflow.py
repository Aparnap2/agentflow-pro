"""Pydantic models for workflow-related API endpoints."""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl

class WorkflowStatus(str, Enum):
    """Status of a workflow."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    PAUSED = "paused"

class TaskType(str, Enum):
    """Types of tasks in a workflow."""
    MANUAL = "manual"
    AUTOMATED = "automated"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    CONDITIONAL = "conditional"

class TaskStatus(str, Enum):
    """Status of a task in a workflow."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskDependency(BaseModel):
    """Model for task dependencies."""
    task_id: str
    required: bool = True
    condition: Optional[Dict[str, Any]] = None

class TaskConfig(BaseModel):
    """Configuration for a workflow task."""
    task_type: TaskType = TaskType.MANUAL
    assignee: Optional[Union[str, List[str]]] = None
    due_date: Optional[datetime] = None
    priority: int = 1
    retry_count: int = 0
    timeout: Optional[int] = None
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskCreate(BaseModel):
    """Model for creating a workflow task."""
    name: str
    description: str = ""
    config: TaskConfig = Field(default_factory=TaskConfig)
    dependencies: List[TaskDependency] = Field(default_factory=list)

class TaskResponse(TaskCreate):
    """Response model for a workflow task."""
    id: str
    workflow_id: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WorkflowBase(BaseModel):
    """Base model for workflow data."""
    name: str
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.DRAFT
    is_template: bool = False
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowCreate(WorkflowBase):
    """Model for creating a new workflow."""
    tasks: List[TaskCreate] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)

class WorkflowUpdate(BaseModel):
    """Model for updating an existing workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    is_template: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class WorkflowResponse(WorkflowBase):
    """Response model for workflow data."""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: int = 1
    tasks: List[TaskResponse] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WorkflowListResponse(BaseModel):
    """Response model for listing workflows."""
    items: List[WorkflowResponse]
    total: int
    page: int
    size: int
    has_more: bool

class WorkflowExecutionRequest(BaseModel):
    """Request model for executing a workflow."""
    input_data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    start_task_id: Optional[str] = None
    override_config: Dict[str, Any] = Field(default_factory=dict)

class WorkflowExecutionResponse(BaseModel):
    """Response model for a workflow execution."""
    execution_id: str
    workflow_id: str
    status: str
    current_task_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WorkflowStatsResponse(BaseModel):
    """Response model for workflow statistics."""
    workflow_id: str
    executions_count: int
    avg_execution_time: float
    success_rate: float
    avg_tasks_per_execution: float
    most_common_errors: List[Dict[str, Any]] = Field(default_factory=list)
    last_executed: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
