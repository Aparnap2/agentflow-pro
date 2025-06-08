"""
CrewAI Integration Module

This module provides integration with the CrewAI framework for multi-agent collaboration.
It includes classes for creating and managing agents, crews, and workflow steps.
"""

import logging
from typing import Dict, List, Optional, Any, Type, Union, TypeVar, Callable
from functools import wraps
from datetime import datetime

from pydantic import BaseModel, Field, validator
from crewai import Agent as CrewAIAgent
from crewai.crew import Crew as CrewAICrew
from crewai.process import Process as CrewAIProcess
from crewai.task import Task as CrewAITask

from ..agents.base_agent import BaseAgent, AgentConfig
from ..workflow.workflow_manager import Workflow, BaseWorkflowStep, WorkflowContext
from ...core.config import settings

logger = logging.getLogger(__name__)

# Type variables for generic type hints
T = TypeVar('T')

def handle_crewai_errors(func: Callable) -> Callable:
    """Decorator to handle common CrewAI errors."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as ve:
            logger.error(f"Validation error in {func.__name__}: {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise RuntimeError(f"CrewAI operation failed: {str(e)}")
    return wrapper

class CrewAIConfig(BaseModel):
    """Configuration for CrewAI integration."""
    process: str = Field(
        "sequential",
        description="Process type: sequential, hierarchical, or parallel"
    )
    verbose: bool = Field(
        False,
        description="Enable verbose output for debugging"
    )
    memory: bool = Field(
        True,
        description="Enable memory for the crew"
    )
    cache: bool = Field(
        True,
        description="Enable caching for the crew"
    )
    max_rpm: Optional[int] = Field(
        None,
        description="Maximum requests per minute"
    )
    max_workers: int = Field(
        5,
        description="Maximum number of worker threads"
    )
    
    @validator('process')
    def validate_process(cls, v):
        """Validate the process type."""
        valid_processes = ["sequential", "hierarchical", "parallel"]
        if v not in valid_processes:
            raise ValueError(f"Process must be one of {valid_processes}")
        return v

class CrewAIAgentWrapper(BaseAgent):
    """Wrapper around CrewAI's Agent to work with our BaseAgent interface."""
    
    def __init__(self, config: AgentConfig, crewai_agent: CrewAIAgent):
        super().__init__(config)
        self.crewai_agent = crewai_agent
        self._metrics = {
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0,
            'total_duration': 0.0,
            'last_execution': None
        }
    
    @handle_crewai_errors
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input using the CrewAI agent.
        
        Args:
            input_data: Dictionary containing 'task' and 'context' keys
            
        Returns:
            Dictionary containing the execution result
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If execution fails
        """
        import time
        start_time = time.time()
        self._metrics['execution_count'] += 1
        
        try:
            # Validate input
            if not isinstance(input_data, dict):
                raise ValueError("Input must be a dictionary")
                
            task = input_data.get("task", "")
            context = input_data.get("context", {})
            
            if not task:
                raise ValueError("Task is required")
            
            # Create a CrewAI task
            crewai_task = CrewAITask(
                description=task,
                agent=self.crewai_agent,
                context=context,
                expected_output=f"The result of: {task}"
            )
            
            # Execute the task
            result = await self.crewai_agent.execute_task(crewai_task)
            
            # Update metrics
            duration = time.time() - start_time
            self._metrics.update({
                'success_count': self._metrics['success_count'] + 1,
                'total_duration': self._metrics['total_duration'] + duration,
                'last_execution': datetime.utcnow().isoformat(),
                'last_duration': duration
            })
            
            return {
                'success': True,
                'output': result,
                'metrics': self._metrics
            }
            
        except Exception as e:
            self._metrics['error_count'] += 1
            self._metrics['last_error'] = str(e)
            self._metrics['last_execution'] = datetime.utcnow().isoformat()
            
            logger.error(f"Error in CrewAIAgentWrapper.process: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'metrics': self._metrics
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current metrics for this agent."""
        return self._metrics

