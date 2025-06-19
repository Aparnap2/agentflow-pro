from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from uuid import uuid4
from .base import Department, AgentRole, MessageType

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[str] = None
    department: Optional[Department] = None
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)

    @validator('deadline')
    def validate_deadline(cls, v):
        if v and v < datetime.now():
            raise ValueError("Deadline must be in the future")
        return v

class TaskResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str]
    assigned_agent: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_chain: List[Dict[str, Any]] = Field(default_factory=list)
    error_message: Optional[str] = None
    escalation_reason: Optional[str] = None
