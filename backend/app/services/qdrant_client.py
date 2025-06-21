from typing import Any, List, Dict, Optional
import logging
from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid
import numpy as np

logger = logging.getLogger(__name__)

class QdrantClient:
    def __init__(self, host: str = 'localhost', port: int = 6333, api_key: Optional[str] = None):
        self.host = host
        self.port = port
        self.api_key = api_key
        self.client = None
        self._connected = False

    async def connect(self):
        """Connect to Qdrant instance"""
        try:
            if self.api_key:
                self.client = QdrantClientLib(
                    url=f"http://{self.host}:{self.port}",
                    api_key=self.api_key
                )
            else:
                self.client = QdrantClientLib(
                    host=self.host,
                    port=self.port
                )
            
            # Test connection
            collections = self.client.get_collections()
            self._connected = True
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            self._connected = False
            return False

    async def create_collection(self, collection_name: str, vector_size: int = 1536):
        """Create a new collection if it doesn't exist"""
        if not self._connected:
            await self.connect()
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            
            if collection_name not in existing_collections:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

    async def upsert_vectors(self, collection: str, vectors: List[Dict[str, Any]]):
        """Upsert vectors into Qdrant collection"""
        if not self._connected:
            await self.connect()
        
        try:
            points = []
            for vector_data in vectors:
                point_id = vector_data.get('id', str(uuid.uuid4()))
                vector = vector_data.get('vector')
                payload = vector_data.get('payload', {})
                
                if vector is None:
                    logger.warning(f"Skipping point {point_id}: no vector provided")
                    continue
                
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                ))
            
            if points:
                self.client.upsert(
                    collection_name=collection,
                    points=points
                )
                logger.info(f"Upserted {len(points)} vectors to {collection}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert vectors to {collection}: {e}")
            return False

    async def search_vectors(self, collection: str, query_vector: List[float], top_k: int = 5, filter_conditions: Optional[Dict] = None):
        """Search for similar vectors"""
        if not self._connected:
            await self.connect()
        
        try:
            search_result = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=top_k,
                query_filter=models.Filter(**filter_conditions) if filter_conditions else None
            )
            
            results = []
            for point in search_result:
                results.append({
                    'id': point.id,
                    'score': point.score,
                    'payload': point.payload
                })
            
            return results
        except Exception as e:
            logger.error(f"Failed to search vectors in {collection}: {e}")
            return []

    async def delete_vectors(self, collection: str, point_ids: List[str]):
        """Delete vectors by IDs"""
        if not self._connected:
            await self.connect()
        
        try:
            self.client.delete(
                collection_name=collection,
                points_selector=models.PointIdsList(
                    points=point_ids
                )
            )
            logger.info(f"Deleted {len(point_ids)} vectors from {collection}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors from {collection}: {e}")
            return False

    async def get_collection_info(self, collection: str):
        """Get collection information"""
        if not self._connected:
            await self.connect()
        
        try:
            info = self.client.get_collection(collection_name=collection)
            return {
                'name': collection,
                'vectors_count': info.vectors_count,
                'indexed_vectors_count': info.indexed_vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection}: {e}")
            return None

    async def create_agent_memory_collections(self, agent_id: str):
        """Create standard memory collections for an agent"""
        collections = [
            f"{agent_id}_conversations",
            f"{agent_id}_tasks",
            f"{agent_id}_context",
            f"{agent_id}_knowledge"
        ]
        
        for collection in collections:
            await self.create_collection(collection)
        
        return collections 