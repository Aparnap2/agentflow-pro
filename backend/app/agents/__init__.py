from typing import Dict, Type, Any
from .base import BaseAgent, AgentConfig, AgentRole
from .core.cofounder import CoFounderAgent
from .core.manager import ManagerAgent
from .verticals.crm_agent import CRMAgent
from .verticals.email_marketing_agent import EmailMarketingAgent
from .verticals.invoice_agent import InvoiceAgent
from .verticals.scheduling_agent import SchedulingAgent
from .verticals.social_agent import SocialAgent
from .verticals.hr_agent import HRAgent
from .verticals.admin_agent import AdminAgent
from .verticals.review_agent import ReviewAgent

# Registry mapping agent IDs to their respective classes
_agent_registry: Dict[str, Type[BaseAgent]] = {
    "cofounder": CoFounderAgent,
    "manager": ManagerAgent,
    "crm_agent": CRMAgent,
    "email_marketing_agent": EmailMarketingAgent,
    "invoice_agent": InvoiceAgent,
    "scheduling_agent": SchedulingAgent,
    "social_agent": SocialAgent,
    "hr_agent": HRAgent,
    "admin_agent": AdminAgent,
    "review_agent": ReviewAgent,
}

# Registry mapping agent role to agent class
AGENT_REGISTRY: Dict[AgentRole, Type[BaseAgent]] = {
    AgentRole.COFOUNDER: CoFounderAgent,
    AgentRole.MANAGER: ManagerAgent,
    AgentRole.CRM_AGENT: CRMAgent,
    AgentRole.EMAIL_MARKETING_AGENT: EmailMarketingAgent,
    AgentRole.INVOICE_AGENT: InvoiceAgent,
    AgentRole.SCHEDULING_AGENT: SchedulingAgent,
    AgentRole.SOCIAL_AGENT: SocialAgent,
    AgentRole.HR_AGENT: HRAgent,
    AgentRole.ADMIN_AGENT: AdminAgent,
    AgentRole.REVIEW_AGENT: ReviewAgent,
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
    from .base import Department
    
    # Base config
    config = {
        "id": role.value,
        "role": role,
        "name": role.value.replace("_", " ").title(),
    }
    
    # Add department based on role
    department_mapping = {
        AgentRole.COFOUNDER: Department.LEADERSHIP,
        AgentRole.MANAGER: Department.OPERATIONS,
        AgentRole.CRM_AGENT: Department.SALES,
        AgentRole.EMAIL_MARKETING_AGENT: Department.MARKETING,
        AgentRole.INVOICE_AGENT: Department.FINANCE,
        AgentRole.SCHEDULING_AGENT: Department.OPERATIONS,
        AgentRole.SOCIAL_AGENT: Department.MARKETING,
        AgentRole.HR_AGENT: Department.HR,
        AgentRole.ADMIN_AGENT: Department.ADMIN,
        AgentRole.REVIEW_AGENT: Department.SUPPORT,
    }
    
    config["department"] = department_mapping.get(role, Department.OPERATIONS)
    return config

def load_agent_configs() -> Dict[str, Dict[str, Any]]:
    """Load agent configurations from a config file or database"""
    # Return default configurations for all agents
    configs = {}
    
    for agent_id in _agent_registry.keys():
        # Get the role from agent_id
        role_mapping = {v: k for k, v in {role.value: role for role in AgentRole}.items()}
        role = role_mapping.get(agent_id)
        
        if role:
            configs[agent_id] = get_agent_config(role)
    
    return configs

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'get_agent',
    'create_agent',
    'get_agent_config',
    'load_agent_configs',
]
