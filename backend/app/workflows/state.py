from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Status of a task in the workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class TaskPriority(str, Enum):
    """Priority levels for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class AgentState(BaseModel):
    """State passed between agent nodes in the workflow"""
    messages: List[BaseMessage] = Field(
        default_factory=list,
        description="Message history for the conversation"
    )
    task_id: str = Field(
        ...,
        description="Unique identifier for the task"
    )
    agent_id: str = Field(
        ...,
        description="ID of the current agent"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the task"
    )
    next_agent: Optional[str] = Field(
        None,
        description="ID of the next agent to handle the task, if any"
    )
    escalate: bool = Field(
        False,
        description="Whether to escalate this task to a higher authority"
    )
    final_result: Optional[Dict[str, Any]] = Field(
        None,
        description="Final result of the task, if completed"
    )
    reasoning_steps: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Step-by-step reasoning and decisions made during processing"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this task was last updated"
    )
    status: TaskStatus = Field(
        TaskStatus.PENDING,
        description="Current status of the task"
    )
    priority: TaskPriority = Field(
        TaskPriority.MEDIUM,
        description="Priority level of the task"
    )

class WorkflowState(BaseModel):
    """State of the entire workflow execution"""
    task_id: str
    current_agent: str
    history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_step(self, agent_id: str, action: str, result: Dict[str, Any]):
        """Add a step to the workflow history"""
        self.history.append({
            "agent_id": agent_id,
            "action": action,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()

class OrchestrationState(BaseModel):
    """State for the overall orchestration process"""
    user_request: str = Field(
        ...,
        description="Original user request that initiated the workflow"
    )
    task_breakdown: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Breakdown of tasks to complete the request"
    )
    assigned_agents: List[str] = Field(
        default_factory=list,
        description="Agents assigned to handle the request"
    )
    results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from each step of the workflow"
    )
    coordination_messages: List[BaseMessage] = Field(
        default_factory=list,
        description="Messages exchanged between agents during coordination"
    )
    final_output: Optional[Dict[str, Any]] = Field(
        None,
        description="Final output of the orchestration"
    )
    status: TaskStatus = Field(
        TaskStatus.PENDING,
        description="Current status of the orchestration"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the orchestration was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the orchestration was last updated"
    )

    def update_status(self, status: TaskStatus):
        """Update the status and set the updated timestamp"""
        self.status = status
        self.updated_at = datetime.utcnow()
