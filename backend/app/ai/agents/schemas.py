"""
Pydantic models for agent configuration and state management.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


class AgentRole(str, Enum):
    """Defines the role of an agent in the system."""
    STRATEGIC_PLANNER = "strategic_planner"
    MARKETING_SPECIALIST = "marketing_specialist"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    SALES_AGENT = "sales_agent"
    HR_SPECIALIST = "hr_specialist"


class AgentConfig(BaseModel):
    """Configuration for creating an agent."""
    id: str = Field(..., description="Unique identifier for the agent")
    role: str = Field(..., description="The agent's specialized function")
    goal: str = Field(..., description="The agent's primary objective")
    backstory: str = Field(..., description="The agent's background and expertise")
    tools: List[str] = Field(default_factory=list, description="List of tool names the agent can use")
    verbose: bool = Field(False, description="Enable verbose output")
    allow_delegation: bool = Field(True, description="Allow agent to delegate tasks")
    max_iter: int = Field(15, description="Maximum number of iterations for task execution")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "market_researcher_1",
                "role": "Market Research Analyst",
                "goal": "Conduct thorough market research to identify trends and opportunities",
                "backstory": "You are an experienced market researcher with expertise in analyzing industry trends and consumer behavior.",
                "tools": ["web_search", "data_analysis"],
                "verbose": True,
                "allow_delegation": True,
                "max_iter": 10
            }
        }


class AgentState(BaseModel):
    """Represents the state of an agent during execution."""
    agent_id: str
    current_task: Optional[str] = None
    memory: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    last_updated: float = Field(default_factory=lambda: time.time())


class CrewConfig(BaseModel):
    """Configuration for creating a crew of agents."""
    id: str
    name: str
    description: str
    agent_ids: List[str]
    process: str = "hierarchical"  # hierarchical, sequential, parallel
    verbose: bool = False
    memory: bool = True
    cache: bool = True
    max_rounds: int = 5
    manager_llm_config: Optional[Dict[str, Any]] = None


class WorkflowStep(BaseModel):
    """Represents a step in a workflow."""
    id: str
    name: str
    description: str
    agent_id: str
    expected_output: str
    tools: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowConfig(BaseModel):
    """Configuration for a workflow."""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    max_iterations: int = 10
    verbose: bool = True
    enable_observability: bool = True


class ExecutionContext(BaseModel):
    """Context for workflow execution."""
    workflow_id: str
    execution_id: str
    input_data: Dict[str, Any]
    state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
