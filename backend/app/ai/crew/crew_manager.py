from typing import Dict, List, Optional, Any, Type, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import uuid
from enum import Enum

from app.ai.agents.base_agent import BaseAgent, AgentConfig
from app.ai.workflow.workflow_manager import Workflow, BaseWorkflowStep, WorkflowContext, WorkflowResult
from app.ai.tools.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class CrewStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"

class CrewConfig(BaseModel):
    """Configuration for a crew of agents."""
    crew_id: str = Field(default_factory=lambda: f"crew_{uuid.uuid4().hex[:8]}")
    name: str
    description: Optional[str] = None
    agents: List[Dict[str, Any]] = Field(default_factory=list)
    workflow: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CrewMember(BaseModel):
    """Represents a member of a crew."""
    agent_id: str
    role: str
    goal: str
    backstory: Optional[str] = None
    agent: Optional[BaseAgent] = None
    tools: List[str] = Field(default_factory=list)

class Crew(BaseModel):
    """A team of agents that work together to accomplish tasks."""
    config: CrewConfig
    members: Dict[str, CrewMember] = Field(default_factory=dict)
    workflow: Optional[Workflow] = None
    status: CrewStatus = CrewStatus.IDLE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_member(self, agent: BaseAgent, role: str, goal: str, backstory: Optional[str] = None) -> 'Crew':
        """Add a member to the crew."""
        member = CrewMember(
            agent_id=agent.config.id,
            role=role,
            goal=goal,
            backstory=backstory,
            agent=agent,
            tools=[tool for tool in agent.tools]
        )
        
        self.members[agent.config.id] = member
        self.updated_at = datetime.utcnow()
        
        # Add agent to workflow if not already present
        if self.workflow and agent.config.id not in [step.name for step in self.workflow.steps]:
            agent_step = AgentWorkflowStep(
                name=agent.config.id,
                agent=agent,
                input_mapping={},
                output_key=f"{agent.config.id}_output"
            )
            self.workflow.add_step(agent_step)
        
        return self
    
    async def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Execute a task using the crew."""
        if not self.workflow:
            raise ValueError("No workflow defined for this crew")
        
        self.status = CrewStatus.PROCESSING
        self.updated_at = datetime.utcnow()
        
        try:
            # Prepare initial context
            initial_context = {
                'task': task,
                'context': context or {},
                'crew_id': self.config.crew_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Execute the workflow
            result = await self.workflow.execute(initial_context)
            
            # Update status
            self.status = CrewStatus.IDLE
            self.updated_at = datetime.utcnow()
            
            return result
            
        except Exception as e:
            self.status = CrewStatus.ERROR
            self.updated_at = datetime.utcnow()
            logger.error(f"Error executing task in crew {self.config.crew_id}: {str(e)}", exc_info=True)
            raise

class AgentWorkflowStep(BaseWorkflowStep):
    """A workflow step that executes an agent."""
    
    def __init__(
        self,
        name: str,
        agent: BaseAgent,
        input_mapping: Dict[str, str],
        output_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.agent = agent
        self.input_mapping = input_mapping
        self.output_key = output_key or f"{name}_output"
    
    async def _execute(self, context: WorkflowContext) -> Dict[str, Any]:
        # Prepare input for the agent
        agent_input = {}
        for param_name, context_key in self.input_mapping.items():
            if context_key in context.data:
                agent_input[param_name] = context.data[context_key]
        
        # Add task if not already in input
        if 'task' not in agent_input and 'task' in context.data:
            agent_input['task'] = context.data['task']
        
        # Execute the agent
        result = await self.agent.process_task(
            agent_input.get('task', ''),
            agent_input
        )
        
        # Return result with the output key
        return {self.output_key: result}

class CrewManager:
    """Manages crews of agents."""
    
    def __init__(self):
        self.crews: Dict[str, Crew] = {}
    
    def create_crew(self, config: CrewConfig) -> Crew:
        """Create a new crew."""
        if config.crew_id in self.crews:
            raise ValueError(f"Crew with ID {config.crew_id} already exists")
        
        crew = Crew(config=config)
        self.crews[config.crew_id] = crew
        
        # Create workflow if specified
        if config.workflow:
            workflow = Workflow(
                workflow_id=f"workflow_{config.crew_id}",
                name=config.workflow.get('name', f"Workflow for {config.name}")
            )
            crew.workflow = workflow
        
        return crew
    
    def get_crew(self, crew_id: str) -> Optional[Crew]:
        """Get a crew by ID."""
        return self.crews.get(crew_id)
    
    def list_crews(self) -> List[Dict[str, Any]]:
        """List all crews."""
        return [
            {
                'crew_id': crew.config.crew_id,
                'name': crew.config.name,
                'description': crew.config.description,
                'status': crew.status,
                'member_count': len(crew.members),
                'created_at': crew.created_at,
                'updated_at': crew.updated_at
            }
            for crew in self.crews.values()
        ]
    
    async def execute_crew_task(
        self,
        crew_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """Execute a task using the specified crew."""
        crew = self.get_crew(crew_id)
        if not crew:
            raise ValueError(f"Crew with ID {crew_id} not found")
        
        return await crew.execute_task(task, context)
    
    def delete_crew(self, crew_id: str) -> bool:
        """Delete a crew."""
        if crew_id in self.crews:
            del self.crews[crew_id]
            return True
        return False

# Singleton instance
crew_manager = CrewManager()
