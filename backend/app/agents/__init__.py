from typing import Dict, Type, Any
from .base import BaseAgent, AgentConfig
from .cofounder import CoFounderAgent
from .manager import ManagerAgent
from .vertical.legal_agent import LegalAgent
from .vertical.finance_agent import FinanceAgent
from .vertical.healthcare_agent import HealthcareAgent
from .support.sales_agent import SalesAgent
from .support.support_agent import SupportAgent
from .support.growth_agent import GrowthAgent

# Registry mapping agent IDs to their respective classes
_agent_registry: Dict[str, Type[BaseAgent]] = {
    "cofounder": CoFounderAgent,
    "manager": ManagerAgent,
    "legal_agent": LegalAgent,
    "finance_agent": FinanceAgent,
    "healthcare_agent": HealthcareAgent,
    "sales": SalesAgent,
    "support": SupportAgent,
    "growth": GrowthAgent,
}

# Registry mapping agent role to agent class
AGENT_REGISTRY: Dict[AgentRole, Type[BaseAgent]] = {
    AgentRole.COFOUNDER: CoFounderAgent,
    AgentRole.MANAGER: ManagerAgent,
    AgentRole.SALES: SalesAgent,
    AgentRole.SUPPORT: SupportAgent,
    AgentRole.GROWTH: GrowthAgent,
}

def get_agent(agent_id: str, config: Dict[str, Any], memory_service, rag_service) -> BaseAgent:
    """Factory function to create agent instances"""
    agent_class = _agent_registry.get(agent_id)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_id}")
    return agent_class(config, memory_service, rag_service)

def create_agent(role: AgentRole, config: Dict[str, Any], memory_service, rag_service) -> BaseAgent:
    """Create an agent instance by role."""
    agent_class = AGENT_REGISTRY.get(role)
    if not agent_class:
        raise ValueError(f"No agent registered for role: {role}")
    return agent_class(config, memory_service, rag_service)

def get_agent_config(role: AgentRole) -> Dict[str, Any]:
    """Get default config for an agent role."""
    # Base config
    config = {
        "id": role.value,
        "role": role,
        "name": role.value.replace("_", " ").title(),
    }
    
    # Add department based on role
    if role == AgentRole.SALES:
        config["department"] = Department.SALES
    elif role == AgentRole.SUPPORT:
        config["department"] = Department.SUPPORT
    elif role == AgentRole.GROWTH:
        config["department"] = Department.MARKETING
    
    return config

def load_agent_configs() -> Dict[str, Dict[str, Any]]:
    """Load agent configurations from a config file or database"""
    # TODO: Load from config file or database
    return {}

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'get_agent',
    'create_agent',
    'get_agent_config',
    'load_agent_configs',
]
