from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger
from ..core.config import settings

class EmbeddingUtils:
    """Utility class for handling text embeddings with support for multiple providers"""
    
    def __init__(self, model_name: Optional[str] = None, **kwargs):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.dimensions = kwargs.get('dimensions', settings.EMBEDDING_DIM)
        self._embedding_model = None
        
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (list of floats)
        """
        if not texts:
            return []
            
        try:
            # Try to use the most appropriate embedding model based on configuration
            if self.model_name.startswith("text-embedding"):
                return await self._get_openai_embeddings(texts)
            elif "bge-" in self.model_name or "bge_" in self.model_name:
                return await self._get_huggingface_embeddings(texts)
            else:
                # Default to sentence-transformers
                return await self._get_sentence_transformers_embeddings(texts)
                
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            # Return random embeddings as fallback (not recommended for production)
            logger.warning("Using random embeddings as fallback")
            return [self._get_random_embedding() for _ in texts]
    
    async def _get_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using OpenAI's API"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            return [item.embedding for item in response.data]
            
        except ImportError:
            logger.warning("OpenAI client not installed. Falling back to random embeddings.")
            return [self._get_random_embedding() for _ in texts]
    
    async def _get_huggingface_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using HuggingFace models"""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            if self._embedding_model is None:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self._embedding_model = SentenceTransformer(
                    self.model_name,
                    device=device
                )
                
            # Convert to numpy and then to list for JSON serialization
            embeddings = self._embedding_model.encode(texts, convert_to_tensor=False)
            return [embedding.tolist() for embedding in embeddings]
            
        except ImportError:
            logger.warning("sentence-transformers not installed. Falling back to random embeddings.")
            return [self._get_random_embedding() for _ in texts]
    
    async def _get_sentence_transformers_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using sentence-transformers"""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            if self._embedding_model is None:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self._embedding_model = SentenceTransformer(
                    'all-MiniLM-L6-v2',  # Default model
                    device=device
                )
                
            # Convert to numpy and then to list for JSON serialization
            embeddings = self._embedding_model.encode(texts, convert_to_tensor=False)
            return [embedding.tolist() for embedding in embeddings]
            
        except ImportError:
            logger.warning("sentence-transformers not installed. Falling back to random embeddings.")
            return [self._get_random_embedding() for _ in texts]
    
    def _get_random_embedding(self) -> List[float]:
        """Generate a random embedding (for testing/fallback only)"""
        return np.random.rand(self.dimensions).tolist()
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

# Global instance for easy import
embedding_utils = EmbeddingUtils()
