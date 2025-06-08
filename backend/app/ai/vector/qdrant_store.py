import os
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from ..core.config import settings

class QdrantConfig(BaseModel):
    """Configuration for Qdrant connection"""
    url: str = Field(..., description="Qdrant server URL")
    api_key: Optional[str] = Field(None, description="Qdrant API key")
    collection_name: str = Field(..., description="Collection name for vectors")
    embedding_dim: int = Field(768, description="Dimension of the embedding vectors")
    distance_metric: str = Field("COSINE", description="Distance metric (COSINE, EUCLID, DOT)")

class QdrantVectorStore:
    """Wrapper around Qdrant Vector Store with Gemini embeddings"""
    
    def __init__(self, config: Optional[QdrantConfig] = None):
        """Initialize the Qdrant vector store with Gemini embeddings"""
        self.config = config or self._load_config()
        self.embeddings = self._init_embeddings()
        self.client = self._init_client()
        self._ensure_collection()
    
    def _load_config(self) -> QdrantConfig:
        """Load configuration from environment variables"""
        return QdrantConfig(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name=os.getenv("QDRANT_COLLECTION", "documents"),
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "768")),
            distance_metric=os.getenv("QDRANT_DISTANCE_METRIC", "COSINE"),
        )
    
    def _init_embeddings(self) -> Embeddings:
        """Initialize Gemini embeddings"""
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            task_type="retrieval_document",
        )
    
    def _init_client(self) -> QdrantClient:
        """Initialize Qdrant client"""
        return QdrantClient(
            url=self.config.url,
            api_key=self.config.api_key,
        )
    
    def _get_distance_metric(self) -> Distance:
        """Get the distance metric enum value"""
        metric_map = {
            "COSINE": Distance.COSINE,
            "EUCLID": Distance.EUCLID,
            "DOT": Distance.DOT,
        }
        return metric_map.get(self.config.distance_metric.upper(), Distance.COSINE)
    
    def _ensure_collection(self):
        """Ensure the collection exists"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.embedding_dim,
                        distance=self._get_distance_metric(),
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.config.collection_name}")
            else:
                logger.debug(f"Using existing Qdrant collection: {self.config.collection_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        documents: List[Document], 
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[str]:
        """Add documents to the vector store"""
        if not documents:
            return []
        
        # Generate embeddings
        texts = [doc.page_content for doc in documents]
        embeddings = await self.embeddings.aembed_documents(texts)
        
        # Prepare points for Qdrant
        points = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = str(uuid4())
            payload = {
                "text": doc.page_content,
                "metadata": {**doc.metadata, **(metadata or {})},
            }
            
            points.append(
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload=payload,
                )
            )
        
        # Add to Qdrant
        self.client.upsert(
            collection_name=self.config.collection_name,
            points=points,
            **kwargs
        )
        
        return [str(point.id) for point in points]
    
    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Document]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Convert filter to Qdrant filter
        qdrant_filter = self._build_qdrant_filter(filter) if filter else None
        
        # Search in Qdrant
        search_result = self.client.search(
            collection_name=self.config.collection_name,
            query_vector=query_embedding,
            query_filter=qdrant_filter,
            limit=k,
            **kwargs
        )
        
        # Convert to LangChain documents
        documents = []
        for hit in search_result:
            payload = hit.payload or {}
            doc = Document(
                page_content=payload.get("text", ""),
                metadata=payload.get("metadata", {}) | {"id": hit.id, "score": hit.score},
            )
            documents.append(doc)
        
        return documents
    
    def _build_qdrant_filter(self, filter_dict: Dict[str, Any]) -> Optional[Filter]:
        """Convert a filter dictionary to Qdrant filter"""
        if not filter_dict:
            return None
            
        must_conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, (str, int, float, bool)):
                must_conditions.append(
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchValue(value=value),
                    )
                )
        
        return Filter(must=must_conditions) if must_conditions else None

# Global instance for easy import
qdrant_vector_store = QdrantVectorStore()

# Example usage:
# from app.ai.vector.qdrant_store import qdrant_vector_store
# docs = [Document(page_content="example text", metadata={"source": "test"})]
# await qdrant_vector_store.add_documents(docs)
# results = await qdrant_vector_store.similarity_search("query text")
