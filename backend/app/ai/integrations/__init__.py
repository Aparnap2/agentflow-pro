"""
Integration modules for external services and frameworks.
"""
from typing import Optional, Dict, Any, Type, Union

from .crewai_integration import CrewAIIntegration, CrewAIWorkflowStep
from .langgraph_integration import LangGraphIntegration, LangGraphWorkflowStep
from .langfuse_integration import LangfuseIntegration, LangfuseConfig
from .payment_processor_integration import PaymentProcessorIntegration, PaymentIntent, Refund, Customer, PaymentMethod
from .basic_payment_processor import BasicPaymentProcessor
# Stripe integration removed for MVP
# from .stripe_integration import StripeIntegration

# Initialize integrations with default configurations
crewai_integration: Optional[CrewAIIntegration] = None
langgraph_integration: Optional[LangGraphIntegration] = None
langfuse_integration: Optional[LangfuseIntegration] = None
payment_processor: Optional[PaymentProcessorIntegration] = None

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
    
    # Initialize Langfuse if configured
    if langfuse_config := config.get('langfuse'):
        initialize_langfuse(langfuse_config)
    
    # Initialize Payment Processor if configured
    if payment_processor_config := config.get('payment_processor'):
        initialize_payment_processor(payment_processor_config)
    
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


def initialize_payment_processor(config: Dict[str, Any] = None) -> None:
    """
    Initialize the payment processor integration.
    For MVP, we use a basic in-memory payment processor that doesn't require external services.
    
    Args:
        config: Configuration dictionary (ignored for MVP)
    """
    global payment_processor
    
    # For MVP, we'll always use the basic payment processor
    # that doesn't require any API keys or external services
    payment_processor = BasicPaymentProcessor()


def get_payment_processor() -> Optional[PaymentProcessorIntegration]:
    """
    Get the payment processor integration instance.
    
    Returns:
        The payment processor integration instance, or None if not initialized
    """
    return payment_processor

def _initialize_defaults():
    """Initialize integrations with default configuration."""
    try:
        initialize_integrations()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to initialize integrations: {e}")

# Initialize with default config when module is imported
_initialize_defaults()
