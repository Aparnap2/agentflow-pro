"""
LangGraph Integration Module

This module provides integration with LangGraph for advanced workflow orchestration.
It enables the creation and execution of complex workflows with support for
state management, error handling, and observability.
"""

import logging
import time
from enum import Enum
from typing import Dict, List, Optional, Any, Type, Callable, Union, TypeVar, Tuple, Set
from functools import wraps
from datetime import datetime

from pydantic import BaseModel, Field, validator, root_validator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.prebuilt import ToolNode

from ..agents.base_agent import BaseAgent, AgentConfig
from ..workflow.workflow_manager import Workflow, BaseWorkflowStep, WorkflowContext
from ...core.config import settings

logger = logging.getLogger(__name__)

# Type variables for generic type hints
T = TypeVar('T')
StateType = Dict[str, Any]

def handle_langgraph_errors(func: Callable) -> Callable:
    """
    Decorator to handle common LangGraph errors with proper logging.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as ve:
            logger.error(f"Validation error in {func.__name__}: {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise RuntimeError(f"LangGraph operation failed: {str(e)}")
    return wrapper

class LangGraphNodeType(str, Enum):
    """
    Types of nodes supported in a LangGraph workflow.
    
    Attributes:
        AGENT: Represents an agent node
        TOOL: Represents a tool node
        CONDITIONAL: Represents a conditional node for branching
        TASK: Represents a task node
        ROUTER: Represents a router node for dynamic routing
    """
    AGENT = "agent"
    TOOL = "tool"
    CONDITIONAL = "conditional"
    TASK = "task"
    ROUTER = "router"

class LangGraphEdge(BaseModel):
    """
    Represents a directed edge between two nodes in a LangGraph.
    
    Attributes:
        source: Source node ID
        target: Target node ID
        condition: Optional condition for conditional edges
        weight: Optional weight for the edge (used in routing)
    """
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    condition: Optional[Union[str, Callable]] = Field(
        None,
        description="Condition for conditional edges"
    )
    weight: float = Field(
        1.0,
        description="Weight for the edge (used in routing)",
        ge=0.0,
        le=1.0
    )
    
    @validator('source', 'target')
    def validate_node_id(cls, v):
        """Validate that node IDs are non-empty strings."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("Node ID must be a non-empty string")
        return v.strip()

class LangGraphNode(BaseModel):
    """
    Represents a node in a LangGraph workflow.
    
    Attributes:
        node_id: Unique identifier for the node
        node_type: Type of the node (from LangGraphNodeType)
        config: Configuration for the node
        agent_id: ID of the agent (for AGENT nodes)
        tool_name: Name of the tool (for TOOL nodes)
        condition: Condition for CONDITIONAL nodes
        description: Optional description of the node
    """
    node_id: str = Field(..., description="Unique identifier for the node")
    node_type: LangGraphNodeType = Field(..., description="Type of the node")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for the node"
    )
    agent_id: Optional[str] = Field(
        None,
        description="ID of the agent (for AGENT nodes)"
    )
    tool_name: Optional[str] = Field(
        None,
        description="Name of the tool (for TOOL nodes)"
    )
    condition: Optional[Union[str, Callable]] = Field(
        None,
        description="Condition for CONDITIONAL nodes"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the node"
    )
    
    @root_validator
    def validate_node_config(cls, values):
        """Validate node configuration based on node type."""
        node_type = values.get('node_type')
        
        if node_type == LangGraphNodeType.AGENT and not values.get('agent_id'):
            raise ValueError("AGENT nodes require an agent_id")
            
        if node_type == LangGraphNodeType.TOOL and not values.get('tool_name'):
            raise ValueError("TOOL nodes require a tool_name")
            
        if node_type == LangGraphNodeType.CONDITIONAL and not values.get('condition'):
            raise ValueError("CONDITIONAL nodes require a condition")
            
        return values

