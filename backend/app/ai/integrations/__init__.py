"""
Integration modules for external services and frameworks.
"""
from typing import Optional, Dict, Any

from .crewai_integration import CrewAIIntegration, CrewAIWorkflowStep
from .langgraph_integration import LangGraphIntegration, LangGraphWorkflowStep
from .langfuse_integration import LangfuseIntegration, LangfuseConfig

# Initialize integrations with default configurations
crewai_integration: Optional[CrewAIIntegration] = None
langgraph_integration: Optional[LangGraphIntegration] = None
langfuse_integration: Optional[LangfuseIntegration] = None

def initialize_integrations(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize all integrations with the given configuration.
    
    Args:
        config: Dictionary containing configuration for each integration
    """
    global crewai_integration, langgraph_integration, langfuse_integration
    
    config = config or {}
    
    # Initialize Langfuse first as other integrations might use it
    langfuse_config = config.get("langfuse", {})
    if langfuse_config.get("enabled", True):
        langfuse_integration = LangfuseIntegration(langfuse_config)
    
    # Initialize CrewAI integration
    crewai_config = config.get("crewai", {})
    if crewai_config.get("enabled", True):
        from ..agents.agent_factory import agent_factory
        crewai_integration = CrewAIIntegration(agent_factory)
    
    # Initialize LangGraph integration
    langgraph_config = config.get("langgraph", {})
    if langgraph_config.get("enabled", True):
        from ..agents.agent_factory import agent_factory
        langgraph_integration = LangGraphIntegration(agent_factory)

def get_crewai_integration() -> Optional[CrewAIIntegration]:
    """Get the CrewAI integration instance."""
    return crewai_integration

def get_langgraph_integration() -> Optional[LangGraphIntegration]:
    """Get the LangGraph integration instance."""
    return langgraph_integration

def get_langfuse_integration() -> Optional[LangfuseIntegration]:
    """Get the Langfuse integration instance."""
    return langfuse_integration

# Initialize with default config when module is imported
initialize_integrations()
