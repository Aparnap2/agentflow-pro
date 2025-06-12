"""
LLM (Large Language Model) integrations for the AI orchestrator.

This package provides interfaces to various LLM providers including OpenRouter.
"""

from .openrouter import (
    OpenRouterClient,
    OpenRouterLLM,
    OpenRouterModelConfig,
    get_predefined_model_config,
    PREDEFINED_MODELS
)

__all__ = [
    'OpenRouterClient',
    'OpenRouterLLM',
    'OpenRouterModelConfig',
    'get_predefined_model_config',
    'PREDEFINED_MODELS'
]
