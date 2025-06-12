"""
OpenRouter LLM integration for the AI orchestrator.

This module provides a wrapper around the OpenRouter API to support multiple LLM models.
"""

from typing import Dict, Any, Optional, List, Union, Type, TypeVar
import os
import json
import logging
import aiohttp
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterModelConfig(BaseModel):
    """Configuration for an OpenRouter model."""
    name: str = Field(..., description="Model name as it appears in OpenRouter")
    provider: str = Field(..., description="Provider of the model (e.g., openai, anthropic, google)")
    context_length: int = Field(default=8192, description="Maximum context length in tokens")
    max_tokens: int = Field(default=2048, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, description="Sampling temperature")
    top_p: float = Field(default=1.0, description="Nucleus sampling parameter")
    frequency_penalty: float = Field(default=0.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, description="Presence penalty")
    stop: Optional[List[str]] = Field(default=None, description="Stop sequences")


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If not provided, will use OPENROUTER_API_KEY from settings.
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY in your environment or pass it explicitly.")
        
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": settings.SITE_URL or "https://github.com/yourusername/agentflow-pro",
                "X-Title": settings.PROJECT_NAME or "AgentFlow Pro"
            }
        )
    
    async def close(self):
        """Close the HTTP session."""
        await self.session.close()
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models from OpenRouter.
        
        Returns:
            List of model configurations.
        """
        try:
            async with self.session.get(f"{self.BASE_URL}/models") as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("data", [])
        except Exception as e:
            logger.error(f"Failed to list OpenRouter models: {e}")
            return []
    
    async def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chat completion using OpenRouter.
        
        Args:
            model: The model ID to use (e.g., "google/gemini-pro")
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for the completion
            
        Returns:
            The API response as a dict
        """
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        try:
            async with self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"OpenRouter API request failed: {e}")
            raise
    
    async def get_model_config(self, model_name: str) -> Optional[OpenRouterModelConfig]:
        """Get configuration for a specific model.
        
        Args:
            model_name: Name of the model to get config for
            
        Returns:
            OpenRouterModelConfig if found, None otherwise
        """
        models = await self.list_models()
        for model in models:
            if model.get("id") == model_name:
                return OpenRouterModelConfig(
                    name=model["id"],
                    provider=model.get("pricing", {}).get("provider", "unknown"),
                    context_length=model.get("context_length", 8192),
                    max_tokens=model.get("max_tokens", 2048)
                )
        return None


class OpenRouterLLM:
    """Wrapper for LangChain-compatible OpenRouter LLM."""
    
    def __init__(
        self,
        model_name: str = "google/gemini-pro",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Initialize the OpenRouter LLM.
        
        Args:
            model_name: Name of the model to use (e.g., "google/gemini-pro")
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional arguments to pass to the API
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self.client = OpenRouterClient()
        self._model_config = None
    
    async def _get_model_config(self) -> OpenRouterModelConfig:
        """Get or fetch the model configuration."""
        if self._model_config is None:
            self._model_config = await self.client.get_model_config(self.model_name)
            if self._model_config is None:
                raise ValueError(f"Model {self.model_name} not found in OpenRouter")
        return self._model_config
    
    async def generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text from prompts.
        
        Args:
            prompts: List of string prompts
            stop: Optional list of stop sequences
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The API response
        """
        # Convert single prompt to list if needed
        if isinstance(prompts, str):
            prompts = [prompts]
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt} for prompt in prompts]
        
        # Get model config for defaults
        model_config = await self._get_model_config()
        
        # Prepare generation parameters
        params = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens or model_config.max_tokens,
            "top_p": self.kwargs.get("top_p", model_config.top_p),
            "frequency_penalty": self.kwargs.get("frequency_penalty", model_config.frequency_penalty),
            "presence_penalty": self.kwargs.get("presence_penalty", model_config.presence_penalty),
            "stop": stop or self.kwargs.get("stop") or model_config.stop,
            **{k: v for k, v in self.kwargs.items() if k not in ["top_p", "frequency_penalty", "presence_penalty", "stop"]}
        }
        
        # Make the API call
        response = await self.client.generate(
            model=self.model_name,
            messages=messages,
            **params
        )
        
        return response
    
    async def __call__(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """Call the model with a single prompt and return the generated text."""
        response = await self.generate([prompt], stop=stop, **kwargs)
        return response["choices"][0]["message"]["content"]
    
    async def close(self):
        """Close the client session."""
        await self.client.close()
    
    def __del__(self):
        """Ensure the client session is closed when the object is destroyed."""
        if hasattr(self, 'client') and self.client.session and not self.client.session.closed:
            import asyncio
            asyncio.create_task(self.client.close())


# Predefined model configurations for common use cases
PREDEFINED_MODELS = {
    # DeepSeek models
    "deepseek-v3": {
        "model": "deepseek-ai/deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 4096,
        "description": "DeepSeek Chat model (v3) - Good for general purpose chat and coding"
    },
    "deepseek-coder": {
        "model": "deepseek-ai/deepseek-coder-33b-instruct",
        "temperature": 0.2,
        "max_tokens": 4096,
        "description": "DeepSeek Coder - Specialized for programming and code generation"
    },
    
    # Google models
    "gemini-pro": {
        "model": "google/gemini-pro",
        "temperature": 0.7,
        "max_tokens": 2048,
        "description": "Google Gemini Pro - General purpose model"
    },
    "gemini-1.5-flash": {
        "model": "google/gemini-1.5-flash-latest",
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "Google Gemini 1.5 Flash - Fast and capable model"
    },
    
    # Qwen models
    "qwen-7b": {
        "model": "qwen/qwen-7b-chat",
        "temperature": 0.7,
        "max_tokens": 2048,
        "description": "Qwen 7B Chat - General purpose chat model"
    },
    "qwen-14b": {
        "model": "qwen/qwen-14b-chat",
        "temperature": 0.7,
        "max_tokens": 4096,
        "description": "Qwen 14B Chat - More capable chat model"
    },
    "qwen-32b": {
        "model": "qwen/qwen-32b-chat",
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "Qwen 32B Chat - High capability chat model"
    },
    
    # OpenAI models
    "gpt-3.5": {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 4096,
        "description": "GPT-3.5 Turbo - General purpose chat model"
    },
    "gpt-4": {
        "model": "openai/gpt-4-turbo-preview",
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "GPT-4 Turbo - Advanced general purpose model"
    },
    
    # Anthropic models
    "claude-3-opus": {
        "model": "anthropic/claude-3-opus-20240229",
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "Claude 3 Opus - Most capable model from Anthropic"
    },
    "claude-3-sonnet": {
        "model": "anthropic/claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "Claude 3 Sonnet - Balanced model from Anthropic"
    },
    "claude-3-haiku": {
        "model": "anthropic/claude-3-haiku-20240307",
        "temperature": 0.7,
        "max_tokens": 8192,
        "description": "Claude 3 Haiku - Fast and efficient model from Anthropic"
    }
}


def get_predefined_model_config(model_name: str) -> Dict[str, Any]:
    """Get configuration for a predefined model.
    
    Args:
        model_name: Name of the predefined model
        
    Returns:
        Dictionary with model configuration
    """
    return PREDEFINED_MODELS.get(model_name, {
        "model": model_name,
        "temperature": 0.7,
        "max_tokens": 2048,
        "description": f"Custom model: {model_name}"
    })
