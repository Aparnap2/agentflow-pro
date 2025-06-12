"""
RAG-enhanced Knowledge Base with Qdrant vector store integration.

This module provides a knowledge base implementation that uses Qdrant
for semantic search and retrieval-augmented generation.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from enum import Enum
import json
import uuid

from pydantic import BaseModel, Field, HttpUrl, validator
from qdrant_client.http import models as qdrant_models

from app.core.config import settings
from .document_processor import DocumentProcessor, Document, ChunkingStrategy
from .vector_store import VectorStore, DocumentChunk, DocumentType
from .embedding_service import EmbeddingService, EmbeddingModel, EmbeddingProvider

logger = logging.getLogger(__name__)

class KnowledgeBaseConfig(BaseModel):
    """Configuration for the RAG-enhanced knowledge base."""
    
    # Vector store settings
    qdrant_url: str = settings.QDRANT_URL
    qdrant_api_key: Optional[str] = settings.QDRANT_API_KEY
    collection_name: str = "knowledge_base"
    
    # Embedding settings
    embedding_model: EmbeddingModel = EmbeddingModel.ALL_MINILM_L6_V2
    embedding_provider: EmbeddingProvider = EmbeddingProvider.LOCAL
    
    # Document processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.SIMPLE
    
    # Search settings
    search_limit: int = 10
    min_score: float = 0.5
    
    # Cache settings
    cache_ttl: int = 3600  # seconds

class RAGKnowledgeBase:
    """
    RAG-enhanced knowledge base with Qdrant vector store.
    
    This class provides methods to store, retrieve, and search documents
    using semantic search powered by Qdrant and embeddings.
    """
    
    def __init__(self, config: Optional[KnowledgeBaseConfig] = None):
        """Initialize the RAG knowledge base."""
        self.config = config or KnowledgeBaseConfig()
        
        # Initialize components
        self.vector_store = VectorStore(
            collection_name=self.config.collection_name,
            qdrant_url=self.config.qdrant_url,
            qdrant_api_key=self.config.qdrant_api_key
        )
        
        self.embedding_service = EmbeddingService(
            model=self.config.embedding_model,
            provider=self.config.embedding_provider
        )
        
        self.document_processor = DocumentProcessor(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            chunking_strategy=self.config.chunking_strategy
        )
        
        # Initialize collection if it doesn't exist
        self._initialize_collection()
    
    def _initialize_collection(self) -> None:
        """Initialize the Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.vector_store.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.config.collection_name not in collection_names:
                # Create collection with the right vector size
                vector_size = self.embedding_service.get_embedding_dimension()
                self.vector_store.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=vector_size,
                        distance=qdrant_models.Distance.COSINE
                    )
                )
                logger.info(f"Created new Qdrant collection: {self.config.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {str(e)}")
            raise
    
    async def add_document(
        self,
        content: Union[str, bytes],
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document_type: Optional[DocumentType] = None,
        **kwargs
    ) -> str:
        """
        Add a document to the knowledge base.
        
        Args:
            content: Document content (text or binary)
            document_id: Optional document ID (generated if not provided)
            metadata: Document metadata
            document_type: Type of document (auto-detected if not provided)
            
        Returns:
            str: Document ID
        """
        doc_id = document_id or str(uuid.uuid4())
        metadata = metadata or {}
        
        try:
            # Process document into chunks
            chunks = await self.document_processor.process_document(
                content=content,
                document_type=document_type,
                metadata={"document_id": doc_id, **metadata},
                **kwargs
            )
            
            # Generate embeddings for chunks
            texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedding_service.get_embeddings(texts)
            
            # Update chunks with embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk.embedding = embedding
                chunk.chunk_index = i
                chunk.document_id = doc_id
            
            # Upsert to vector store
            await self.vector_store.upsert_documents(chunks)
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """
        Search the knowledge base using semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            min_score: Minimum relevance score (0.0 to 1.0)
            filter_conditions: Additional filter conditions
            
        Returns:
            List of matching document chunks with scores
        """
        try:
            # Generate query embedding
            query_embedding = await self.embedding_service.get_embeddings([query])
            
            if not query_embedding:
                return []
                
            # Search vector store
            results = await self.vector_store.search(
                query_embedding=query_embedding[0],
                limit=limit or self.config.search_limit,
                min_score=min_score or self.config.min_score,
                filter_conditions=filter_conditions,
                **kwargs
            )
            
            return [result.chunk for result in results]
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    async def get_document_chunks(
        self,
        document_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[DocumentChunk]:
        """
        Retrieve all chunks for a document.
        
        Args:
            document_id: Document ID
            limit: Maximum number of chunks to return
            offset: Number of chunks to skip
            
        Returns:
            List of document chunks
        """
        try:
            return await self.vector_store.get_document_chunks(
                document_id=document_id,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Failed to get document chunks: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks from the knowledge base.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            await self.vector_store.delete_document(document_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the knowledge base collection.
        
        Returns:
            Dictionary with collection information
        """
        try:
            return await self.vector_store.get_collection_info()
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            raise

# Global instance for easy import
rag_knowledge_base = RAGKnowledgeBase()
