from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class GenerationConfig(BaseModel):
    """Configuration for text generation."""
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    top_k: int = 40
    stop_sequences: Optional[List[str]] = None

class LLMResponse(BaseModel):
    """Response from an LLM generation call."""
    text: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseLLM(ABC):
    """Base class for all LLM providers."""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}
        self.client = self.initialize_client()
    
    @abstractmethod
    def initialize_client(self) -> Any:
        """Initialize the LLM client."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate text from the given prompt."""
        pass
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate a chat completion."""
        # Default implementation can be overridden by subclasses
        prompt = self._format_chat_messages(messages)
        return await self.generate(prompt, config)
    
    def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a single prompt string."""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role.upper()}: {content}")
        return "\n".join(formatted)
    
    def _get_generation_config(self, config: Optional[GenerationConfig] = None) -> Dict[str, Any]:
        """Get the generation config with defaults."""
        default_config = GenerationConfig()
        if config is None:
            return default_config.dict()
        
        # Merge with defaults
        return {**default_config.dict(), **config.dict(exclude_unset=True)}
