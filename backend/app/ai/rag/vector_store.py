"""Qdrant vector store implementation for RAG."""
from typing import List, Dict, Any, Optional, Union, Tuple
import uuid
import logging
from datetime import datetime
from enum import Enum

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue,
    FilterSelector, SearchParams, Payload, UpdateResult
)
from pydantic import BaseModel, Field, HttpUrl, validator

from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentType(str, Enum):
    """Supported document types for RAG."""
    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    CODE = "code"
    CSV = "csv"
    JSON = "json"

class DocumentChunk(BaseModel):
    """A chunk of a document with metadata and embedding."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    document_id: str
    chunk_index: int
    chunk_size: int
    document_type: DocumentType = DocumentType.TEXT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SearchResult(BaseModel):
    """Search result with score and chunk."""
    chunk: DocumentChunk
    score: float

class VectorStore:
    """Qdrant vector store for document embeddings and similarity search."""
    
    def __init__(self, collection_name: str = None):
        """Initialize the Qdrant client and collection."""
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
            timeout=30.0
        )
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Ensure the collection exists, create if it doesn't."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=768,  # Default size for all-MiniLM-L6-v2
                    distance=Distance.COSINE
                )
            )
    
    async def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        embeddings: List[List[float]] = None,
        batch_size: int = 100,
        **kwargs
    ) -> List[str]:
        """Upsert documents with optional embeddings into the vector store."""
        if not documents:
            logger.warning("No documents provided for upsert")
            return []
            
        if embeddings and len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        # Process documents in batches
        document_ids = []
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size] if embeddings else None
            
            points = []
            for idx, doc in enumerate(batch_docs):
                doc_id = doc.get("id", str(uuid.uuid4()))
                embedding = batch_embeddings[idx] if batch_embeddings else None
                
                # Extract metadata and ensure it's JSON-serializable
                metadata = {k: v for k, v in doc.items() 
                          if k not in ["id", "text", "embedding"]}
                
                point = PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "text": doc.get("text", ""),
                        "metadata": metadata,
                        "document_id": doc.get("document_id", doc_id),
                        "document_type": doc.get("document_type", "text"),
                        "created_at": datetime.utcnow().isoformat(),
                        **metadata
                    }
                )
                points.append(point)
                document_ids.append(doc_id)
            
            # Upsert the batch
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                    **kwargs
                )
                logger.info(f"Upserted batch of {len(points)} documents")
            except Exception as e:
                logger.error(f"Error upserting batch: {e}")
                raise
        
        return document_ids
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search for similar documents using a query embedding."""
        if not query_embedding:
            raise ValueError("Query embedding cannot be empty")
        
        # Build filter if conditions are provided
        search_filter = None
        if filter_conditions:
            must_conditions = []
            for field, value in filter_conditions.items():
                if isinstance(value, list):
                    must_conditions.append(FieldCondition(
                        key=f"metadata.{field}",
                        match=MatchValue(value=value[0])  # Using first value for IN condition
                    ))
                else:
                    must_conditions.append(FieldCondition(
                        key=f"metadata.{field}",
                        match=MatchValue(value=value)
                    ))
            
            search_filter = Filter(must=must_conditions)
        
        # Perform the search
        try:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                **kwargs
            )
            
            # Convert to SearchResult objects
            results = []
            for hit in search_results:
                payload = hit.payload or {}
                chunk = DocumentChunk(
                    id=str(hit.id),
                    text=payload.get("text", ""),
                    metadata=payload.get("metadata", {}),
                    embedding=hit.vector,
                    document_id=payload.get("document_id", str(hit.id)),
                    chunk_index=payload.get("chunk_index", 0),
                    chunk_size=payload.get("chunk_size", 0),
                    document_type=DocumentType(payload.get("document_type", "text")),
                    created_at=datetime.fromisoformat(payload.get("created_at")),
                    updated_at=datetime.fromisoformat(payload.get("updated_at", datetime.utcnow().isoformat()))
                )
                results.append(SearchResult(chunk=chunk, score=hit.score))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

# Global instance for easy import
vector_store = VectorStore()
