"""
Agent workflow integration for coordinating multiple agents in complex tasks.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Type, Callable, Awaitable, Union
from enum import Enum
from datetime import datetime, timedelta
import json

from pydantic import BaseModel, Field, validator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryCallState
)

from ..agents import BaseAgent, AgentResponse, AgentFactory, AgentError
from .workflow_manager import Workflow, BaseWorkflowStep, WorkflowContext, WorkflowError

logger = logging.getLogger(__name__)

class AgentWorkflowStepType(str, Enum):
    """Types of steps in an agent workflow."""
    AGENT_TASK = "agent_task"
    PARALLEL_TASKS = "parallel_tasks"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    API_CALL = "api_call"
    DATA_TRANSFORM = "data_transform"

class AgentWorkflowStep(BaseModel):
    """A single step in an agent workflow."""
    step_id: str
    name: str
    step_type: AgentWorkflowStepType
    agent_type: Optional[str] = None
    task: Optional[str] = None
    input_template: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[float] = None
    
    @validator('step_type', pre=True)
    def validate_step_type(cls, v):
        if isinstance(v, AgentWorkflowStepType):
            return v
        return AgentWorkflowStepType(v.lower())
    
    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration for this step."""
        default = {
            "stop": stop_after_attempt(3),
            "wait": wait_exponential(multiplier=1, min=1, max=10),
            "retry": retry_if_exception_type((ConnectionError, TimeoutError)),
            "reraise": True
        }
        default.update(self.retry_policy)
        return default

