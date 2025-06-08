"""
Integration with Langfuse for monitoring and observability.
"""
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic, Type
import logging
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime
import os

from pydantic import BaseModel, Field

# Optional import - only required if langfuse is installed
try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler
    from langfuse.model import (
        CreateTrace,
        CreateSpan,
        CreateGeneration,
        CreateEvent,
        CreateScore
    )
    LANGFLUSE_AVAILABLE = True
except ImportError:
    LANGFLUSE_AVAILABLE = False
    # Create mock classes for type checking
    class Langfuse:
        pass
    
    class CallbackHandler:
        pass

logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar('T')

class LangfuseConfig(BaseModel):
    """Configuration for Langfuse integration."""
    public_key: Optional[str] = Field(
        default=os.getenv("LANGFUSE_PUBLIC_KEY"),
        description="Langfuse public key"
    )
    secret_key: Optional[str] = Field(
        default=os.getenv("LANGFUSE_SECRET_KEY"),
        description="Langfuse secret key"
    )
    host: str = Field(
        default=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        description="Langfuse host URL"
    )
    flush_at: int = Field(
        default=100,
        description="Number of events to batch before sending to Langfuse"
    )
    flush_interval: int = Field(
        default=5,
        description="Interval in seconds to flush events to Langfuse"
    )
    enabled: bool = Field(
        default=True,
        description="Whether Langfuse is enabled"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug logging"
    )

class LangfuseIntegration:
    """Handles integration with Langfuse for monitoring and observability."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = LangfuseConfig(**(config or {}))
        self._langfuse = None
        self._handler_cache = {}
        
        if not self.config.enabled:
            logger.info("Langfuse integration is disabled")
            return
            
        if not LANGFLUSE_AVAILABLE:
            logger.warning(
                "Langfuse Python SDK not installed. Install with: pip install langfuse"
            )
            self.config.enabled = False
            return
        
        try:
            self._langfuse = Langfuse(
                public_key=self.config.public_key,
                secret_key=self.config.secret_key,
                host=self.config.host,
                debug=self.config.debug,
                flush_at=self.config.flush_at,
                flush_interval=self.config.flush_interval
            )
            logger.info("Langfuse integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {str(e)}")
            self.config.enabled = False
    
    @property
    def is_enabled(self) -> bool:
        """Check if Langfuse integration is enabled."""
        return self.config.enabled and self._langfuse is not None
    
    def get_handler(self, trace_id: str) -> Optional[CallbackHandler]:
        """Get or create a Langfuse callback handler for a trace."""
        if not self.is_enabled or not trace_id:
            return None
            
        if trace_id not in self._handler_cache:
            self._handler_cache[trace_id] = CallbackHandler(
                public_key=self.config.public_key,
                secret_key=self.config.secret_key,
                host=self.config.host,
                trace_name=trace_id,
                trace_id=trace_id
            )
        
        return self._handler_cache[trace_id]
    
    @asynccontextmanager
    async def trace(
        self,
        name: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Context manager for creating a trace."""
        if not self.is_enabled:
            yield None
            return
        
        trace = self._langfuse.trace(
            CreateTrace(
                name=name,
                id=trace_id,
                metadata=metadata or {},
                **kwargs
            )
        )
        
        try:
            yield trace
        except Exception as e:
            trace.event(
                name="error",
                input={"error": str(e)},
                level="error"
            )
            raise
        finally:
            trace.update(
                end_time=datetime.utcnow()
            )
            self._langfuse.flush()
    
    async def log_agent_execution(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """Log an agent execution to Langfuse."""
        if not self.is_enabled:
            return None
        
        trace_id = trace_id or f"agent_{agent_id}_{datetime.utcnow().isoformat()}"
        
        try:
            with self.trace(
                name=f"Agent Execution: {agent_id}",
                trace_id=trace_id,
                metadata={"agent_id": agent_id, **(metadata or {})}
            ) as trace:
                # Log the input
                trace.span(
                    name="agent_input",
                    input=input_data,
                    metadata={"agent_id": agent_id}
                )
                
                # Log the output
                trace.span(
                    name="agent_output",
                    output=output_data,
                    metadata={"agent_id": agent_id}
                )
                
                # Log any metrics
                if "metrics" in output_data:
                    for metric_name, metric_value in output_data["metrics"].items():
                        trace.score(
                            name=metric_name,
                            value=float(metric_value),
                            comment=f"Agent metric: {metric_name}"
                        )
                
                return trace_id
                
        except Exception as e:
            logger.error(f"Failed to log agent execution to Langfuse: {str(e)}")
            return None
    
    async def log_workflow_execution(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """Log a workflow execution to Langfuse."""
        if not self.is_enabled:
            return None
        
        trace_id = trace_id or f"workflow_{workflow_id}_{datetime.utcnow().isoformat()}"
        
        try:
            with self.trace(
                name=f"Workflow Execution: {workflow_id}",
                trace_id=trace_id,
                metadata={"workflow_id": workflow_id, **(metadata or {})}
            ) as trace:
                # Log the workflow input
                trace.span(
                    name="workflow_input",
                    input=input_data,
                    metadata={"workflow_id": workflow_id}
                )
                
                # Log each step
                for step in steps:
                    step_span = trace.span(
                        name=f"step_{step.get('step_id', 'unknown')}",
                        input=step.get("input", {}),
                        output=step.get("output", {}),
                        metadata={
                            "step_id": step.get("step_id"),
                            "status": step.get("status"),
                            "start_time": step.get("start_time"),
                            "end_time": step.get("end_time"),
                        }
                    )
                    
                    # Log any step metrics
                    if "metrics" in step:
                        for metric_name, metric_value in step["metrics"].items():
                            step_span.score(
                                name=metric_name,
                                value=float(metric_value),
                                comment=f"Step metric: {metric_name}"
                            )
                
                # Log the workflow output
                trace.span(
                    name="workflow_output",
                    output=output_data,
                    metadata={"workflow_id": workflow_id}
                )
                
                return trace_id
                
        except Exception as e:
            logger.error(f"Failed to log workflow execution to Langfuse: {str(e)}")
            return None
