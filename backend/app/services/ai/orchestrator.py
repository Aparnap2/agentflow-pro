import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple, Type, TypeVar, Callable
from enum import Enum
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from loguru import logger
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Tuple, Type, TypeVar, Callable
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from qdrant_client import QdrantClient
from redis.asyncio import Redis
from openrouter import OpenRouter
from crewai import Agent, Task, Crew, Process
from crewai.agents import CrewAgent
from crewai.tasks import TaskOutput
    CREWAI_AVAILABLE = False

# Crawl4AI imports
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# Vector database
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Caching
from upstash_redis import Redis

# Local imports
from ..core.config import settings

# Type hints
typing_extensions = None  # For type checking
TypedDict = dict  # Fallback if typing_extensions not available

try:
    from typing_extensions import TypedDict as TypedDictType
    TypedDict = TypedDictType
except ImportError:
    pass

# Constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300  # 5 minutes

# Memory and Monitoring
class MemoryManager:
    """Manages persistent memory for agents using Graphiti MCP"""
    
    def __init__(self, redis_client, qdrant_client):
        self.redis = redis_client
        self.qdrant = qdrant_client
        self.collection_name = "agent_memory"
        self._init_memory_collection()
    
    def _init_memory_collection(self):
        """Initialize the Qdrant collection for agent memory"""
        try:
            collections = self.qdrant.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "text": models.VectorParams(
                            size=1536,  # OpenAI embedding size
                            distance=models.Distance.COSINE
                        )
                    }
                )
                logger.info(f"Created memory collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing memory collection: {str(e)}")
            raise
    
    async def store_memory(
        self, 
        agent_id: str, 
        memory_data: Dict[str, Any], 
        embedding: Optional[List[float]] = None
    ) -> str:
        """
        Store a memory for an agent
        
        Args:
            agent_id: ID of the agent
            memory_data: Memory data to store
            embedding: Optional embedding for the memory
            
        Returns:
            ID of the stored memory
        """
        memory_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Store in Redis for fast access
        redis_key = f"agent:{agent_id}:memory:{memory_id}"
        await self.redis.set(
            redis_key,
            json.dumps({
                **memory_data,
                "id": memory_id,
                "agent_id": agent_id,
                "timestamp": timestamp
            }),
            ex=86400 * 30  # 30 days TTL
        )
        
        # Store in Qdrant for semantic search if embedding is provided
        if embedding:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=memory_id,
                        vector={"text": embedding},
                        payload={
                            "agent_id": agent_id,
                            "text": memory_data.get("content", ""),
                            "type": memory_data.get("type", "generic"),
                            "timestamp": timestamp,
                            "metadata": memory_data.get("metadata", {})
                        }
                    )
                ]
            )
        
        return memory_id
    
    async def retrieve_memories(
        self,
        agent_id: str,
        query: Optional[str] = None,
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for an agent, optionally filtered by query
        
        Args:
            agent_id: ID of the agent
            query: Optional query for semantic search
            limit: Maximum number of memories to return
            memory_type: Optional memory type filter
            
        Returns:
            List of memories
        """
        if query:
            # Semantic search using Qdrant
            query_embedding = embedding_utils.get_embedding(query)
            
            # Build filter
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="agent_id",
                        match=models.MatchValue(value=agent_id)
                    )
                ]
            )
            
            if memory_type:
                filter_condition.must.append(
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value=memory_type)
                    )
                )
            
            # Search in Qdrant
            search_result = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=("text", query_embedding),
                query_filter=filter_condition,
                limit=limit
            )
            
            # Get full memory data from Redis
            memories = []
            for result in search_result:
                memory_id = result.id
                redis_key = f"agent:{agent_id}:memory:{memory_id}"
                memory_data = await self.redis.get(redis_key)
                if memory_data:
                    memories.append(json.loads(memory_data))
            
            return memories
        else:
            # Simple key-based lookup from Redis
            pattern = f"agent:{agent_id}:memory:*"
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return []
                
            # Get values for all keys
            memory_data = await self.redis.mget(keys)
            memories = [json.loads(data) for data in memory_data if data]
            
            # Filter by type if specified
            if memory_type:
                memories = [m for m in memories if m.get("type") == memory_type]
            
            # Sort by timestamp
            memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return memories[:limit]

class Monitoring:
    """Handles monitoring and observability for the orchestrator"""
    
    def __init__(self):
        self.langfuse = None
        self._setup_monitoring()
    
    def _setup_monitoring(self):
        """Initialize monitoring tools"""
        if LANGFUSE_AVAILABLE and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            self.langfuse = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST or "https://cloud.langfuse.com"
            )
            logger.info("Langfuse monitoring initialized")
    
    def log_agent_execution(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        parent_observation_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Log an agent execution to monitoring tools
        
        Returns:
            Observation ID if monitoring is enabled, None otherwise
        """
        if not self.langfuse:
            return None
            
        try:
            trace = self.langfuse.trace(
                id=trace_id or str(uuid.uuid4()),
                name=f"agent_execution_{agent_name}",
                metadata={"agent": agent_name, **(metadata or {})}
            )
            
            observation = trace.span(
                name=f"agent_{agent_name}",
                input=input_data,
                output=output_data,
                metadata={"agent_type": agent_name}
            )
            
            if parent_observation_id:
                observation.parent_observation_id = parent_observation_id
                
            return observation.id
            
        except Exception as e:
            logger.error(f"Error logging to Langfuse: {str(e)}", exc_info=True)
            return None

# Import Langfuse for monitoring
try:
    from langfuse import Langfuse
    from langfuse.model import CreateTrace
    LANGFUSE_AVAILABLE = True
except ImportError:
    logger.warning("Langfuse not installed. Monitoring will be limited.")
    LANGFUSE_AVAILABLE = False

# Check OpenRouter availability
OPENROUTER_AVAILABLE = hasattr(settings, 'OPENROUTER_API_KEY') and settings.OPENROUTER_API_KEY is not None
if not OPENROUTER_AVAILABLE:
    logger.warning("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your environment.")

# Type variables
T = TypeVar('T')
AgentType = TypeVar('AgentType', bound='BaseAgent')

# Agent Router
class AgentRouter:
    """
    Routes tasks to the most appropriate agent based on the task requirements.
    Implements the router pattern from the PRD.
    """
    
    def __init__(self, orchestrator: 'AIOrchestrator'):
        self.orchestrator = orchestrator
        self.llm = None  # Will be initialized later
        self._setup_router_llm()
    
    def _setup_router_llm(self):
        """Initialize the LLM for routing decisions using OpenRouter"""
        if not OPENROUTER_AVAILABLE:
            raise RuntimeError(
                "OpenRouter is not available. "
                "Please set OPENROUTER_API_KEY in your environment variables."
            )
            
        try:
            # Use deepseek-chat as the default router model
            self.llm = OpenRouterLLM(
                model_name="deepseek-ai/deepseek-chat",
                temperature=0.1,
                max_tokens=1024,
                request_timeout=30  # 30 seconds timeout
            )
            logger.info("Initialized OpenRouter LLM for routing with deepseek-chat model")
            
            # Test the connection
            test_prompt = "Test connection"
            test_messages = [{"role": "user", "content": test_prompt}]
            
            # This will raise an exception if the API key is invalid or there are connection issues
            _ = asyncio.run(self.llm.client.generate(
                model="deepseek-ai/deepseek-chat",
                messages=test_messages,
                max_tokens=10
            ))
            
        except Exception as e:
            error_msg = f"Failed to initialize OpenRouter LLM: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(
                f"Failed to initialize LLM router. {error_msg} "
                "Please check your OpenRouter API key and network connection."
            )
    
    async def route_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to the most appropriate agent.
        
        Args:
            task_description: Description of the task to be routed
            context: Additional context for routing decision
            
        Returns:
            Dict with routing information
        """
        # Get available agents
        available_agents = self.orchestrator.agent_registry.list_agents()
        
        # Create prompt for routing decision
        prompt = f"""You are an intelligent task router. Your job is to determine which agent 
        is best suited to handle the following task. Consider the task description and context 
        to make your decision.
        
        Available Agents: {', '.join(available_agents)}
        
        Task: {task_description}
        
        Context: {context}
        
        Respond with a JSON object containing:
        - agent_name: The name of the best agent to handle this task
        - confidence: Your confidence score (0-1)
        - reasoning: Brief explanation of your choice
        """
        
        try:
            # Get routing decision from LLM
            response = await self.llm.ainvoke(prompt)
            routing_decision = json.loads(response.content)
            
            # Validate response
            if not all(k in routing_decision for k in ["agent_name", "confidence", "reasoning"]):
                raise ValueError("Invalid routing decision format")
                
            # Get agent class
            agent_class = self.orchestrator.agent_registry.get_agent(routing_decision["agent_name"])
            if not agent_class:
                raise ValueError(f"Agent {routing_decision['agent_name']} not found")
                
            return {
                "agent": routing_decision["agent_name"],
                "confidence": float(routing_decision["confidence"]),
                "reasoning": routing_decision["reasoning"],
                "agent_class": agent_class
            }
            
        except Exception as e:
            logger.error(f"Error in task routing: {str(e)}", exc_info=True)
            # Fall back to default routing
            return await self._fallback_route(task_description, context)
    
    async def _fallback_route(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback routing logic when LLM routing fails"""
        # Simple keyword-based routing as fallback
        task_lower = task_description.lower()
        
        # Define keyword to agent mapping
        keyword_mapping = {
            "finance": "finance",
            "budget": "finance",
            "invoice": "finance",
            "support": "support",
            "ticket": "support",
            "help": "support",
            "develop": "developer",
            "code": "developer",
            "bug": "developer",
            "hr": "hr",
            "employee": "hr",
            "analytics": "analytics",
            "report": "analytics",
            "data": "analytics"
        }
        
        # Find matching agent
        for keyword, agent_name in keyword_mapping.items():
            if keyword in task_lower:
                agent_class = self.orchestrator.agent_registry.get_agent(agent_name)
                if agent_class:
                    return {
                        "agent": agent_name,
                        "confidence": 0.7,  # Lower confidence for keyword-based routing
                        "reasoning": f"Matched keyword '{keyword}' to agent '{agent_name}'",
                        "agent_class": agent_class
                    }
        
        # Default to general agent if available
        default_agent = "support" if "support" in self.orchestrator.agent_registry.list_agents() else None
        if default_agent:
            return {
                "agent": default_agent,
                "confidence": 0.5,
                "reasoning": "Defaulted to support agent",
                "agent_class": self.orchestrator.agent_registry.get_agent(default_agent)
            }
            
        raise ValueError("No suitable agent found for the task")

