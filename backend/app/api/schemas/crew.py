"""Pydantic models for crew-related API endpoints."""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl

class CrewMemberRole(str, Enum):
    """Roles that crew members can have."""
    LEADER = "leader"
    MEMBER = "member"
    OBSERVER = "observer"
    REVIEWER = "reviewer"

class CrewMember(BaseModel):
    """Model for a crew member."""
    agent_id: str
    role: CrewMemberRole = CrewMemberRole.MEMBER
    permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrewBase(BaseModel):
    """Base model for crew data."""
    name: str
    description: str = ""
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class CrewCreate(CrewBase):
    """Model for creating a new crew."""
    members: List[CrewMember] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

class CrewUpdate(BaseModel):
    """Model for updating an existing crew."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None

class CrewResponse(CrewBase):
    """Response model for crew data."""
    id: str
    created_at: datetime
    updated_at: datetime
    members: List[Dict[str, Any]] = Field(default_factory=list)
    workflow_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CrewListResponse(BaseModel):
    """Response model for listing crews."""
    items: List[CrewResponse]
    total: int
    page: int
    size: int
    has_more: bool

class CrewExecutionRequest(BaseModel):
    """Request model for executing a crew."""
    input_data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    stream: bool = False

class CrewExecutionResponse(BaseModel):
    """Response model for a crew execution."""
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrewStatsResponse(BaseModel):
    """Response model for crew statistics."""
    crew_id: str
    executions_count: int
    avg_execution_time: float
    success_rate: float
    last_executed: Optional[datetime] = None
    member_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
