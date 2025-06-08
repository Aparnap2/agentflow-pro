from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.ai.agents.base_agent import AgentConfig, AgentResponse
from app.ai.crew.crew_manager import crew_manager, CrewConfig, CrewMember
from app.ai.workflow.workflow_manager import Workflow, BaseWorkflowStep

router = APIRouter(prefix="/agents", tags=["agents"])
logger = logging.getLogger(__name__)

class AgentCreateRequest(BaseModel):
    name: str
    role: str
    goal: str
    backstory: Optional[str] = None
    verbose: bool = False
    allow_delegation: bool = False
    tools: List[str] = []
    llm_config: Optional[Dict[str, Any]] = None

class AgentResponseModel(BaseModel):
    id: str
    name: str
    role: str
    goal: str
    backstory: Optional[str] = None
    verbose: bool
    allow_delegation: bool
    tools: List[str]
    llm_config: Optional[Dict[str, Any]] = None

class TaskRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}

@router.post("/create", response_model=AgentResponseModel)
async def create_agent(agent_data: AgentCreateRequest):
    """Create a new agent with the given configuration."""
    try:
        # In a real implementation, you would create and store the agent
        agent_id = f"agent_{len(crew_manager.crews) + 1}"
        
        # Create agent config (in a real app, this would create an actual agent)
        agent_config = AgentConfig(
            id=agent_id,
            name=agent_data.name,
            role=agent_data.role,
            goal=agent_data.goal,
            backstory=agent_data.backstory,
            verbose=agent_data.verbose,
            allow_delegation=agent_data.allow_delegation,
            tools=agent_data.tools,
            llm_config=agent_data.llm_config
        )
        
        # In a real implementation, you would store the agent and its config
        # For now, we'll just return the config
        return {
            "id": agent_config.id,
            "name": agent_config.name,
            "role": agent_config.role,
            "goal": agent_config.goal,
            "backstory": agent_config.backstory,
            "verbose": agent_config.verbose,
            "allow_delegation": agent_config.allow_delegation,
            "tools": agent_config.tools,
            "llm_config": agent_config.llm_config
        }
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )

@router.post("/{agent_id}/process", response_model=AgentResponse)
async def process_task(agent_id: str, task_request: TaskRequest):
    """Process a task with the specified agent."""
    try:
        # In a real implementation, you would load the agent by ID
        # For now, we'll return a mock response
        return {
            "success": True,
            "output": f"Processed task '{task_request.task}' with agent {agent_id}",
            "metadata": {
                "agent_id": agent_id,
                "timestamp": "2023-01-01T00:00:00Z"  # Use datetime.utcnow().isoformat() in real code
            }
        }
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process task: {str(e)}"
        )

@router.get("/list", response_model=List[AgentResponseModel])
async def list_agents():
    """List all available agents."""
    # In a real implementation, you would return actual agents
    return [
        {
            "id": "agent_1",
            "name": "Support Agent",
            "role": "Customer Support",
            "goal": "Help users with their questions and issues",
            "verbose": False,
            "allow_delegation": True,
            "tools": ["web_search", "knowledge_base"],
            "llm_config": {"model": "gemini-pro"}
        },
        {
            "id": "agent_2",
            "name": "Research Agent",
            "role": "Researcher",
            "goal": "Gather and analyze information",
            "verbose": True,
            "allow_delegation": False,
            "tools": ["web_search", "data_analysis"],
            "llm_config": {"model": "gemini-1.5-pro"}
        }
    ]

# Crew endpoints
class CrewCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    agents: List[Dict[str, Any]] = []
    workflow: Optional[Dict[str, Any]] = None

@router.post("/crews/create", status_code=status.HTTP_201_CREATED)
async def create_crew(crew_data: CrewCreateRequest):
    """Create a new crew of agents."""
    try:
        # In a real implementation, you would validate and create the crew
        crew_config = CrewConfig(
            name=crew_data.name,
            description=crew_data.description,
            agents=crew_data.agents,
            workflow=crew_data.workflow
        )
        
        crew = crew_manager.create_crew(crew_config)
        
        return {
            "crew_id": crew.config.crew_id,
            "name": crew.config.name,
            "status": crew.status,
            "created_at": crew.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating crew: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create crew: {str(e)}"
        )

@router.post("/crews/{crew_id}/execute")
async def execute_crew_task(crew_id: str, task_request: TaskRequest):
    """Execute a task with the specified crew."""
    try:
        result = await crew_manager.execute_crew_task(
            crew_id=crew_id,
            task=task_request.task,
            context=task_request.context
        )
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms,
            "crew_id": crew_id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error executing crew task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute crew task: {str(e)}"
        )

@router.get("/crews/list")
async def list_crews():
    """List all available crews."""
    return crew_manager.list_crews()
