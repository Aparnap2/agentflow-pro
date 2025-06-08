from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Type, Generic, Callable
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import json
from enum import Enum
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState
)
from functools import wraps
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class AgentState(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    UPDATING = "updating"

class AgentConfig(BaseModel):
    """Configuration for an AI agent."""
    id: str
    name: str
    role: str
    goal: str
    backstory: Optional[str] = None
    verbose: bool = False
    allow_delegation: bool = False
    tools: List[str] = Field(default_factory=list)
    llm_config: Dict[str, Any] = Field(default_factory=dict)
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60  # seconds

class AgentResponse(BaseModel):
    """Standard response format for agent operations."""
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None

class CircuitBreakerError(Exception):
    """Raised when the circuit breaker is open."""
    pass

class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

def circuit_breaker(max_failures: int = 3, reset_timeout: int = 60):
    """Circuit breaker decorator for agent methods."""
    def decorator(func):
        failures = 0
        last_failure = 0
        circuit_open = False
        
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            nonlocal failures, last_failure, circuit_open
            
            # Check if circuit is open
            current_time = datetime.now().timestamp()
            if circuit_open:
                if current_time - last_failure < reset_timeout:
                    raise CircuitBreakerError(
                        f"Circuit breaker is open. Too many failures. "
                        f"Will retry after {reset_timeout} seconds"
                    )
                circuit_open = False
            
            try:
                result = await func(self, *args, **kwargs)
                # Reset failure count on success
                failures = 0
                return result
            except Exception as e:
                failures += 1
                last_failure = current_time
                
                if failures >= max_failures:
                    circuit_open = True
                    self.logger.error(
                        f"Circuit breaker triggered after {failures} failures. "
                        f"Will retry after {reset_timeout} seconds"
                    )
                
                raise
        
        return wrapper
    return decorator

class BaseAgent(ABC):
    """Base class for all AI agents with enhanced error handling and state management."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.IDLE
        self.failure_count = 0
        self.last_error = None
        self.metrics = {
            "tasks_processed": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_processing_time": 0.0,
            "last_updated": datetime.utcnow().isoformat()
        }
        self._state_lock = asyncio.Lock()
        self.llm = self._initialize_llm()
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}.{config.id}")
        self.logger.info(f"Initialized {self.__class__.__name__} with ID: {config.id}")
    
    def _initialize_llm(self):
        """Initialize the language model based on configuration."""
        # Implementation would depend on the actual LLM being used
        # For example, using OpenAI or another provider
        pass
    
    async def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent."""
        return {
            "agent_id": self.config.id,
            "state": self.state,
            "metrics": self.metrics,
            "last_error": str(self.last_error) if self.last_error else None,
            "config": self.config.dict(exclude={"llm_config"}),
            "llm_config_available": bool(self.config.llm_config)
        }
    
    async def update_state(self, **updates):
        """Update agent state in a thread-safe manner."""
        async with self._state_lock:
            for key, value in updates.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.metrics["last_updated"] = datetime.utcnow().isoformat()
    
    @asynccontextmanager
    async def _processing_context(self, task_name: str):
        """Context manager for task processing with state management."""
        start_time = datetime.utcnow()
        await self.update_state(state=AgentState.PROCESSING)
        
        try:
            self.logger.info(f"Starting task: {task_name}")
            yield
            
            # Update metrics on success
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self.update_state(
                state=AgentState.IDLE,
                failure_count=0,
                last_error=None,
                metrics={
                    "tasks_processed": self.metrics["tasks_processed"] + 1,
                    "successful_tasks": self.metrics["successful_tasks"] + 1,
                    "average_processing_time": (
                        (self.metrics["average_processing_time"] * self.metrics["tasks_processed"] + processing_time) /
                        (self.metrics["tasks_processed"] + 1)
                    )
                }
            )
            self.logger.info(f"Completed task: {task_name} in {processing_time:.2f}ms")
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = str(e)
            await self.update_state(
                state=AgentState.ERROR,
                failure_count=self.failure_count + 1,
                last_error=error_msg,
                metrics={
                    "tasks_processed": self.metrics["tasks_processed"] + 1,
                    "failed_tasks": self.metrics["failed_tasks"] + 1,
                    "average_processing_time": (
                        (self.metrics["average_processing_time"] * self.metrics["tasks_processed"] + processing_time) /
                        (self.metrics["tasks_processed"] + 1)
                    )
                }
            )
            self.logger.error(
                f"Task '{task_name}' failed after {processing_time:.2f}ms: {error_msg}",
                exc_info=True
            )
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def _call_llm_with_retry(self, prompt: str, **kwargs) -> str:
        """Call LLM with retry logic."""
        try:
            # This is a placeholder - implement actual LLM call
            response = await self.llm.generate(prompt, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise
    
    @circuit_breaker(max_failures=5, reset_timeout=300)
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a task with the given context."""
        start_time = datetime.utcnow()
        
        async with self._processing_context(f"process_task: {task[:50]}..."):
            try:
                result = await self._process_task(task, context or {})
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                return AgentResponse(
                    success=True,
                    output=result,
                    execution_time_ms=execution_time,
                    metadata={
                        "agent_id": self.config.id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "task_type": task.split(":")[0] if ":" in task else "general"
                    }
                )
                
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                error_msg = f"Error processing task '{task}': {str(e)}"
                
                if not isinstance(e, (CircuitBreakerError, AgentError)):
                    self.logger.error(error_msg, exc_info=True)
                
                return AgentResponse(
                    success=False,
                    error=error_msg,
                    execution_time_ms=execution_time,
                    metadata={
                        "agent_id": self.config.id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "task_type": task.split(":")[0] if ":" in task else "general",
                        "error_type": e.__class__.__name__
                    }
                )
    
    async def _process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implement task processing logic in subclasses."""
        raise NotImplementedError("Subclasses must implement _process_task")
    
    async def analyze_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and understand the task."""
        raise NotImplementedError("Subclasses must implement analyze_task")
    
    async def create_plan(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an execution plan based on task analysis."""
        raise NotImplementedError("Subclasses must implement create_plan")
    
    async def execute_plan(self, plan: List[Dict[str, Any]], context: Dict[str, Any]) -> Any:
        """Execute the given plan."""
        results = []
        
        for step in plan:
            try:
                result = await self.execute_step(step, context)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing step {step}: {str(e)}")
                raise
                
        return results
    
    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a single step in the plan."""
        step_type = step.get('type')
        
        if step_type == 'tool':
            tool_name = step.get('tool')
            if tool_name not in self.tools:
                raise ValueError(f"Tool not found: {tool_name}")
            return await self.tools[tool_name].execute(step.get('params', {}))
            
        elif step_type == 'llm':
            # Execute an LLM call
            prompt = step.get('prompt')
            if not prompt:
                raise ValueError("LLM step requires a prompt")
                
            return await self.llm.generate(prompt, step.get('options', {}))
            
        else:
            # Default implementation for other step types
            return step
    
    def format_response(self, result: Any) -> AgentResponse:
        """Format the final response."""
        return AgentResponse(
            success=True,
            output=result,
            metadata={
                'agent': self.config.name,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def add_tool(self, tool_name: str, tool: Any):
        """Add a tool to the agent."""
        self.tools[tool_name] = tool
        
    def get_tool(self, tool_name: str) -> Any:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def update_memory(self, key: str, value: Any):
        """Update the agent's memory."""
        self.memory[key] = value
        
    def get_memory(self, key: str, default: Any = None) -> Any:
        """Get a value from the agent's memory."""
        return self.memory.get(key, default)