class AgentWorkflowResult(BaseModel):
    """Result of an agent workflow execution."""
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float
    steps: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentWorkflow:
    """Manages the execution of workflows involving multiple agents."""
    
    def __init__(self, workflow_id: str, name: str, agent_factory: AgentFactory):
        self.workflow_id = workflow_id
        self.name = name
        self.agent_factory = agent_factory
        self.steps: Dict[str, AgentWorkflowStep] = {}
        self.workflow = Workflow(workflow_id, name)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the workflow and its dependencies."""
        if not self._initialized:
            await self.agent_factory.initialize()
            self._initialized = True
    
    def add_step(self, step: AgentWorkflowStep) -> 'AgentWorkflow':
        """Add a step to the workflow."""
        if step.step_id in self.steps:
            raise ValueError(f"Step with ID {step.step_id} already exists")
        
        self.steps[step.step_id] = step
        
        # Create a workflow step that will be executed
        workflow_step = AgentTaskStep(
            name=step.name,
            step_id=step.step_id,
            agent_factory=self.agent_factory,
            workflow_step=step
        )
        
        self.workflow.add_step(workflow_step)
        return self
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentWorkflowResult:
        """
        Execute the workflow with the given input data and context.
        
        Args:
            input_data: Input data for the workflow
            context: Additional context for the workflow execution
            
        Returns:
            AgentWorkflowResult: The result of the workflow execution
        """
        start_time = datetime.utcnow()
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Prepare execution context
            exec_context = {
                "input": input_data,
                "context": context or {},
                "start_time": start_time.isoformat(),
                "workflow_id": self.workflow_id,
                "steps": {}
            }
            
            # Execute the workflow
            result = await self.workflow.execute(exec_context)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AgentWorkflowResult(
                success=result.success,
                output=result.output,
                error=result.error,
                execution_time_ms=execution_time,
                steps=exec_context.get("steps", {})
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return AgentWorkflowResult(
                success=False,
                error=error_msg,
                execution_time_ms=execution_time,
                steps=context.get("steps", {}) if context else {}
            )
    
    def validate(self) -> bool:
        """Validate the workflow configuration."""
        # Check for circular dependencies
        visited = set()
        path = set()
        
        def visit(step_id: str):
            if step_id in path:
                raise ValueError(f"Circular dependency detected at step: {step_id}")
            if step_id in visited:
                return
                
            path.add(step_id)
            step = self.steps[step_id]
            
            for dep_id in step.depends_on:
                if dep_id not in self.steps:
                    raise ValueError(f"Dependency {dep_id} not found for step {step_id}")
                visit(dep_id)
                
            path.remove(step_id)
            visited.add(step_id)
        
        for step_id in self.steps:
            if step_id not in visited:
                visit(step_id)
        
        return True

class AgentTaskStep(BaseWorkflowStep):
    """A workflow step that executes an agent task."""
    
    def __init__(
        self,
        name: str,
        step_id: str,
        agent_factory: AgentFactory,
        workflow_step: AgentWorkflowStep,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.step_id = step_id
        self.agent_factory = agent_factory
        self.workflow_step = workflow_step
    
    async def _execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Execute the agent task."""
        step = self.workflow_step
        step_start = datetime.utcnow()
        
        # Prepare step context
        step_context = {
            "start_time": step_start.isoformat(),
            "status": "started",
            "step_id": step.step_id,
            "step_type": step.step_type.value,
            "input": {}
        }
        
        try:
            # Get the agent
            if not step.agent_type:
                raise ValueError(f"Agent type not specified for step {step.step_id}")
                
            agent = await self.agent_factory.get_agent(
                agent_type=step.agent_type,
                agent_id=f"workflow_{context.workflow_id}_{step.step_id}"
            )
            
            if not agent:
                raise ValueError(f"Agent of type {step.agent_type} not found")
            
            # Prepare input data
            input_data = self._prepare_input(step, context.data)
            step_context["input"] = input_data
            
            # Execute the agent task
            task = step.task or "process_task"
            
            # Apply retry policy
            retry_config = step.get_retry_config()
            retry_decorator = retry(**retry_config)
            
            # Execute with timeout if specified
            if step.timeout:
                task_coro = asyncio.wait_for(
                    getattr(agent, task)(**input_data),
                    timeout=step.timeout
                )
            else:
                task_coro = getattr(agent, task)(**input_data)
            
            # Execute with retry
            result = await retry_decorator(task_coro)
            
            # Update step context
            step_context.update({
                "status": "completed",
                "end_time": datetime.utcnow().isoformat(),
                "execution_time_ms": (datetime.utcnow() - step_start).total_seconds() * 1000,
                "success": True,
                "output": result.dict() if hasattr(result, 'dict') else result
            })
            
            # Save the result to the workflow context
            if "steps" not in context.data:
                context.data["steps"] = {}
            context.data["steps"][step.step_id] = step_context
            
            return {
                step.step_id: {
                    "success": True,
                    "output": result,
                    "metadata": {
                        "step_id": step.step_id,
                        "agent_type": step.agent_type,
                        "execution_time_ms": step_context["execution_time_ms"]
                    }
                }
            }
            
        except Exception as e:
            error_msg = f"Step {step.step_id} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            step_context.update({
                "status": "failed",
                "end_time": datetime.utcnow().isoformat(),
                "execution_time_ms": (datetime.utcnow() - step_start).total_seconds() * 1000,
                "success": False,
                "error": error_msg,
                "error_type": e.__class__.__name__
            })
            
            # Save the error to the workflow context
            if "steps" not in context.data:
                context.data["steps"] = {}
            context.data["steps"][step.step_id] = step_context
            
            raise WorkflowError(error_msg) from e
    
    def _prepare_input(self, step: AgentWorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare input data for the agent task."""
        input_data = {}
        
        # Add parameters from the step configuration
        if step.parameters:
            input_data.update(step.parameters)
        
        # Process input template if provided
        if step.input_template:
            try:
                # Simple template processing - in a real implementation, use a proper templating engine
                template = step.input_template
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        template = template.replace(f"{{{{{key}}}}}", str(value))
                
                # Try to parse the result as JSON, otherwise use as is
                try:
                    template_data = json.loads(template)
                    if isinstance(template_data, dict):
                        input_data.update(template_data)
                except json.JSONDecodeError:
                    input_data["input"] = template
                    
            except Exception as e:
                logger.warning(f"Failed to process input template: {str(e)}")
        
        return input_data

# Example usage:
"""
async def example_workflow():
    # Create agent factory
    factory = AgentFactory()
    
    # Create a workflow
    workflow = AgentWorkflow("lead_gen", "Lead Generation Workflow", factory)
    
    # Add steps to the workflow
    workflow.add_step(AgentWorkflowStep(
        step_id="qualify_lead",
        name="Qualify Lead",
        step_type=AgentWorkflowStepType.AGENT_TASK,
        agent_type="sales",
        task="qualify_lead",
        parameters={"priority": "high"},
        retry_policy={"stop": stop_after_attempt(3)}
    ))
    
    workflow.add_step(AgentWorkflowStep(
        step_id="enrich_data",
        name="Enrich Lead Data",
        step_type=AgentWorkflowStepType.AGENT_TASK,
        agent_type="research",
        task="enrich_lead",
        depends_on=["qualify_lead"],
        timeout=30.0  # 30 seconds timeout
    ))
    
    # Execute the workflow
    result = await workflow.execute({
        "lead": {"name": "Acme Corp", "email": "contact@acmecorp.com"}
    })
    
    if result.success:
        print(f"Workflow completed in {result.execution_time_ms:.2f}ms")
        print(json.dumps(result.output, indent=2))
    else:
        print(f"Workflow failed: {result.error}")
"""