# Agent Registry
class AgentRegistry:
    """Global registry for all available agents"""
    _instance = None
    _agents: Dict[str, Type['BaseAgent']] = {}
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str) -> Callable[[Type[AgentType]], Type[AgentType]]:
        """Decorator to register an agent class"""
        def decorator(agent_cls: Type[AgentType]) -> Type[AgentType]:
            cls._agents[name] = agent_cls
            return agent_cls
        return decorator

    @classmethod
    def get_agent(cls, name: str) -> Optional[Type['BaseAgent']]:
        """Get an agent class by name"""
        return cls._agents.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent names"""
        return list(cls._agents.keys())

# Base Agent Class
class BaseAgent:
    """Base class for all agents"""
    name: str = "base_agent"
    description: str = "Base agent with common functionality"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.memory = {}
        self.trace_id = str(uuid.uuid4())
        self.langfuse = None
        if LANGFUSE_AVAILABLE and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            self.langfuse = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST or "https://cloud.langfuse.com"
            )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def _start_trace(self, name: str, metadata: Optional[Dict] = None) -> Optional[CreateTrace]:
        """Start a new trace for monitoring"""
        if not self.langfuse:
            return None
        return self.langfuse.trace(
            id=self.trace_id,
            name=name,
            metadata=metadata or {}
        )
    
    def _log_event(self, trace: Optional[CreateTrace], name: str, input_data: Dict, output_data: Dict):
        """Log an event to the trace"""
        if not trace:
            return
            
        trace.span(
            name=name,
            input=input_data,
            output=output_data
        )

# Import embedding utilities
from app.ai.embeddings import EmbeddingUtils, embedding_utils
from typing import Literal
from enum import Enum

# Initialize embedding utilities
embedding_utils = EmbeddingUtils()

# State Management
class AgentState(TypedDict):
    """State for individual agent execution"""
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    status: Literal["pending", "processing", "completed", "failed"]
    error: Optional[str]
    metadata: Dict[str, Any]
    timestamp: str

class GraphState(TypedDict):
    """State for the entire workflow graph"""
    # Input from user
    user_input: str
    
    # Agent execution context
    current_agent: Optional[str]
    agent_states: Dict[str, AgentState]
    
    # Workflow metadata
    workflow_id: str
    status: Literal["pending", "running", "completed", "failed"]
    created_at: str
    updated_at: str
    
    # Context and memory
    context: Dict[str, Any]
    memory: Dict[str, Any]
    
    # Error handling
    error: Optional[str]
    retry_count: int
    max_retries: int

# Agent Status Enum
class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

class AIOrchestrator:
    """
    Main orchestrator for managing AI agents and workflows.
    Handles agent registration, workflow execution, and state management.
    """
    
    def __init__(self):
        # Initialize core components
        self.workflow = self._create_workflow()
        self.llm_router = self._setup_llm_router()
        self.agent_registry = AgentRegistry()
        
        # Initialize storage and caching
        self.redis = Redis.from_params(
            url=settings.REDIS_URL,
            token=settings.REDIS_TOKEN
        )
        self.qdrant = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        
        # Initialize state tracking
        self.active_workflows: Dict[str, asyncio.Task] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        
        # Initialize memory and monitoring
        self.memory_manager = MemoryManager(self.redis, self.qdrant)
        self.monitoring = Monitoring()
        
        # Initialize components
        self._init_qdrant_collection()
        self._register_builtin_agents()
        
        # Initialize router
        self.router = AgentRouter(self)
        
        # Initialize CrewAI if available
        self.crews: Dict[str, Any] = {}
        if CREWAI_AVAILABLE:
            self._setup_crewai_teams()
            
        logger.info("AIOrchestrator initialized with memory and monitoring")
    
    def _setup_crewai_teams(self):
        """Initialize CrewAI teams based on registered agents"""
        try:
            # Create a default crew with all agents
            agents = []
            for agent_name in self.agent_registry.list_agents():
                agent_cls = self.agent_registry.get_agent(agent_name)
                if agent_cls:
                    agent = Agent(
                        role=agent_cls.name,
                        goal=agent_cls.description,
                        backstory=f"Specialized {agent_cls.name} agent for handling specific tasks",
                        verbose=True,
                        allow_delegation=True
                    )
                    agents.append(agent)
            
            if agents:
                self.crews["default_crew"] = Crew(
                    agents=agents,
                    tasks=[],  # Will be created dynamically
                    verbose=2,
                    process=Process.sequential
                )
                logger.info(f"Created default CrewAI team with {len(agents)} agents")
                
        except Exception as e:
            logger.error(f"Error setting up CrewAI teams: {str(e)}", exc_info=True)
    
    async def execute_crew_task(
        self,
        task_description: str,
        crew_name: str = "default_crew",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using a CrewAI team
        
        Args:
            task_description: Description of the task to execute
            crew_name: Name of the crew to use (defaults to 'default_crew')
            context: Additional context for the task
            
        Returns:
            Dict containing task results
        """
        if not CREWAI_AVAILABLE:
            raise RuntimeError("CrewAI is not available. Please install it with 'pip install crewai'.")
            
        if crew_name not in self.crews:
            raise ValueError(f"Crew '{crew_name}' not found. Available crews: {list(self.crews.keys())}")
            
        try:
            # Create a task for the crew
            task = Task(
                description=task_description,
                expected_output="A detailed response addressing the task requirements",
                context=context or {},
                agent=self.crews[crew_name].agents[0]  # Start with the first agent
            )
            
            # Execute the task
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.crews[crew_name].kickoff({"task": task})
            )
            
            return {
                "status": "completed",
                "result": result,
                "crew": crew_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing CrewAI task: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "crew": crew_name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _register_builtin_agents(self):
        """Register all built-in agents with the registry"""
        from app.ai.agents import (
            FinanceAgent, SupportAgent, DevAgent, HRAgent, AnalyticsAgent
        )
        
        agents = [
            ("finance", FinanceAgent),
            ("support", SupportAgent),
            ("developer", DevAgent),
            ("hr", HRAgent),
            ("analytics", AnalyticsAgent)
        ]
        
        for name, agent_cls in agents:
            self.agent_registry.register(name)(agent_cls)
            self.agent_status[name] = AgentStatus.IDLE
    
    async def execute_workflow(
        self, 
        workflow_input: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow with the given input
        
        Args:
            workflow_input: Input data for the workflow
            workflow_id: Optional workflow ID (generated if not provided)
            
        Returns:
            Dict containing workflow execution results
        """
        workflow_id = workflow_id or str(uuid.uuid4())
        
        # Initialize workflow state
        state: GraphState = {
            "user_input": workflow_input.get("input", ""),
            "current_agent": None,
            "agent_states": {},
            "workflow_id": workflow_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "context": workflow_input.get("context", {}),
            "memory": {},
            "error": None,
            "retry_count": 0,
            "max_retries": workflow_input.get("max_retries", 3)
        }
        
        # Execute workflow in background
        task = asyncio.create_task(self._run_workflow(state))
        self.active_workflows[workflow_id] = task
        
        # Return initial response
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": f"Workflow {workflow_id} started successfully"
        }
    
    async def _run_workflow(self, state: GraphState) -> Dict[str, Any]:
        """
        Internal method to execute the workflow with state management
        """
        trace_id = state.get("trace_id", str(uuid.uuid4()))
        workflow_id = state.get("workflow_id", "unknown")
        
        # Log workflow start
        observation_id = self.monitoring.log_agent_execution(
            agent_name="workflow_orchestrator",
            input_data={"state": state},
            output_data={"status": "started"},
            trace_id=trace_id,
            metadata={"workflow_id": workflow_id}
        )
        
        try:
            state["status"] = "running"
            
            # Log workflow start to memory
            await self.memory_manager.store_memory(
                agent_id="orchestrator",
                memory_data={
                    "type": "workflow_start",
                    "content": f"Workflow {workflow_id} started",
                    "metadata": {
                        "workflow_id": workflow_id,
                        "trace_id": trace_id,
                        "input": state.get("user_input", "")
                    }
                }
            )
            
            # Execute the workflow graph
            result = await self.workflow.ainvoke(state)
            
            # Update final state
            state.update(result)
            state["status"] = "completed"
            state["updated_at"] = datetime.utcnow().isoformat()
            
            # Log workflow completion
            await self.memory_manager.store_memory(
                agent_id="orchestrator",
                memory_data={
                    "type": "workflow_complete",
                    "content": f"Workflow {workflow_id} completed successfully",
                    "metadata": {
                        "workflow_id": workflow_id,
                        "trace_id": trace_id,
                        "result": result
                    }
                }
            )
            
            # Log completion to monitoring
            self.monitoring.log_agent_execution(
                agent_name="workflow_orchestrator",
                input_data={"state": state},
                output_data={"status": "completed", "result": result},
                trace_id=trace_id,
                parent_observation_id=observation_id,
                metadata={"workflow_id": workflow_id}
            )
            
            return state
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Update state with error
            state["status"] = "failed"
            state["error"] = str(e)
            state["updated_at"] = datetime.utcnow().isoformat()
            
            # Log error to memory
            await self.memory_manager.store_memory(
                agent_id="orchestrator",
                memory_data={
                    "type": "workflow_error",
                    "content": f"Workflow {workflow_id} failed: {str(e)}",
                    "metadata": {
                        "workflow_id": workflow_id,
                        "trace_id": trace_id,
                        "error": str(e),
                        "retry_count": state.get("retry_count", 0)
                    }
                }
            )
            
            # Log error to monitoring
            self.monitoring.log_agent_execution(
                agent_name="workflow_orchestrator",
                input_data={"state": state},
                output_data={"status": "failed", "error": str(e)},
                trace_id=trace_id,
                parent_observation_id=observation_id,
                metadata={
                    "workflow_id": workflow_id,
                    "error_type": e.__class__.__name__,
                    "retry_count": state.get("retry_count", 0)
                }
            )
            
            # Handle retries if needed
            if state["retry_count"] < state["max_retries"]:
                state["retry_count"] += 1
                retry_msg = f"Retrying workflow (attempt {state['retry_count']}/{state['max_retries']})"
                logger.info(retry_msg)
                
                # Log retry to memory
                await self.memory_manager.store_memory(
                    agent_id="orchestrator",
                    memory_data={
                        "type": "workflow_retry",
                        "content": retry_msg,
                        "metadata": {
                            "workflow_id": workflow_id,
                            "trace_id": trace_id,
                            "attempt": state["retry_count"],
                            "max_attempts": state["max_retries"]
                        }
                    }
                )
                
                return await self._run_workflow(state)
                
            return state
            
        finally:
            # Clean up
            self.active_workflows.pop(state.get("workflow_id"), None)
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow
        """
        if workflow_id in self.active_workflows:
            return {
                "workflow_id": workflow_id,
                "status": "running",
                "message": "Workflow is currently executing"
            }
            
        # Check if workflow exists in completed/failed state
        # (Implementation depends on your persistence layer)
        return {
            "workflow_id": workflow_id,
            "status": "unknown",
            "message": "Workflow not found"
        }
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the LangGraph workflow
        """
        # Create a new graph
        workflow = StateGraph(GraphState)
        
        # Add nodes for each agent
        for agent_name in self.agent_registry.list_agents():
            workflow.add_node(agent_name, self._create_agent_node(agent_name))
        
        # Define edges (simplified - should be based on your workflow logic)
        workflow.add_edge("intent_classifier", "knowledge_retrieval")
        workflow.add_edge("knowledge_retrieval", "task_planner")
        workflow.add_edge("task_planner", "crew_executor")
        workflow.add_edge("crew_executor", "response_generator")
        
        # Set entry point
        workflow.set_entry_point("intent_classifier")
        
        # Set finish point
        workflow.add_edge("response_generator", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def _create_agent_node(self, agent_name: str):
        """
        Create a node function for a specific agent
        """
        async def agent_node(state: GraphState) -> Dict[str, Any]:
            try:
                # Get the agent instance
                agent_cls = self.agent_registry.get_agent(agent_name)
                if not agent_cls:
                    raise ValueError(f"Agent {agent_name} not found")
                
                agent = agent_cls()
                
                # Update state
                state["current_agent"] = agent_name
                state["updated_at"] = datetime.utcnow().isoformat()
                
                # Create agent state if not exists
                if agent_name not in state["agent_states"]:
                    state["agent_states"][agent_name] = {
                        "input": {},
                        "output": None,
                        "status": "pending",
                        "error": None,
                        "metadata": {},
                        "timestamp": datetime.utcnow().isoformat()
                    }
                
                agent_state = state["agent_states"][agent_name]
                agent_state["status"] = "processing"
                agent_state["input"] = state.get("context", {})
                
                # Execute agent
                result = await agent.process(agent_state["input"])
                
                # Update state with results
                agent_state["output"] = result
                agent_state["status"] = "completed"
                agent_state["timestamp"] = datetime.utcnow().isoformat()
                
                # Update context with agent output
                if "context" not in state:
                    state["context"] = {}
                state["context"].update(result.get("context", {}))
                
                return state
                
            except Exception as e:
                logger.error(f"Error in agent {agent_name}: {str(e)}", exc_info=True)
                if agent_name in state["agent_states"]:
                    state["agent_states"][agent_name]["status"] = "failed"
                    state["agent_states"][agent_name]["error"] = str(e)
                raise
        
        return agent_node
    
    def _init_qdrant_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            collections = self.qdrant.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if settings.QDRANT_COLLECTION not in collection_names:
                self.qdrant.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config={
                        "text": models.VectorParams(
                            size=768,  # Adjust based on your embedding model
                            distance=models.Distance.COSINE
                        )
                    }
                )
                logger.info(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {str(e)}")
            raise
    
    async def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result from Redis"""
        try:
            cached = await self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Error getting cache: {str(e)}")
            return None
    
    async def _set_cached_result(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Cache result in Redis with TTL"""
        try:
            await self.redis.setex(key, ttl_seconds, json.dumps(value))
        except Exception as e:
            logger.warning(f"Error setting cache: {str(e)}")
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters"""
        key_str = "".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return f"{prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    async def crawl_website(self, url: str, extract_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Crawl a website and optionally extract structured data"""
        cache_key = self._generate_cache_key("crawl", url=url, schema=json.dumps(extract_schema or {}))
        
        # Check cache first
        if cached := await self._get_cached_result(cache_key):
            logger.info(f"Cache hit for URL: {url}")
            return cached
        
        browser_conf = BrowserConfig(
            headless=True,
            browser="chromium",
            proxy=None,
            timeout=30000  # 30 seconds
        )
        
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=JsonCssExtractionStrategy(extract_schema) if extract_schema else None
        )
        
        try:
            async with AsyncWebCrawler(config=browser_conf) as crawler:
                result = await crawler.arun(url=url, config=run_conf)
                
                response = {
                    "url": url,
                    "markdown": result.markdown.raw_markdown if result.markdown else "",
                    "extracted_data": json.loads(result.extracted_content) if result.extracted_content else {},
                    "screenshot": result.screenshot if hasattr(result, 'screenshot') else None,
                    "status": "success"
                }
                
                # Cache the result
                await self._set_cached_result(cache_key, response)
                return response
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "status": "error"
            }
    
    async def store_embeddings(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Store text and its embeddings in Qdrant
        
        Args:
            text: The text to embed and store
            metadata: Additional metadata to store with the text
            collection_name: Optional collection name (defaults to settings.QDRANT_COLLECTION)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate embeddings using our embedding utility
            embeddings = await embedding_utils.get_embeddings([text])
            if not embeddings or not embeddings[0]:
                logger.error("Failed to generate embeddings")
                return False
                
            # Create a unique ID for the document
            doc_id = hashlib.md5(text.encode()).hexdigest()
            
            # Prepare metadata
            metadata = metadata or {}
            metadata.update({
                "text": text, 
                "timestamp": datetime.utcnow().isoformat(),
                "source": metadata.get("source", "unknown")
            })
            
            # Store in Qdrant
            collection = collection_name or settings.QDRANT_COLLECTION
            self.qdrant.upsert(
                collection_name=collection,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector={"text": embeddings[0]},
                        payload=metadata
                    )
                ]
            )
            logger.info(f"Stored embeddings for document in collection '{collection}': {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embeddings: {str(e)}")
            return False
    
    async def search_similar(
        self, 
        query: str, 
        limit: int = 5,
        collection_name: Optional[str] = None,
        score_threshold: float = 0.7,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in Qdrant using vector similarity
        
        Args:
            query: The query text to find similar content for
            limit: Maximum number of results to return
            collection_name: Optional collection name (defaults to settings.QDRANT_COLLECTION)
            score_threshold: Minimum similarity score (0-1) for results
            metadata_filters: Optional metadata filters to apply to the search
            
        Returns:
            List of similar documents with scores and metadata
        """
        try:
            # Generate query embedding
            query_embedding = await embedding_utils.get_embeddings([query])
            if not query_embedding or not query_embedding[0]:
                logger.error("Failed to generate query embedding")
                return []
                
            # Prepare filters
            filter_conditions = []
            if metadata_filters:
                for key, value in metadata_filters.items():
                    filter_conditions.append(models.FieldCondition(
                        key=f"metadata.{key}",
                        match=models.MatchValue(value=value)
                    ))
            
            # Build the query filter
            query_filter = models.Filter(
                must=filter_conditions if filter_conditions else None
            )
            
            # Search in Qdrant
            collection = collection_name or settings.QDRANT_COLLECTION
            search_result = self.qdrant.search(
                collection_name=collection,
                query_vector=("text", query_embedding[0]),
                query_filter=query_filter if filter_conditions else None,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for hit in search_result:
                payload = hit.payload or {}
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": payload,
                    "text": payload.get("text", "")[:500] + ("..." if len(payload.get("text", "")) > 500 else ""),
                    "metadata": {
                        k: v for k, v in payload.items() 
                        if k not in ["text", "vector"]
                    }
                })
            
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            return []
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user message through the AI workflow with enhanced capabilities"""
        try:
            # Check if message contains a URL and needs web crawling
            urls = self._extract_urls(message)
            crawled_data = {}
            
            if urls:
                for url in urls:
                    # Use a simple schema for news/article sites
                    schema = {
                        "title": "h1",
                        "content": ["article", ".content"],
                        "author": ["[itemprop='author']", ".author"],
                        "date": ["[itemprop='datePublished']", "time", ".date"]
                    }
                    crawled_data[url] = await self.crawl_website(url, schema)
            
            # Initialize state with crawled data
            state = {
                "messages": [{"role": "user", "content": message}],
                "context": {
                    **context,
                    "crawled_data": crawled_data,
                    "crawl_timestamp": datetime.utcnow().isoformat()
                },
                "intermediate_steps": [],
                "final_output": None
            }
            
            # Execute workflow
            for node in self.workflow:
                state = await node.process(state, self.llm_router)
            
            # Store conversation in vector DB for future reference
            if state.get("final_output"):
                await self.store_embeddings(
                    text=message,
                    metadata={
                        "response": state["final_output"],
                        "context": context,
                        "type": "conversation"
                    }
                )
            
            return {
                "response": state["final_output"], 
                "context": state["context"],
                "sources": self._extract_sources(state)
            }
            
        except Exception as e:
            logger.error(f"Error in AI processing: {str(e)}", exc_info=True)
            raise
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        return re.findall(url_pattern, text)
    
    def _extract_sources(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sources from the workflow state"""
        sources = []
        
        # Add crawled URLs as sources
        if "crawled_data" in state.get("context", {}):
            for url, data in state["context"]["crawled_data"].items():
                if data.get("status") == "success":
                    sources.append({
                        "type": "webpage",
                        "url": url,
                        "title": data.get("extracted_data", {}).get("title", url)
                    })
        
        # Add vector search results if any
        if "vector_search_results" in state.get("context", {}):
            for result in state["context"]["vector_search_results"]:
                sources.append({
                    "type": "knowledge_base",
                    "id": result.get("id"),
                    "score": result.get("score", 0),
                    "text_preview": result.get("text", "")[:200] + "..."
                })
        
        return sources

    def _create_workflow(self) -> List['BaseNode']:
        """Create and return the workflow nodes"""
        return [
            IntentClassifierNode(),
            KnowledgeRetrievalNode(),
            TaskPlannerNode(),
            CrewExecutorNode(),
            ResponseGeneratorNode()
        ]
    
    def _setup_llm_router(self):
        """Initialize LLM router for different tasks with OpenRouter models"""
        return {
            # Analysis tasks - use deepseek models for their strong reasoning
            "analysis": {
                "model": "deepseek-ai/deepseek-chat",
                "temperature": 0.3,
                "max_tokens": 4096
            },
            # Programming tasks - use deepseek-coder models
            "programming": {
                "model": "deepseek-ai/deepseek-coder-33b-instruct",
                "temperature": 0.2,
                "max_tokens": 4096
            },
            # General tasks - use Qwen for balanced performance
            "general": {
                "model": "qwen/qwen-14b-chat",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            # Default fallback - use deepseek for reliability
            "default": {
                "model": "deepseek-ai/deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 4096
            }
        }

class BaseNode:
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        raise NotImplementedError("Subclasses must implement process method")

class IntentClassifierNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Classifying intent...")
        message = state["messages"][-1]["content"].lower()
        
        if any(word in message for word in ["analyze", "analysis", "understand", "explain"]):
            state["intent"] = "analysis"
        elif any(word in message for word in ["code", "program", "script", "function"]):
            state["intent"] = "programming"
        else:
            state["intent"] = "general"
            
        logger.info(f"Classified intent: {state['intent']}")
        return state

class KnowledgeRetrievalNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Retrieving relevant knowledge...")
        # TODO: Implement RAG with Qdrant
        state["retrieved_knowledge"] = []
        return state

class TaskPlannerNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Planning tasks...")
        state["tasks"] = [{
            "id": "task_1",
            "description": "Process user query",
            "type": state.get("intent", "general"),
            "status": "pending"
        }]
        return state

class CrewExecutorNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Executing tasks with CrewAI...")
        for task in state.get("tasks", []):
            task["status"] = "completed"
        return state

class ResponseGeneratorNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Generating response...")
        state["final_output"] = {
            "response": f"Processed your request with intent: {state.get('intent', 'general')}",
            "context": state.get("context", {}),
            "metadata": {
                "model": llm_router.get(state.get("intent", "default"), {})
            }
        }
        return state
