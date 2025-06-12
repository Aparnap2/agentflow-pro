"""Embedding service for generating and managing text embeddings."""
from typing import List, Dict, Any, Optional, Union
import logging
from enum import Enum
import numpy as np
import httpx
from pydantic import BaseModel, Field, HttpUrl, validator

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingModel(str, Enum):
    """Supported embedding models."""
    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    OPENAI_TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    BAAI_BGE_SMALL_EN = "BAAI/bge-small-en-v1.5"
    BAAI_BGE_BASE_EN = "BAAI/bge-base-en-v1.5"
    BAAI_BGE_LARGE_EN = "BAAI/bge-large-en-v1.5"
    ALL_MINILM_L6_V2 = "sentence-transformers/all-MiniLM-L6-v2"
    ALL_MPNET_BASE_V2 = "sentence-transformers/all-mpnet-base-v2"

class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

class EmbeddingConfig(BaseModel):
    """Configuration for embedding generation."""
    model: EmbeddingModel = Field(
        default=EmbeddingModel.ALL_MINILM_L6_V2,
        description="The embedding model to use"
    )
    provider: EmbeddingProvider = Field(
        default=EmbeddingProvider.LOCAL,
        description="The embedding provider to use"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the embedding provider"
    )
    batch_size: int = Field(
        default=32,
        description="Number of texts to embed in a single batch"
    )
    normalize_embeddings: bool = Field(
        default=True,
        description="Whether to normalize the embeddings to unit length"
    )
    device: str = Field(
        default="cpu",
        description="Device to run the model on (cpu, cuda, mps)"
    )

class EmbeddingService:
    """Service for generating and managing text embeddings."""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """Initialize the embedding service.
        
        Args:
            config: Embedding configuration. If None, uses default settings.
        """
        self.config = config or EmbeddingConfig()
        self._model = None
        self._tokenizer = None
        self._client = None
        
        # Initialize the appropriate client based on provider
        if self.config.provider == EmbeddingProvider.OPENAI:
            self._init_openai()
        elif self.config.provider == EmbeddingProvider.HUGGINGFACE:
            self._init_huggingface()
        else:  # LOCAL
            self._init_local()
    
    def _init_openai(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.config.api_key or settings.OPENAI_API_KEY)
        except ImportError:
            logger.error("OpenAI client not installed. Install with: pip install openai")
            raise
    
    def _init_huggingface(self) -> None:
        """Initialize the Hugging Face client."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self.config.model.value,
                device=self.config.device
            )
        except ImportError:
            logger.error("SentenceTransformers not installed. Install with: pip install sentence-transformers")
            raise
    
    def _init_local(self) -> None:
        """Initialize the local embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(
                self.config.model.value,
                device=self.config.device
            )
            logger.info(f"Initialized local embedding model: {self.config.model.value}")
        except ImportError:
            logger.error("SentenceTransformers not installed. Install with: pip install sentence-transformers")
            raise
    
    async def get_embeddings(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        **kwargs
    ) -> List[List[float]]:
        """Get embeddings for the input texts.
        
        Args:
            texts: A single text or list of texts to embed
            batch_size: Override the default batch size
            **kwargs: Additional arguments to pass to the embedding model
            
        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
            
        batch_size = batch_size or self.config.batch_size
        
        if self.config.provider == EmbeddingProvider.OPENAI:
            return await self._get_openai_embeddings(texts, **kwargs)
        else:  # HuggingFace or Local
            return self._get_hf_embeddings(texts, batch_size, **kwargs)
    
    async def _get_openai_embeddings(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """Get embeddings using the OpenAI API."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")
            
        # Split into batches
        batches = [texts[i:i + self.config.batch_size] 
                  for i in range(0, len(texts), self.config.batch_size)]
        
        all_embeddings = []
        for batch in batches:
            try:
                response = await self._client.embeddings.create(
                    input=batch,
                    model=self.config.model.value,
                    **kwargs
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error getting OpenAI embeddings: {e}")
                raise
        
        return all_embeddings
    
    def _get_hf_embeddings(
        self,
        texts: List[str],
        batch_size: int,
        **kwargs
    ) -> List[List[float]]:
        """Get embeddings using a local or Hugging Face model."""
        if not self._model:
            raise RuntimeError("Model not initialized")
            
        try:
            # Encode the texts
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 10,
                convert_to_numpy=True,
                normalize_embeddings=self.config.normalize_embeddings,
                **kwargs
            )
            
            # Convert to list of lists
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        if self.config.provider == EmbeddingProvider.OPENAI:
            # Default dimensions for OpenAI models
            if "3-large" in self.config.model.value:
                return 3072
            elif "3-small" in self.config.model.value:
                return 1536
            else:  # ada-002
                return 1536
        elif self._model:
            # For local/HF models, get the dimension from the model
            return self._model.get_sentence_embedding_dimension()
        else:
            # Default to a common dimension
            return 768

# Global instance for easy import
embedding_service = EmbeddingService()