class CrewAIIntegration:
    """
    Integration class for CrewAI to manage multi-agent collaboration.
    
    This class provides methods to create and manage agents, crews, and tasks
    using the CrewAI framework, with support for observability and error handling.
    """
    
    def __init__(self, agent_factory=None):
        """
        Initialize the CrewAI integration.
        
        Args:
            agent_factory: Reference to the AgentFactory instance (optional)
        """
        self.agent_factory = agent_factory
        self.crews: Dict[str, CrewAICrew] = {}
        self._agent_cache: Dict[str, CrewAIAgent] = {}
        logger.info("CrewAI Integration initialized")
    
    @handle_crewai_errors
    def create_crewai_agent(self, agent_config: AgentConfig) -> CrewAIAgent:
        """
        Create a CrewAI agent from our agent config.
        
        Args:
            agent_config: Configuration for the agent
            
        Returns:
            CrewAIAgent: The created CrewAI agent
            
        Raises:
            ValueError: If agent configuration is invalid
            RuntimeError: If agent creation fails
        """
        cache_key = f"{agent_config.role}:{agent_config.goal}"
        
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]
        
        try:
            agent = CrewAIAgent(
                role=agent_config.role,
                goal=agent_config.goal,
                backstory=agent_config.backstory or "",
                allow_delegation=agent_config.allow_delegation,
                verbose=agent_config.verbose or settings.DEBUG,
                max_iter=agent_config.max_iter or 15,
                # TODO: Map tools from agent_config.tools
                tools=[],
                **(agent_config.llm_config or {})
            )
            
            self._agent_cache[cache_key] = agent
            logger.info(f"Created CrewAI agent: {agent_config.role}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create CrewAI agent: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to create CrewAI agent: {str(e)}")
    
    @handle_crewai_errors
    def create_crew(
        self,
        crew_id: str,
        name: str,
        agent_ids: List[str],
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> CrewAICrew:
        """
        Create a new crew with the given agents.
        
        Args:
            crew_id: Unique identifier for the crew
            name: Display name for the crew
            agent_ids: List of agent IDs to include in the crew
            config: Additional configuration for the crew
            **kwargs: Additional keyword arguments for crew creation
            
        Returns:
            CrewAICrew: The created crew
            
        Raises:
            ValueError: If any agent is not found or configuration is invalid
            RuntimeError: If crew creation fails
        """
        if not crew_id:
            raise ValueError("Crew ID is required")
            
        if not agent_ids:
            raise ValueError("At least one agent ID is required")
            
        if crew_id in self.crews:
            logger.warning(f"Crew with ID {crew_id} already exists. Updating.")
        
        try:
            # Get or create CrewAI agents
            crew_agents = []
            for agent_id in agent_ids:
                if not self.agent_factory:
                    raise ValueError("Agent factory is required to resolve agent IDs")
                    
                agent = self.agent_factory.get_agent(agent_id)
                if not agent:
                    raise ValueError(f"Agent {agent_id} not found")
                
                # Create or get CrewAI agent
                crew_agent = self.create_crewai_agent(agent.config)
                crew_agents.append(crew_agent)
            
            # Create crew config with defaults
            crew_config = CrewAIConfig(**(config or {}))
            
            # Get the process type
            try:
                process = getattr(CrewAIProcess, crew_config.process.upper())
            except AttributeError:
                raise ValueError(f"Invalid process type: {crew_config.process}")
            
            # Create the crew
            crew = CrewAICrew(
                name=name,
                agents=crew_agents,
                process=process,
                verbose=crew_config.verbose or settings.DEBUG,
                memory=crew_config.memory,
                cache=crew_config.cache,
                max_rpm=crew_config.max_rpm,
                max_workers=crew_config.max_workers,
                **kwargs
            )
            
            self.crews[crew_id] = crew
            logger.info(f"Created CrewAI crew '{name}' with {len(crew_agents)} agents")
            return crew
            
        except Exception as e:
            logger.error(f"Failed to create crew: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to create crew: {str(e)}")
    
    @handle_crewai_errors
    async def execute_crew_task(
        self,
        crew_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a task with the specified crew.
        
        Args:
            crew_id: ID of the crew to execute the task
            task: Task description
            context: Additional context for the task
            **kwargs: Additional keyword arguments for task execution
            
        Returns:
            Dictionary containing the execution result
            
        Raises:
            ValueError: If crew is not found
            RuntimeError: If task execution fails
        """
        if not crew_id:
            raise ValueError("Crew ID is required")
            
        if not task:
            raise ValueError("Task description is required")
        
        crew = self.crews.get(crew_id)
        if not crew:
            raise ValueError(f"Crew {crew_id} not found")
        
        try:
            # Create and execute the task
            result = await crew.kickoff(
                inputs={
                    "task": task,
                    "context": context or {}
                },
                **kwargs
            )
            
            logger.info(f"Crew {crew_id} task executed successfully")
            return {
                "success": True,
                "result": result,
                "crew_id": crew_id
            }
            
        except Exception as e:
            error_msg = f"Error executing crew task: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "crew_id": crew_id
            }

class CrewAIWorkflowStep(BaseWorkflowStep):
    """
    Workflow step that executes a CrewAI crew.
    
    This class provides a way to integrate CrewAI crews into larger workflows,
    with support for input/output validation and error handling.
    """
    
    def __init__(
        self,
        name: str,
        crew_id: str,
        task_template: str,
        expected_output: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the workflow step.
        
        Args:
            name: Name of the workflow step
            crew_id: ID of the crew to execute
            task_template: Template for the task description (supports string formatting)
            expected_output: Expected output format or description
            **kwargs: Additional keyword arguments for the base class
        """
        super().__init__(name, **kwargs)
        self.crew_id = crew_id
        self.task_template = task_template
        self.expected_output = expected_output or "Results of the crew execution"
        
        # Initialize metrics
        self._metrics = {
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0,
            'total_duration': 0.0,
            'last_execution': None
        }
    
    async def _execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute the workflow step using the specified crew.
        
        Args:
            context: Workflow context containing input data
            
        Returns:
            Dictionary containing the execution result and metadata
            
        Raises:
            RuntimeError: If execution fails
        """
        import time
        start_time = time.time()
        self._metrics['execution_count'] += 1
        
        try:
            # Render the task template with context
            task = self.task_template.format(**context.data)
            
            # Get the crew from the workflow context or config
            crew = None
            if hasattr(self, 'config') and hasattr(self.config, 'get'):
                crew_integration = self.config.get("crewai_integration")
                if crew_integration:
                    crew = crew_integration.crews.get(self.crew_id)
            
            if not crew:
                error_msg = f"Crew {self.crew_id} not found in workflow context"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Execute the task
            result = await crew.kickoff(
                inputs={
                    "task": task,
                    "context": context.data
                }
            )
            
            # Update metrics
            duration = time.time() - start_time
            self._metrics.update({
                'success_count': self._metrics['success_count'] + 1,
                'total_duration': self._metrics['total_duration'] + duration,
                'last_execution': datetime.utcnow().isoformat(),
                'last_duration': duration
            })
            
            # Update the context with the result
            return {
                'status': 'completed',
                'output': result,
                'expected_output': self.expected_output,
                'success': True,
                'metrics': self._metrics,
                'duration': duration
            }
            
        except Exception as e:
            error_msg = f"Error in CrewAIWorkflowStep._execute: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Update metrics
            self._metrics.update({
                'error_count': self._metrics['error_count'] + 1,
                'last_error': error_msg,
                'last_execution': datetime.utcnow().isoformat()
            })
            
            return {
                'status': 'failed',
                'error': error_msg,
                'success': False,
                'metrics': self._metrics,
                'duration': time.time() - start_time
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the current metrics for this workflow step.
        
        Returns:
            Dictionary containing execution metrics
        """
        return self._metrics
