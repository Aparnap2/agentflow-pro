"""Domain models for the application."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

from .base import Node, NodeType, Relationship, RelationshipType

# Re-export base types
__all__ = [
    'Node', 'NodeType', 'Relationship', 'RelationshipType',
    'AgentNode', 'CrewNode', 'WorkflowNode', 'TaskNode', 'MessageNode',
    'BELONGS_TO', 'HAS_MEMBER', 'EXECUTES', 'CREATED_BY', 'PART_OF', 'NEXT', 'USES', 'PRODUCES'
]

# Common relationship types for easier access
BELONGS_TO = RelationshipType.BELONGS_TO
HAS_MEMBER = RelationshipType.HAS_MEMBER
EXECUTES = RelationshipType.EXECUTES
CREATED_BY = RelationshipType.CREATED_BY
PART_OF = RelationshipType.PART_OF
NEXT = RelationshipType.NEXT
USES = RelationshipType.USES
PRODUCES = RelationshipType.PRODUCES

class AgentNode(Node):
    """Represents an agent in the system."""
    type: NodeType = Field(default=NodeType.AGENT, const=True)
    name: str
    description: str = ""
    config: Dict[str, Any] = Field(default_factory=dict)
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    llm_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrewNode(Node):
    """Represents a crew of agents."""
    type: NodeType = Field(default=NodeType.CREW, const=True)
    name: str
    description: str = ""
    members: List[Dict[str, Any]] = Field(default_factory=list)  # List of agent IDs with roles
    workflow_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowNode(Node):
    """Represents a workflow definition."""
    type: NodeType = Field(default=NodeType.WORKFLOW, const=True)
    name: str
    description: str = ""
    version: str = "1.0.0"
    entry_point: str  # ID of the starting task
    tasks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # Task ID to task definition
    edges: List[Dict[str, str]] = Field(default_factory=list)  # List of {source, target} task IDs
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskNode(Node):
    """Represents a task in a workflow."""
    type: NodeType = Field(default=NodeType.TASK, const=True)
    name: str
    description: str = ""
    task_type: str  # e.g., "llm", "tool", "condition", "parallel"
    config: Dict[str, Any] = Field(default_factory=dict)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    is_async: bool = False
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageNode(Node):
    """Represents a message in a conversation."""
    type: NodeType = Field(default=NodeType.MESSAGE, const=True)
    content: str
    role: str  # "user", "assistant", "system", "function"
    conversation_id: str
    parent_message_id: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    function_result: Optional[Dict[str, Any]] = None
    tokens: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
