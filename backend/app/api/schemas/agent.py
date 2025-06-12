"""Pydantic models for agent-related API endpoints."""
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator

class AgentType(str, Enum):
    """Types of agents in the system."""
    GENERAL = "general"
    DESIGN = "design"
    CODE = "code"
    MARKETING = "marketing"
    SALES = "sales"
    SUPPORT = "support"
    ANALYTICS = "analytics"

class ToolConfig(BaseModel):
    """Configuration for an agent tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

class LLMConfig(BaseModel):
    """Configuration for an agent's LLM."""
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: List[str] = Field(default_factory=list)

class AgentBase(BaseModel):
    """Base model for agent data."""
    name: str
    description: str
    agent_type: AgentType = AgentType.GENERAL
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class AgentCreate(AgentBase):
    """Model for creating a new agent."""
    tools: List[ToolConfig] = Field(default_factory=list)
    llm_config: LLMConfig = Field(default_factory=LLMConfig)

class AgentUpdate(BaseModel):
    """Model for updating an existing agent."""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[AgentType] = None
    is_active: Optional[bool] = None
    tools: Optional[List[ToolConfig]] = None
    llm_config: Optional[LLMConfig] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class AgentResponse(AgentBase):
    """Response model for agent data."""
    id: str
    created_at: datetime
    updated_at: datetime
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    llm_config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentListResponse(BaseModel):
    """Response model for listing agents."""
    items: List[AgentResponse]
    total: int
    page: int
    size: int
    has_more: bool

class ProcessTaskRequest(BaseModel):
    """Request model for processing a task with an agent."""
    task: str
    context: Dict[str, Any] = Field(default_factory=dict)
    stream: bool = False

class ProcessTaskResponse(BaseModel):
    """Response model for a processed task."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentStatsResponse(BaseModel):
    """Response model for agent statistics."""
    agent_id: str
    tasks_processed: int
    avg_processing_time: float
    success_rate: float
    last_active: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