class LangGraphConfig(BaseModel):
    """
    Configuration for a LangGraph workflow.
    
    Attributes:
        checkpoint_saver: Checkpoint saver for workflow state persistence
        max_iterations: Maximum number of iterations for workflow execution
        debug: Enable debug mode for detailed logging
        validate_graph: Validate the workflow graph before execution
        allow_cycles: Whether to allow cycles in the workflow graph
        default_timeout: Default timeout for node execution in seconds
    """
    checkpoint_saver: Optional[BaseCheckpointSaver] = Field(
        None,
        description="Checkpoint saver for workflow state persistence"
    )
    max_iterations: int = Field(
        10,
        description="Maximum number of iterations for workflow execution",
        gt=0
    )
    debug: bool = Field(
        settings.DEBUG,
        description="Enable debug mode for detailed logging"
    )
    validate_graph: bool = Field(
        True,
        description="Validate the workflow graph before execution"
    )
    allow_cycles: bool = Field(
        False,
        description="Whether to allow cycles in the workflow graph"
    )
    default_timeout: Optional[float] = Field(
        60.0,
        description="Default timeout for node execution in seconds",
        gt=0.0
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('max_iterations')
    def validate_max_iterations(cls, v):
        """Ensure max_iterations is positive."""
        if v <= 0:
            raise ValueError("max_iterations must be greater than 0")
        return v
    
    @validator('default_timeout')
    def validate_timeout(cls, v):
        """Ensure timeout is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("timeout must be greater than 0")
        return v

class LangGraphIntegration:
    """
    Integration class for LangGraph workflow orchestration.
    
    This class provides methods to create, manage, and execute LangGraph workflows
    with support for agents, tools, and custom nodes.
    
    Args:
        agent_factory: Factory for creating and managing agents
        config: Configuration for the LangGraph integration
    """
    
    def __init__(
        self,
        agent_factory,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_factory = agent_factory
        self.config = LangGraphConfig(**(config or {}))
        self.graphs: Dict[str, StateGraph] = {}
        self._node_registry: Dict[str, LangGraphNode] = {}
        self._edge_registry: Dict[Tuple[str, str], LangGraphEdge] = {}
        logger.info("LangGraph Integration initialized")
    
    @handle_langgraph_errors
    def add_node(self, node: LangGraphNode) -> None:
        """
        Add a node to the graph.
        
        Args:
            node: The node to add
            
        Raises:
            ValueError: If a node with the same ID already exists
        """
        if node.node_id in self._node_registry:
            raise ValueError(f"Node with ID '{node.node_id}' already exists")
        self._node_registry[node.node_id] = node
    
    @handle_langgraph_errors
    def add_edge(self, edge: LangGraphEdge) -> None:
        """
        Add an edge between two nodes.
        
        Args:
            edge: The edge to add
            
        Raises:
            ValueError: If source or target node doesn't exist
        """
        if edge.source not in self._node_registry:
            raise ValueError(f"Source node '{edge.source}' not found")
        if edge.target not in self._node_registry and edge.target != END:
            raise ValueError(f"Target node '{edge.target}' not found")
        
        self._edge_registry[(edge.source, edge.target)] = edge
    
    @handle_langgraph_errors
    def create_graph(self, graph_id: str, config: Optional[Dict[str, Any]] = None) -> StateGraph:
        """
        Create a new LangGraph workflow.
        
        Args:
            graph_id: Unique identifier for the graph
            config: Configuration for the graph
            
        Returns:
            The created StateGraph
            
        Raises:
            ValueError: If a graph with the same ID already exists
            RuntimeError: If graph creation fails
        """
        if graph_id in self.graphs:
            raise ValueError(f"Graph with ID '{graph_id}' already exists")
        
        graph_config = LangGraphConfig(**(config or {}))
        
        try:
            # Create a new graph with the specified state specification
            graph = StateGraph(
                state_spec=dict,
                checkpointer=graph_config.checkpoint_saver
            )
            
            # Add nodes to the graph
            node_mapping = {}
            for node_id, node in self._node_registry.items():
                if node.node_type == LangGraphNodeType.AGENT:
                    # Create an agent node
                    agent = self.agent_factory.get_agent(node.agent_id)
                    if not agent:
                        raise ValueError(f"Agent '{node.agent_id}' not found")
                    
                    # Create a function that calls the agent with proper error handling
                    async def agent_node(state: StateType, agent=agent, node_id=node_id):
                        try:
                            logger.debug(f"Executing agent node: {node_id}")
                            result = await agent.process(state)
                            return {"output": result}
                        except Exception as e:
                            logger.error(f"Error in agent node {node_id}: {str(e)}", exc_info=True)
                            return {"error": str(e), "status": "failed"}
                    
                    graph.add_node(node_id, agent_node)
                    node_mapping[node_id] = node
                
                elif node.node_type == LangGraphNodeType.TOOL:
                    # Create a tool node
                    tool = self.agent_factory.get_tool(node.tool_name)
                    if not tool:
                        raise ValueError(f"Tool '{node.tool_name}' not found")
                    
                    tool_node = ToolNode([tool])
                    graph.add_node(node_id, tool_node)
                    node_mapping[node_id] = node
                
                # Add support for other node types as needed
                else:
                    logger.warning(f"Unsupported node type: {node.node_type}")
            
            # Add edges to the graph
            for (source, target), edge in self._edge_registry.items():
                if edge.condition:
                    graph.add_conditional_edges(
                        source,
                        edge.condition,
                        {target: target}
                    )
                else:
                    graph.add_edge(source, target)
            
            # Set the entry point if nodes exist
            if self._node_registry:
                entry_node = next(iter(self._node_registry.keys()))
                graph.set_entry_point(entry_node)
            
            # Always set the finish point
            graph.set_finish_point(END)
            
            # Compile the graph
            compiled_graph = graph.compile()
            self.graphs[graph_id] = compiled_graph
            
            logger.info(f"Created LangGraph workflow: {graph_id} with {len(self._node_registry)} nodes and {len(self._edge_registry)} edges")
            return compiled_graph
            
        except Exception as e:
            error_msg = f"Failed to create LangGraph: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    @handle_langgraph_errors
    async def execute_graph(
        self,
        graph_id: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a LangGraph workflow with the given input data.
        
        Args:
            graph_id: ID of the graph to execute
            input_data: Input data for the workflow
            config: Additional configuration for execution
            
        Returns:
            Dictionary containing the execution result and metadata
            
        Raises:
            ValueError: If the graph is not found
            RuntimeError: If execution fails
        """
        if graph_id not in self.graphs:
            # Try to compile the graph if it hasn't been compiled yet
            try:
                self.create_graph(graph_id, config)
            except Exception as e:
                raise ValueError(f"Graph '{graph_id}' not found and could not be compiled: {str(e)}")
        
        graph = self.graphs[graph_id]
        
        try:
            # Prepare execution configuration
            exec_config = {
                "recursion_limit": self.config.max_iterations,
                "configurable": {
                    "thread_id": f"thread_{int(time.time())}"
                }
            }
            
            if config:
                exec_config.update(config)
            
            # Execute the graph
            start_time = time.time()
            result = await graph.ainvoke(input_data, exec_config)
            duration = time.time() - start_time
            
            logger.info(f"Executed LangGraph '{graph_id}' in {duration:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "graph_id": graph_id,
                    "duration": duration,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            error_msg = f"Error executing graph '{graph_id}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "success": False,
                "error": error_msg,
                "metadata": {
                    "graph_id": graph_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
    
    def get_graph_status(self, graph_id: str) -> Dict[str, Any]:
        """
        Get the status of a graph.
        
        Args:
            graph_id: ID of the graph
            
        Returns:
            Dictionary containing graph status information
            
        Raises:
            ValueError: If the graph is not found
        """
        if graph_id not in self.graphs:
            raise ValueError(f"Graph '{graph_id}' not found")
        
        return {
            "graph_id": graph_id,
            "node_count": len(self._node_registry),
            "edge_count": len(self._edge_registry),
            "is_compiled": True,
            "config": self.config.dict()
        }

class LangGraphWorkflowStep(BaseWorkflowStep):
    """
    Workflow step that executes a LangGraph workflow.
    
    This class provides a way to integrate LangGraph workflows into larger
    workflow systems with proper error handling and state management.
    
    Args:
        name: Name of the workflow step
        graph_id: ID of the LangGraph to execute
        input_mapping: Mapping of input parameters to graph inputs
        output_mapping: Mapping of graph outputs to step outputs
        config: Additional configuration for the workflow step
        **kwargs: Additional keyword arguments for the base class
    """
    
    def __init__(
        self,
        name: str,
        graph_id: str,
        input_mapping: Optional[Dict[str, str]] = None,
        output_mapping: Optional[Dict[str, str]] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.graph_id = graph_id
        self.input_mapping = input_mapping or {}
        self.output_mapping = output_mapping or {}
        self.config = config or {}
        self._execution_count = 0
        self._success_count = 0
        self._error_count = 0
        self._total_duration = 0.0
        self._last_execution: Optional[datetime] = None
        
    def _prepare_inputs(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Prepare inputs for the LangGraph execution.
        
        Args:
            context: Current workflow context
            
        Returns:
            Dictionary of prepared inputs
        """
        inputs = {}
        
        # Apply input mapping if provided
        if self.input_mapping:
            for input_key, context_key in self.input_mapping.items():
                if context_key in context.data:
                    inputs[input_key] = context.data[context_key]
        else:
            # Default behavior: pass all context data
            inputs.update(context.data)
            
        return inputs
        
    def _process_outputs(
        self,
        result: Dict[str, Any],
        context: WorkflowContext
    ) -> Dict[str, Any]:
        """
        Process the outputs from the LangGraph execution.
        
        Args:
            result: Raw result from LangGraph execution
            context: Current workflow context
            
        Returns:
            Processed outputs
        """
        outputs = {}
        
        # Apply output mapping if provided
        if self.output_mapping:
            for output_key, result_key in self.output_mapping.items():
                if result_key in result:
                    outputs[output_key] = result[result_key]
        else:
            # Default behavior: pass all result data
            outputs.update(result)
            
        return outputs
        
    async def _execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute the LangGraph workflow step.
        
        Args:
            context: Current workflow context
            
        Returns:
            Dictionary containing the execution result and metadata
        """
        start_time = time.time()
        self._execution_count += 1
        
        try:
            # Get the LangGraph integration from the context
            langgraph = context.integrations.get("langgraph")
            if not langgraph:
                raise ValueError("LangGraph integration not found in context")
                
            # Prepare inputs
            inputs = self._prepare_inputs(context)
            
            # Execute the graph
            result = await langgraph.execute_graph(
                graph_id=self.graph_id,
                input_data={"input": inputs},
                config=self.config
            )
            
            # Process outputs
            outputs = self._process_outputs(result.get("result", {}), context)
            
            # Update metrics
            duration = time.time() - start_time
            self._success_count += 1
            self._total_duration += duration
            self._last_execution = datetime.utcnow()
            
            return {
                "status": "completed",
                "outputs": outputs,
                "metadata": {
                    "graph_id": self.graph_id,
                    "duration": duration,
                    "timestamp": self._last_execution.isoformat(),
                    "execution_count": self._execution_count,
                    "success_count": self._success_count,
                    "error_count": self._error_count,
                    "avg_duration": self._total_duration / self._execution_count
                }
            }
            
        except Exception as e:
            # Update error metrics
            self._error_count += 1
            duration = time.time() - start_time
            self._last_execution = datetime.utcnow()
            
            error_msg = f"Error in LangGraphWorkflowStep '{self.name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "status": "failed",
                "error": error_msg,
                "metadata": {
                    "graph_id": self.graph_id,
                    "duration": duration,
                    "timestamp": self._last_execution.isoformat(),
                    "execution_count": self._execution_count,
                    "success_count": self._success_count,
                    "error_count": self._error_count,
                    "last_error": str(e)
                }
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get execution metrics for this workflow step.
        
        Returns:
            Dictionary containing execution metrics
        """
        return {
            "execution_count": self._execution_count,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "total_duration": self._total_duration,
            "avg_duration": self._total_duration / self._execution_count if self._execution_count > 0 else 0.0,
            "last_execution": self._last_execution.isoformat() if self._last_execution else None,
            "graph_id": self.graph_id
        }
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.graph_id = graph_id
        self.input_mapping = input_mapping or {}
    
    async def _execute(self, context: WorkflowContext) -> Dict[str, Any]:
        """Execute the workflow step using the specified LangGraph."""
        # Get the LangGraph integration
        langgraph = self.config.get("langgraph_integration")
        if not langgraph or not isinstance(langgraph, LangGraphIntegration):
            raise ValueError("LangGraph integration not available")
        
        # Prepare input data
        input_data = {}
        for target_key, source_key in self.input_mapping.items():
            if source_key in context.data:
                input_data[target_key] = context.data[source_key]
        
        # Execute the graph
        result = await langgraph.execute_graph(
            graph_id=self.graph_id,
            input_data=input_data
        )
        
        if not result.get("success"):
            raise ValueError(f"Failed to execute graph {self.graph_id}: {result.get('error')}")
        
        # Update the context with the result
        return {"result": result["result"]}
