from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import json
import logging

logger = logging.getLogger(__name__)

class AgentRole(str, Enum):
    """Agent roles in the system"""
    # Core Leadership
    COFOUNDER = "cofounder"
    MANAGER = "manager"
    
    # Business Function Agents
    CRM_AGENT = "crm_agent"
    EMAIL_MARKETING_AGENT = "email_marketing_agent"
    INVOICE_AGENT = "invoice_agent"
    SCHEDULING_AGENT = "scheduling_agent"
    SOCIAL_AGENT = "social_agent"
    HR_AGENT = "hr_agent"
    ADMIN_AGENT = "admin_agent"
    REVIEW_AGENT = "review_agent"

class Department(str, Enum):
    """Department classifications for agents"""
    LEADERSHIP = "leadership"
    OPERATIONS = "operations"
    SALES = "sales"
    MARKETING = "marketing"
    SUPPORT = "support"
    FINANCE = "finance"
    HR = "hr"
    ADMIN = "admin"

class AgentConfig(BaseModel):
    """Configuration for an agent instance"""
    id: str
    name: str
    role: AgentRole
    department: Department
    level: int = 1
    manager_id: Optional[str] = None
    direct_reports: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)
    system_prompt: str = ""
    max_concurrent_tasks: int = 5
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    memory_context: Dict[str, Any] = Field(default_factory=dict)

class AgentState(BaseModel):
    """State passed between agent nodes in the workflow"""
    messages: List[BaseMessage] = Field(default_factory=list)
    task_id: str
    agent_id: str
    context: Dict[str, Any] = Field(default_factory=dict)
    next_agent: Optional[str] = None
    escalate: bool = False
    final_result: Optional[Dict[str, Any]] = None
    reasoning_steps: List[Dict[str, Any]] = Field(default_factory=list)

class BaseAgent(ABC):
    """Base class for all agent implementations"""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        """
        Initialize the agent with services and configuration
        
        Args:
            config: Dictionary containing agent configuration
            memory_service: Service for agent memory operations
            rag_service: Service for retrieval-augmented generation
        """
        self.config = AgentConfig(**config)
        self.memory_service = memory_service
        self.rag_service = rag_service
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model for this agent"""
        from langchain_openai import ChatOpenAI
        from app.core.config import settings
        
        return ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model="anthropic/claude-3.5-sonnet",
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://agentflow.pro",
            }
        )
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the current state and return updated state
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        # Convert dict to AgentState if needed
        if not isinstance(state, AgentState):
            state = AgentState(**state)
            
        try:
            # Get relevant context and memories
            context = await self._get_context(state)
            
            # Generate response
            response = await self._generate_response(state, context)
            
            # Update state with response
            updated_state = self._update_state(state, response, context)
            
            # Log the interaction
            await self._log_interaction(state, response, context)
            
            return updated_state.dict()
            
        except Exception as e:
            logger.error(f"Error in {self.config.role} agent process: {str(e)}", exc_info=True)
            state.escalate = True
            state.context["error"] = str(e)
            return state.dict()
    
    async def _get_context(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve relevant context for the agent"""
        context = {
            "agent_config": self.config.dict(),
            "task_context": state.context,
            "memories": [],
            "documents": []
        }
        
        # Get relevant memories
        if state.messages:
            last_message = state.messages[-1].content if state.messages else ""
            memories = await self.memory_service.retrieve_memory(
                self.config.id, 
                last_message,
                limit=5
            )
            context["memories"] = memories
        
        # Get relevant documents if specified
        if state.context.get("documents"):
            doc_results = await self.rag_service.search_documents(
                state.messages[-1].content if state.messages else "",
                limit=3,
                doc_ids=state.context["documents"]
            )
            context["documents"] = doc_results
            
        return context
    
    @abstractmethod
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> BaseMessage:
        """Generate a response based on the current state and context"""
        pass
    
    def _update_state(self, state: AgentState, response: BaseMessage, context: Dict[str, Any]) -> AgentState:
        """Update the state with the agent's response"""
        # Add the response to the message history
        state.messages.append(response)
        
        # Update reasoning steps
        state.reasoning_steps.append({
            "agent": self.config.role.value,
            "reasoning": f"Processed task using {self.config.role} capabilities",
            "decision": response.content if hasattr(response, 'content') else str(response),
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    async def _log_interaction(self, state: AgentState, response: BaseMessage, context: Dict[str, Any]) -> None:
        """Log the interaction to memory"""
        try:
            await self.memory_service.store_memory(
                self.config.id,
                f"Task: {state.messages[-2].content if len(state.messages) > 1 else 'N/A'}\n"
                f"Response: {response.content if hasattr(response, 'content') else str(response)}",
                {
                    "task_id": state.task_id,
                    "agent_id": self.config.id,
                    "timestamp": datetime.now().isoformat(),
                    "context": context
                }
            )
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}", exc_info=True)

# Type variable for agent state
AgentStateT = TypeVar('AgentStateT', bound=AgentState)
