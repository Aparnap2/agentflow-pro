from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Union
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from enum import Enum

# Import integrations
from ..integrations import (
    CrewAIWorkflowStep,
    LangGraphWorkflowStep,
    get_langfuse_integration
)

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStep(BaseModel):
    """Represents a single step in a workflow."""
    step_id: str
    name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowContext(BaseModel):
    """Context that is passed between workflow steps."""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    current_step: Optional[str] = None
    steps: Dict[str, WorkflowStep] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowResult(BaseModel):
    """Result of a workflow execution."""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    context: WorkflowContext
    execution_time_ms: Optional[float] = None

class BaseWorkflowStep(ABC):
    """Base class for all workflow steps."""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs
    
    async def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Execute the workflow step."""
        step_id = f"step_{len(context.steps) + 1}_{self.name}"
        
        # Create a new step in the context
        step = WorkflowStep(
            step_id=step_id,
            name=self.name,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.utcnow(),
            input=context.data.copy()
        )
        
        context.steps[step_id] = step
        context.current_step = step_id
        
        try:
            # Execute the step
            logger.info(f"Executing step: {self.name}")
            result = await self._execute(context)
            
            # Update step status
            step.status = WorkflowStatus.COMPLETED
            step.output = result
            step.end_time = datetime.utcnow()
            
            # Update context with step result
            if result and isinstance(result, dict):
                context.data.update(result)
            
            return context
            
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            logger.error(f"Error in step {self.name}: {error_msg}", exc_info=True)
            
            step.status = WorkflowStatus.FAILED
            step.error = error_msg
            step.end_time = datetime.utcnow()
            
            context.status = WorkflowStatus.FAILED
            context.end_time = datetime.utcnow()
            
            raise WorkflowError(f"Step '{self.name}' failed: {error_msg}")
    
    @abstractmethod
    async def _execute(self, context: WorkflowContext) -> Any:
        """Execute the step logic. To be implemented by subclasses."""
        pass

class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    pass

class Workflow:
    """Manages the execution of a workflow with multiple steps with integrations."""
    
    def __init__(self, workflow_id: str, name: str, metadata: Optional[Dict[str, Any]] = None):
        self.workflow_id = workflow_id
        self.name = name
        self.metadata = metadata or {}
        self.steps: List[BaseWorkflowStep] = []
    
    def add_step(self, step: Union[BaseWorkflowStep, CrewAIWorkflowStep, LangGraphWorkflowStep]) -> None:
        """
        Add a step to the workflow.
        
        Args:
            step: The step to add (can be a regular step, CrewAI step, or LangGraph step)
        """
        self.steps.append(step)
    
    async def execute(
        self, 
        initial_data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> WorkflowResult:
        """
        Execute the workflow with the given initial data and tracing.
        
        Args:
            initial_data: Initial data for the workflow
            trace_id: Optional trace ID for distributed tracing
            
        Returns:
            WorkflowResult containing the execution result
        """
        execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        trace_id = trace_id or f"workflow_{self.workflow_id}_{execution_id}"
        
        context = WorkflowContext(
            workflow_id=self.workflow_id,
            execution_id=execution_id,
            status=WorkflowStatus.RUNNING,
            data=initial_data or {},
            metadata={
                **self.metadata,
                "trace_id": trace_id,
                "workflow_name": self.name
            }
        )
        
        start_time = datetime.utcnow()
        langfuse = get_langfuse_integration()
        
        # Log workflow start to Langfuse
        if langfuse and langfuse.is_enabled:
            await langfuse.log_agent_execution(
                agent_id=f"workflow_{self.workflow_id}",
                input_data={"status": "started", "input": initial_data or {}},
                output_data={"status": "started"},
                trace_id=trace_id,
                metadata={
                    "workflow_id": self.workflow_id,
                    "execution_id": execution_id,
                    "workflow_name": self.name,
                    "step_count": len(self.steps)
                }
            )
        
        executed_steps = []
        
        try:
            for step in self.steps:
                step_start_time = datetime.utcnow()
                step_trace_id = f"{trace_id}_step_{step.name}"
                
                # Log step start to Langfuse
                if langfuse and langfuse.is_enabled:
                    await langfuse.log_agent_execution(
                        agent_id=step.name,
                        input_data=context.data,
                        output_data={"status": "started"},
                        trace_id=step_trace_id,
                        metadata={
                            "workflow_id": self.workflow_id,
                            "execution_id": execution_id,
                            "step_id": step.name,
                            "step_type": step.__class__.__name__
                        }
                    )
                
                try:
                    # Execute the step
                    context = await step.execute(context)
                    
                    # Log step completion
                    step_duration = (datetime.utcnow() - step_start_time).total_seconds()
                    executed_steps.append({
                        "step_id": step.name,
                        "status": "completed",
                        "start_time": step_start_time.isoformat(),
                        "end_time": datetime.utcnow().isoformat(),
                        "duration_seconds": step_duration,
                        "step_type": step.__class__.__name__
                    })
                    
                    # Log step completion to Langfuse
                    if langfuse and langfuse.is_enabled:
                        await langfuse.log_agent_execution(
                            agent_id=step.name,
                            input_data=context.data,
                            output_data={
                                "status": "completed",
                                "duration_seconds": step_duration
                            },
                            trace_id=step_trace_id,
                            metadata={
                                "workflow_id": self.workflow_id,
                                "execution_id": execution_id,
                                "step_id": step.name,
                                "step_type": step.__class__.__name__,
                                "duration_seconds": step_duration
                            }
                        )
                    
                    # If any step fails, stop execution
                    if context.status == WorkflowStatus.FAILED:
                        break
                        
                except Exception as step_error:
                    error_msg = str(step_error)
                    step_duration = (datetime.utcnow() - step_start_time).total_seconds()
                    
                    # Log step failure
                    executed_steps.append({
                        "step_id": step.name,
                        "status": "failed",
                        "start_time": step_start_time.isoformat(),
                        "end_time": datetime.utcnow().isoformat(),
                        "duration_seconds": step_duration,
                        "error": error_msg,
                        "step_type": step.__class__.__name__
                    })
                    
                    # Log step failure to Langfuse
                    if langfuse and langfuse.is_enabled:
                        await langfuse.log_agent_execution(
                            agent_id=step.name,
                            input_data=context.data,
                            output_data={
                                "status": "failed",
                                "error": error_msg,
                                "duration_seconds": step_duration
                            },
                            trace_id=step_trace_id,
                            metadata={
                                "workflow_id": self.workflow_id,
                                "execution_id": execution_id,
                                "step_id": step.name,
                                "step_type": step.__class__.__name__,
                                "error": error_msg,
                                "duration_seconds": step_duration
                            }
                        )
                    
                    context.status = WorkflowStatus.FAILED
                    context.end_time = datetime.utcnow()
                    
                    # Re-raise the error to be handled by the workflow
                    raise WorkflowError(f"Step '{step.name}' failed: {error_msg}") from step_error
            
            # If we get here, all steps completed successfully
            context.status = WorkflowStatus.COMPLETED
            
            # Log workflow completion to Langfuse
            if langfuse and langfuse.is_enabled:
                workflow_duration = (datetime.utcnow() - start_time).total_seconds()
                await langfuse.log_agent_execution(
                    agent_id=f"workflow_{self.workflow_id}",
                    input_data=initial_data or {},
                    output_data={
                        "status": "completed",
                        "output": context.data,
                        "duration_seconds": workflow_duration,
                        "steps": executed_steps
                    },
                    trace_id=trace_id,
                    metadata={
                        "workflow_id": self.workflow_id,
                        "execution_id": execution_id,
                        "workflow_name": self.name,
                        "step_count": len(self.steps),
                        "completed_steps": len([s for s in executed_steps if s["status"] == "completed"]),
                        "failed_steps": len([s for s in executed_steps if s["status"] == "failed"]),
                        "duration_seconds": workflow_duration
                    }
                )
            
        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.end_time = datetime.utcnow()
            workflow_duration = (context.end_time - start_time).total_seconds()
            
            # Log workflow failure to Langfuse
            if langfuse and langfuse.is_enabled:
                await langfuse.log_agent_execution(
                    agent_id=f"workflow_{self.workflow_id}",
                    input_data=initial_data or {},
                    output_data={
                        "status": "failed",
                        "error": str(e),
                        "duration_seconds": workflow_duration,
                        "steps": executed_steps
                    },
                    trace_id=trace_id,
                    metadata={
                        "workflow_id": self.workflow_id,
                        "execution_id": execution_id,
                        "workflow_name": self.name,
                        "error": str(e),
                        "duration_seconds": workflow_duration
                    }
                )
            
            # Log the error
            logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
            
            return WorkflowResult(
                success=False,
                error=str(e),
                context=context,
                execution_time_ms=workflow_duration * 1000 if 'workflow_duration' in locals() else 0
            )
        
        context.end_time = datetime.utcnow()
        workflow_duration = (context.end_time - start_time).total_seconds()
        
        return WorkflowResult(
            success=True,
            output=context.data,
            context=context,
            execution_time_ms=workflow_duration * 1000
        )
