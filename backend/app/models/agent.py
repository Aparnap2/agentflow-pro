from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import uuid4
from ..core.config import PlanType
from .base import AgentRole, Department

class AgentConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: AgentRole
    department: Department
    level: int
    manager_id: Optional[str] = None
    direct_reports: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)
    system_prompt: str = ""
    max_concurrent_tasks: int = 5
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    memory_context: Dict[str, Any] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    agent_id: Optional[str] = None
    message: str
    message_type: str  # Using string type for flexibility
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class DocumentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    content_type: str
    size: int
    processed: bool = False
    chunks_count: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
