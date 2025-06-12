import json
import logging
import asyncio
from typing import Dict, Type, Any, Optional, List, Tuple, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from pydantic import BaseModel, Field
from fastapi import HTTPException, status
from redis import asyncio as aioredis

from .base_agent import (
    BaseAgent, AgentConfig, AgentResponse, AgentState,
    CircuitBreakerError, AgentError
)
from .strategic_agent import StrategicAgent
from .sales_agent import SalesAgent
from .marketing_agent import MarketingAgent
from .finance_agent import FinanceAgent
from .hr_agent import HRAgent
from .dev_agent import DevelopmentAgent
from .design_agent import DesignAgent
from ..core.config import settings
from ..workflow.workflow_manager import Workflow, BaseWorkflowStep, WorkflowContext

# Import integrations
from ..integrations import (
    CrewAIIntegration, CrewAIWorkflowStep,
    LangGraphIntegration, LangGraphWorkflowStep,
    LangfuseIntegration, initialize_integrations
)

logger = logging.getLogger(__name__)

class AgentPersistenceError(Exception):
    """Raised when there's an error persisting or loading agent state."""
    pass

class AgentMetrics(BaseModel):
    """Metrics for agent performance monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    error_rate: float = 0.0

class AgentFactory:
    """Factory class for creating and managing agent instances with persistence."""
    
    _agent_registry: Dict[str, Type[BaseAgent]] = {
        'strategic': StrategicAgent,
        'sales': SalesAgent,
        'marketing': MarketingAgent,
        'finance': FinanceAgent,
        'hr': HRAgent,
        'development': DevelopmentAgent,
        'design': DesignAgent
    }
    
    _agent_instances: Dict[str, BaseAgent] = {}
    _redis: Optional[aioredis.Redis] = None
    _instance = None
    
    # Integration instances
    _crewai_integration: Optional[CrewAIIntegration] = None
    _langgraph_integration: Optional[LangGraphIntegration] = None
    _langfuse_integration: Optional[LangfuseIntegration] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._redis = None
    
    async def initialize(self):
        """Initialize the factory with required connections."""
        # Initialize Redis
        if not self._redis:
            try:
                self._redis = aioredis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                await self._redis.ping()
                logger.info("Connected to Redis for agent state persistence")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self._redis = None
        
        # Initialize integrations
        initialize_integrations({
            "langfuse": {
                "public_key": settings.LANGFUSE_PUBLIC_KEY,
                "secret_key": settings.LANGFUSE_SECRET_KEY,
                "host": settings.LANGFUSE_HOST,
                "enabled": bool(settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY)
            },
            "crewai": {
                "enabled": True
            },
            "langgraph": {
                "enabled": True
            }
        })
    
    async def close(self):
        """Clean up resources."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            
        # Clean up integrations
        self._crewai_integration = None
        self._langgraph_integration = None
        self._langfuse_integration = None
    
    @classmethod
    def register_agent(cls, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type with the factory."""
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"Agent class must be a subclass of BaseAgent")
        cls._agent_registry[agent_type] = agent_class
        logger.info(f"Registered new agent type: {agent_type} -> {agent_class.__name__}")
    
    @property
    def crewai_integration(self) -> Optional[CrewAIIntegration]:
        """Get the CrewAI integration instance."""
        if not self._crewai_integration:
            from ..integrations import get_crewai_integration
            self._crewai_integration = get_crewai_integration()
        return self._crewai_integration
    
    @property
    def langgraph_integration(self) -> Optional[LangGraphIntegration]:
        """Get the LangGraph integration instance."""
        if not self._langgraph_integration:
            from ..integrations import get_langgraph_integration
            self._langgraph_integration = get_langgraph_integration()
        return self._langgraph_integration
    
    @property
    def langfuse_integration(self) -> Optional[LangfuseIntegration]:
        """Get the Langfuse integration instance."""
        if not self._langfuse_integration:
            from ..integrations import get_langfuse_integration
            self._langfuse_integration = get_langfuse_integration()
        return self._langfuse_integration
    
    def create_crew(
        self,
        crew_id: str,
        name: str,
        agent_ids: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create a new crew with the given agents.
        
        Args:
            crew_id: Unique identifier for the crew
            name: Name of the crew
            agent_ids: List of agent IDs to include in the crew
            config: Configuration for the crew
            
        Returns:
            The created crew
        """
        if not self.crewai_integration:
            raise RuntimeError("CrewAI integration is not available")
            
        return self.crewai_integration.create_crew(
            crew_id=crew_id,
            name=name,
            agent_ids=agent_ids,
            config=config or {}
        )
    
    async def execute_crew_task(
        self,
        crew_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task with the specified crew.
        
        Args:
            crew_id: ID of the crew to execute the task with
            task: Task description
            context: Additional context for the task
            
        Returns:
            Dictionary containing the result of the task execution
        """
        if not self.crewai_integration:
            raise RuntimeError("CrewAI integration is not available")
            
        return await self.crewai_integration.execute_crew_task(
            crew_id=crew_id,
            task=task,
            context=context or {}
        )
    
    def create_langgraph(
        self,
        graph_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create a new LangGraph with the given configuration.
        
        Args:
            graph_id: Unique identifier for the graph
            config: Configuration for the graph
            
        Returns:
            The created graph
        """
        if not self.langgraph_integration:
            raise RuntimeError("LangGraph integration is not available")
            
        return self.langgraph_integration.create_graph(
            graph_id=graph_id,
            config=config or {}
        )
    
    async def execute_langgraph(
        self,
        graph_id: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a LangGraph with the given input data.
        
        Args:
            graph_id: ID of the graph to execute
            input_data: Input data for the graph
            config: Additional configuration for the execution
            
        Returns:
            Dictionary containing the result of the graph execution
        """
        if not self.langgraph_integration:
            raise RuntimeError("LangGraph integration is not available")
            
        return await self.langgraph_integration.execute_graph(
            graph_id=graph_id,
            input_data=input_data,
            config=config or {}
        )
    
    async def create_agent(
        self,
        agent_type: str,
        agent_id: str,
        name: str,
        role: str,
        goal: str,
        **kwargs
    ) -> BaseAgent:
        """
        Create a new agent instance or return existing one.
        
        Args:
            agent_type: Type of agent to create (e.g., 'sales', 'marketing')
            agent_id: Unique identifier for this agent instance
            name: Human-readable name for the agent
            role: The role of the agent
            goal: The primary goal of the agent
            **kwargs: Additional configuration parameters
            
        Returns:
            BaseAgent: The created or existing agent instance
            
        Raises:
            ValueError: If agent_type is unknown
            AgentPersistenceError: If there's an error loading/saving agent state
        """
        if agent_type not in self._agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}. "
                           f"Available types: {', '.join(self._agent_registry.keys())}")
        
        instance_key = f"{agent_type}:{agent_id}"
        
        # Return existing instance if it exists
        if instance_key in self._agent_instances:
            return self._agent_instances[instance_key]
        
        # Try to load agent state if persistence is available
        agent_state = await self._load_agent_state(instance_key)
        
        # Create agent config, merging with any saved state
        config_data = {
            "id": agent_id,
            "name": name,
            "role": role,
            "goal": goal,
            "llm_config": {
                "model": settings.LLM_MODEL,
                "api_key": settings.OPENAI_API_KEY or settings.GEMINI_API_KEY,
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        }
        
        # Update with any saved state
        if agent_state and "config" in agent_state:
            config_data.update(agent_state["config"])
        
        # Apply any overrides from kwargs
        config_data.update(kwargs)
        
        # Create the config object
        config = AgentConfig(**config_data)
        
        # Create the agent instance
        agent_class = self._agent_registry[agent_type]
        agent = agent_class(config)
        
        # Restore state if available
        if agent_state:
            await self._restore_agent_state(agent, agent_state)
        
        # Store the agent instance
        self._agent_instances[instance_key] = agent
        
        logger.info(f"Created new {agent_type} agent: {name} (ID: {agent_id})")
        return agent
    
    async def get_agent(self, agent_type: str, agent_id: str) -> Optional[BaseAgent]:
        """Get an existing agent instance by type and ID."""
        instance_key = f"{agent_type}:{agent_id}"
        return self._agent_instances.get(instance_key)
    
    async def get_or_create_agent(
        self,
        agent_type: str,
        agent_id: str,
        name: str,
        role: str,
        goal: str,
        **kwargs
    ) -> BaseAgent:
        """Get an existing agent or create a new one if it doesn't exist."""
        agent = await self.get_agent(agent_type, agent_id)
        if agent is None:
            agent = await self.create_agent(
                agent_type=agent_type,
                agent_id=agent_id,
                name=name,
                role=role,
                goal=goal,
                **kwargs
            )
        return agent
    
    async def save_agent_state(self, agent: BaseAgent) -> bool:
        """Save the current state of an agent to persistent storage."""
        try:
            if not self._redis:
                return False
                
            state = {
                "agent_id": agent.config.id,
                "agent_type": agent.__class__.__name__.lower().replace("agent", ""),
                "state": agent.state.value if hasattr(agent, 'state') else AgentState.IDLE.value,
                "metrics": agent.metrics if hasattr(agent, 'metrics') else {},
                "config": agent.config.dict(exclude={"llm_config"}),
                "last_updated": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
            
            instance_key = f"{state['agent_type']}:{agent.config.id}"
            
            # Save to Redis with TTL of 7 days
            await self._redis.set(
                f"agent:{instance_key}",
                json.dumps(state, default=str),
                ex=timedelta(days=7)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving agent state: {str(e)}", exc_info=True)
            return False
    
    async def _load_agent_state(self, instance_key: str) -> Optional[Dict]:
        """Load agent state from persistent storage."""
        try:
            if not self._redis:
                return None
                
            state_data = await self._redis.get(f"agent:{instance_key}")
            if not state_data:
                return None
                
            state = json.loads(state_data)
            
            # Convert string timestamps back to datetime objects
            for time_field in ["last_updated"]:
                if time_field in state:
                    state[time_field] = datetime.fromisoformat(state[time_field])
            
            return state
            
        except Exception as e:
            logger.error(f"Error loading agent state: {str(e)}", exc_info=True)
            return None
    
    async def _restore_agent_state(self, agent: BaseAgent, state: Dict[str, Any]) -> None:
        """Restore agent state from a previously saved state."""
        try:
            if "state" in state:
                agent.state = AgentState(state["state"])
                
            if "metrics" in state:
                agent.metrics.update(state["metrics"])
                
            logger.info(f"Restored state for agent {agent.config.id}")
            
        except Exception as e:
            logger.error(f"Error restoring agent state: {str(e)}", exc_info=True)
            raise AgentPersistenceError(f"Failed to restore agent state: {str(e)}")
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get information about all active agents."""
        agents = []
        for instance_key, agent in self._agent_instances.items():
            try:
                state = await agent.get_state()
                agents.append({
                    "id": agent.config.id,
                    "type": agent.__class__.__name__.lower().replace("agent", ""),
                    "name": agent.config.name,
                    "state": state,
                    "last_updated": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting state for agent {instance_key}: {str(e)}")
        
        return agents
    
    async def clear_agents(self) -> None:
        """Clear all agent instances from memory."""
        # Save states before clearing
        for agent in self._agent_instances.values():
            await self.save_agent_state(agent)
        
        self._agent_instances.clear()
        logger.info("Cleared all agent instances from memory")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the agent factory and its components."""
        redis_ok = False
        if self._redis:
            try:
                await self._redis.ping()
                redis_ok = True
            except Exception:
                redis_ok = False
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_registered": len(self._agent_registry),
            "agents_active": len(self._agent_instances),
            "redis_connected": redis_ok,
            "version": "1.0.0"  # Should come from package version
        }

# Create a singleton instance
agent_factory = AgentFactory()

# Initialize the factory when this module is imported
async def init_agent_factory():
    """Initialize the agent factory with required connections."""
    await agent_factory.initialize()

# Run the initialization
import asyncio
asyncio.create_task(init_agent_factory())
