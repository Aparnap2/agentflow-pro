"""Orchestrator for managing agent workflows."""
from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime, timedelta
import json
import uuid

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint import BaseCheckpointSaver

from .builder import WorkflowBuilder
from .state import AgentState, WorkflowState, OrchestrationState, TaskStatus
from ..services.memory import GraphitiMemoryService
from ..services.rag import QdrantRAGService

logger = logging.getLogger(__name__)

class LangGraphOrchestrator:
    """Orchestrates agent workflows using LangGraph."""
    
    def __init__(
        self,
        memory_service: Optional[GraphitiMemoryService] = None,
        rag_service: Optional[QdrantRAGService] = None,
        checkpoint: Optional[BaseCheckpointSaver] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the orchestrator.
        
        Args:
            memory_service: Service for agent memory operations
            rag_service: Service for retrieval-augmented generation
            checkpoint: Checkpoint saver for workflow state persistence
            config: Additional configuration
        """
        self.memory_service = memory_service or GraphitiMemoryService()
        self.rag_service = rag_service or QdrantRAGService()
        self.checkpoint = checkpoint
        self.config = config or {}
        
        # Initialize workflow builder
        self.workflow_builder = WorkflowBuilder(
            memory_service=self.memory_service,
            rag_service=self.rag_service,
            checkpoint=self.checkpoint
        )
        
        # Build default workflow
        self.default_workflow = self.workflow_builder.build_workflow("default")
    
    async def process_task(
        self,
        task: Dict[str, Any],
        user_id: str,
        workflow_name: str = "default"
    ) -> Dict[str, Any]:
        """Process a task using the agent workflow.
        
        Args:
            task: Task to process
            user_id: ID of the user submitting the task
            workflow_name: Name of the workflow to use
            
        Returns:
            Task response with results or error
        """
        task_id = task.get("task_id") or str(uuid.uuid4())
        logger.info(f"Processing task {task_id} with workflow '{workflow_name}' for user {user_id}")
        
        try:
            # Add user context to task
            task["user_id"] = user_id
            task["task_id"] = task_id
            task["created_at"] = datetime.utcnow().isoformat()
            
            # Execute the workflow
            result = await self.workflow_builder.execute_workflow(
                task=task,
                workflow_name=workflow_name,
                config={
                    "configurable": {
                        "user_id": user_id,
                        "task_id": task_id,
                        "workflow_name": workflow_name
                    }
                }
            )
            
            # Check for errors
            if result["status"] == "failed":
                logger.error(f"Workflow execution failed: {result.get('error')}")
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "task_id": task_id
                }
            
            # Extract final state
            final_state = result.get("result", {})
            
            # Format the response
            return self._format_response(final_state, task_id)
            
        except Exception as e:
            logger.exception(f"Error processing task {task_id}")
            return {
                "status": "error",
                "error": str(e),
                "task_id": task_id
            }
    
    def _format_response(self, state: Union[AgentState, Dict], task_id: str) -> Dict[str, Any]:
        """Format the workflow response.
        
        Args:
            state: Final agent state
            task_id: Task ID
            
        Returns:
            Formatted response dictionary
        """
        if isinstance(state, dict):
            state = AgentState(**state)
            
        # Extract messages
        messages = []
        for msg in state.messages:
            if hasattr(msg, "content"):
                messages.append({
                    "role": "assistant" if hasattr(msg, "type") and msg.type == "ai" else "user",
                    "content": msg.content,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Extract reasoning steps
        reasoning_steps = []
        for step in state.reasoning_steps:
            if isinstance(step, dict):
                reasoning_steps.append(step)
            else:
                reasoning_steps.append({"step": str(step)})
        
        # Build the response
        response = {
            "status": "success",
            "task_id": task_id,
            "agent_id": state.agent_id,
            "messages": messages,
            "reasoning_steps": reasoning_steps,
            "context": state.context,
            "next_agent": state.next_agent,
            "escalated": state.escalate,
            "completed": state.final_result is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add final result if available
        if state.final_result is not None:
            response["result"] = state.final_result
            
        return response
    
    async def get_workflow_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Status information
        """
        # This would typically check a database or the checkpoint store
        # For now, we'll return a placeholder
        return {
            "task_id": task_id,
            "status": "completed",  # Placeholder
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cancel_workflow(self, task_id: str) -> Dict[str, Any]:
        """Cancel a running workflow.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            Cancellation status
        """
        # This would typically update the task status in a database
        # and signal the workflow to stop
        return {
            "task_id": task_id,
            "status": "cancelled",
            "timestamp": datetime.utcnow().isoformat()
        }
