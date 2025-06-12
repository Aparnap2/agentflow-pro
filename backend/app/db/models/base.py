"""Base models for Graphiti with Neo4j."""
from typing import Dict, Any, List, Optional, Type, TypeVar, ClassVar
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, validator
from enum import Enum
from functools import cached_property

T = TypeVar('T', bound='Node')

class RelationshipType(str, Enum):
    BELONGS_TO = "BELONGS_TO"
    HAS_MEMBER = "HAS_MEMBER"
    EXECUTES = "EXECUTES"
    CREATED_BY = "CREATED_BY"
    PART_OF = "PART_OF"
    NEXT = "NEXT"
    USES = "USES"
    PRODUCES = "PRODUCES"

class NodeType(str, Enum):
    AGENT = "Agent"
    CREW = "Crew"
    WORKFLOW = "Workflow"
    TASK = "Task"
    MESSAGE = "Message"
    USER = "User"
    ORGANIZATION = "Organization"
    PROJECT = "Project"

class Node(BaseModel):
    """Base node model for all entities in the graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
    
    @validator('id')
    def validate_id(cls, v):
        if not v:
            return str(uuid.uuid4())
        return v
    
    @cached_property
    def labels(self) -> List[str]:
        """Get the Neo4j labels for this node."""
        return [self.type.value]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary for Neo4j."""
        return {
            "id": self.id,
            "type": self.type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            **self.properties
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a node from a dictionary."""
        props = data.copy()
        node_id = props.pop("id", None)
        node_type = props.pop("type")
        created_at = props.pop("created_at", None)
        updated_at = props.pop("updated_at", None)
        
        # Convert string timestamps back to datetime
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        return cls(
            id=node_id,
            type=NodeType(node_type),
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            properties=props
        )

class Relationship(BaseModel):
    """Represents a relationship between two nodes."""
    source_id: str
    target_id: str
    type: RelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary for Neo4j."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            **self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a relationship from a dictionary."""
        props = data.copy()
        source_id = props.pop("source_id")
        target_id = props.pop("target_id")
        rel_type = RelationshipType(props.pop("type"))
        
        return cls(
            source_id=source_id,
            target_id=target_id,
            type=rel_type,
            properties=props
        )
