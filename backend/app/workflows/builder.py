"""Workflow builder for creating agent workflows with LangGraph."""
from typing import Dict, Any, List, Optional, Callable, Type
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState, WorkflowState, OrchestrationState, TaskStatus
from ..agents import get_agent, load_agent_configs
import logging

logger = logging.getLogger(__name__)

class WorkflowBuilder:
    """Builder for creating and managing agent workflows."""
    
    def __init__(self, memory_service, rag_service, checkpoint: Optional[BaseCheckpointSaver] = None):
        """Initialize the workflow builder.
        
        Args:
            memory_service: Service for agent memory operations
            rag_service: Service for retrieval-augmented generation
            checkpoint: Optional checkpoint saver for workflow state persistence
        """
        self.memory_service = memory_service
        self.rag_service = rag_service
        self.checkpoint = checkpoint or MemorySaver()
        self.agent_configs = load_agent_configs()
        self.workflows: Dict[str, Any] = {}
    
    def build_workflow(self, name: str = "default") -> StateGraph:
        """Build and compile the agent workflow.
        
        Args:
            name: Name of the workflow to build
            
        Returns:
            Compiled workflow
        """
        # Create a new workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        self._add_agent_nodes(workflow)
        
        # Define the workflow edges
        self._define_workflow_edges(workflow)
        
        # Set the entry point
        workflow.set_entry_point("cofounder")
        
        # Compile the workflow with checkpointing
        compiled_workflow = workflow.compile(checkpointer=self.checkpoint)
        self.workflows[name] = compiled_workflow
        
        return compiled_workflow
    
    def _add_agent_nodes(self, workflow: StateGraph) -> None:
        """Add nodes for all agents to the workflow.
        
        Args:
            workflow: The workflow graph to add nodes to
        """
        for agent_id, config in self.agent_configs.items():
            # Create agent instance
            agent = get_agent(agent_id, config, self.memory_service, self.rag_service)
            
            # Add node to workflow
            workflow.add_node(agent_id, agent.process)
    
    def _define_workflow_edges(self, workflow: StateGraph) -> None:
        """Define the edges between agent nodes in the workflow.
        
        Args:
            workflow: The workflow graph to add edges to
        """
        # Helper function to determine next agent
        def route_agent(state: AgentState) -> str:
            if state.escalate:
                # Escalate to cofounder
                return "cofounder"
            elif state.next_agent and state.next_agent in self.agent_configs:
                # Route to specified agent
                return state.next_agent
            # End the workflow if no next agent specified
            return END
        
        # Define edges for each agent
        for agent_id in self.agent_configs.keys():
            # Get possible next agents (all agents + END)
            possible_next = list(self.agent_configs.keys()) + [END]
            
            # Add conditional edges
            workflow.add_conditional_edges(
                agent_id,
                route_agent,
                possible_next
            )
    
    def get_workflow(self, name: str = "default"):
        """Get a compiled workflow by name.
        
        Args:
            name: Name of the workflow to retrieve
            
        Returns:
            The compiled workflow
        """
        if name not in self.workflows:
            raise ValueError(f"Workflow '{name}' not found. Available workflows: {list(self.workflows.keys())}")
        return self.workflows[name]
    
    async def execute_workflow(
        self, 
        task: Dict[str, Any], 
        workflow_name: str = "default",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow with the given task.
        
        Args:
            task: Task to execute
            workflow_name: Name of the workflow to execute
            config: Additional configuration for the workflow execution
            
        Returns:
            Result of the workflow execution
        """
        try:
            # Get the workflow
            workflow = self.get_workflow(workflow_name)
            
            # Create initial state
            initial_state = self._create_initial_state(task)
            
            # Execute the workflow
            result = await workflow.ainvoke(
                initial_state,
                config=config or {"configurable": {"thread_id": task.get("task_id", "default")}}
            )
            
            return {
                "status": "completed",
                "result": result,
                "workflow_name": workflow_name
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow '{workflow_name}': {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "workflow_name": workflow_name
            }
    
    def _create_initial_state(self, task: Dict[str, Any]) -> AgentState:
        """Create the initial state for a workflow execution.
        
        Args:
            task: Task to create state for
            
        Returns:
            Initial agent state
        """
        from langchain_core.messages import HumanMessage
        
        # Convert task to AgentState
        return AgentState(
            task_id=task.get("task_id", "default_task"),
            agent_id="cofounder",  # Start with cofounder
            messages=[
                HumanMessage(
                    content=task.get("description", ""),
                    additional_kwargs={
                        "task_metadata": {
                            "title": task.get("title", ""),
                            "priority": task.get("priority", "medium"),
                            "deadline": task.get("deadline"),
                            "tags": task.get("tags", []),
                        }
                    }
                )
            ],
            context={
                "task": task,
                "workflow_start_time": str(datetime.utcnow()),
                "previous_agents": []
            },
            status=TaskStatus.IN_PROGRESS,
            priority=task.get("priority", "medium")
        )

# Example usage:
# builder = WorkflowBuilder(memory_service, rag_service)
# workflow = builder.build_workflow("default")
# result = await builder.execute_workflow({"task_id": "123", "description": "Analyze Q2 sales data"})
