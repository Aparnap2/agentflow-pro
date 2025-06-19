from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from langchain_core.messages import BaseMessage

class AgentState(BaseModel):
    messages: List[BaseMessage]
    task_id: str
    agent_id: str
    context: Dict[str, Any]
    next_agent: Optional[str]
    escalate: bool
    final_result: Optional[Dict[str, Any]]
    reasoning_steps: List[Dict[str, Any]]

class OrchestrationState(BaseModel):
    user_request: str
    task_breakdown: List[Dict[str, Any]]
    assigned_agents: List[str]
    results: Dict[str, Any]
    coordination_messages: List[BaseMessage]
    final_output: Optional[Dict[str, Any]]
