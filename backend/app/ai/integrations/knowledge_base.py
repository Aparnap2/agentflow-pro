"""
Knowledge Base Integration Module

Provides access to a knowledge base for storing and retrieving
articles, FAQs, and other support content.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl
import json
from datetime import datetime
from typing import AsyncGenerator
import re

logger = logging.getLogger(__name__)

class ArticleCategory(str, Enum):
    """Categories for knowledge base articles."""
    GENERAL = "general"
    GETTING_STARTED = "getting_started"
    TROUBLESHOOTING = "troubleshooting"
    HOW_TO = "how_to"
    FAQ = "faq"
    REFERENCE = "reference"
    ANNOUNCEMENT = "announcement"

class ArticleStatus(str, Enum):
    """Status of a knowledge base article."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    HIDDEN = "hidden"

class SearchResult(BaseModel):
    """Result of a knowledge base search."""
    article_id: str
    title: str
    content: str
    score: float
    url: Optional[HttpUrl] = None
    category: Optional[ArticleCategory] = None
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Article(BaseModel):
    """Knowledge base article model."""
    article_id: str
    title: str
    content: str
    summary: Optional[str] = None
    category: ArticleCategory = ArticleCategory.GENERAL
    status: ArticleStatus = ArticleStatus.PUBLISHED
    tags: List[str] = Field(default_factory=list)
    author: str = "system"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    views: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    related_articles: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeBaseConfig(BaseModel):
    """Configuration for knowledge base integration."""
    storage_type: str = "memory"  # 'memory', 'database', 'elasticsearch', 'zendesk', etc.
    vector_store_type: Optional[str] = None  # 'faiss', 'pinecone', 'weaviate', etc.
    embedding_model: str = "all-MiniLM-L6-v2"  # Default embedding model
    max_results: int = 10
    min_relevance_score: float = 0.5
    cache_ttl: int = 3600  # Cache TTL in seconds

class KnowledgeBaseIntegration:
    """
    Handles integration with a knowledge base system.
    
    This class provides methods to search, retrieve, and manage
    knowledge base articles for customer support and self-service.
    """
    
    def __init__(self, config: Optional[Union[Dict[str, Any], KnowledgeBaseConfig]] = None):
        """
        Initialize the knowledge base integration.
        
        Args:
            config: Configuration as a dict or KnowledgeBaseConfig
        """
        if config is None:
            config = {}
            
        if isinstance(config, dict):
            self.config = KnowledgeBaseConfig(**config)
        else:
            self.config = config
            
        self._storage = {}
        self._vector_store = None
        self._embedding_model = None
        self._cache = {}
        self._cache_timestamps = {}
        
        self._initialize_storage()
    
    def _initialize_storage(self) -> None:
        """Initialize the storage backend based on configuration."""
        try:
            if self.config.storage_type == "memory":
                # In-memory storage (for testing/demo)
                self._storage = {}
                logger.info("Using in-memory knowledge base storage")
                
            elif self.config.storage_type == "database":
                # Database storage (e.g., PostgreSQL, MongoDB)
                # Implementation would go here
                pass
                
            elif self.config.storage_type == "elasticsearch":
                # Elasticsearch storage
                # Implementation would go here
                pass
                
            # Initialize vector store if configured
            if self.config.vector_store_type:
                self._initialize_vector_store()
                
            # Initialize embedding model
            self._initialize_embedding_model()
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base storage: {str(e)}")
            raise
    
    def _initialize_vector_store(self) -> None:
        """Initialize the vector store for semantic search."""
        try:
            if self.config.vector_store_type == "faiss":
                import faiss
                import numpy as np
                
                # Create an in-memory FAISS index
                self._vector_store = faiss.IndexFlatL2(384)  # Dimension of all-MiniLM-L6-v2
                logger.info("Initialized FAISS vector store")
                
            elif self.config.vector_store_type == "pinecone":
                import pinecone
                
                # Initialize Pinecone client
                pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
                
                # Create or connect to an index
                index_name = "knowledge-base"
                if index_name not in pinecone.list_indexes():
                    pinecone.create_index(
                        name=index_name,
                        metric="cosine",
                        dimension=384  # Dimension of all-MiniLM-L6-v2
                    )
                
                self._vector_store = pinecone.Index(index_name)
                logger.info("Initialized Pinecone vector store")
                
            # Add other vector store implementations as needed
            
        except ImportError as e:
            logger.warning(f"Vector store not available: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
    
    def _initialize_embedding_model(self) -> None:
        """Initialize the embedding model."""
        try:
            # Use sentence-transformers by default
            from sentence_transformers import SentenceTransformer
            
            self._embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info(f"Initialized embedding model: {self.config.embedding_model}")
            
        except ImportError:
            logger.warning("sentence-transformers not available, using simple embeddings")
            # Fallback to simple embeddings (for testing only)
            self._embedding_model = None
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            self._embedding_model = None
    
    async def add_article(self, article: Union[Dict[str, Any], Article]) -> str:
        """
        Add or update an article in the knowledge base.
        
        Args:
            article: Article data as dict or Article instance
            
        Returns:
            str: ID of the created/updated article
        """
        try:
            # Convert dict to Article if needed
            if isinstance(article, dict):
                article = Article(**article)
            
            # Generate ID if not provided
            if not article.article_id:
                article.article_id = f"art_{len(self._storage) + 1}"
            
            # Update timestamps
            now = datetime.utcnow()
            if not article.created_at:
                article.created_at = now
            article.updated_at = now
            
            # Store the article
            self._storage[article.article_id] = article.dict()
            
            # Update vector store if available
            if self._vector_store and self._embedding_model:
                await self._update_article_embeddings(article)
            
            # Invalidate cache
            self._invalidate_cache()
            
            logger.info(f"Added/updated article: {article.article_id}")
            return article.article_id
            
        except Exception as e:
            logger.error(f"Failed to add article: {str(e)}", exc_info=True)
            raise
    
    async def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve an article by ID.
        
        Args:
            article_id: ID of the article to retrieve
            
        Returns:
            Article if found, None otherwise
        """
        try:
            article_data = self._storage.get(article_id)
            if not article_data:
                return None
                
            # Convert dict back to Article
            article = Article(**article_data)
            
            # Increment view count
            article.views += 1
            await self.add_article(article)
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to get article {article_id}: {str(e)}")
            return None
    
    async def search_articles(
        self,
        query: str,
        category: Optional[ArticleCategory] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        min_score: Optional[float] = None,
        use_semantic_search: bool = True
    ) -> List[SearchResult]:
        """
        Search for articles matching the query.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            limit: Maximum number of results
            min_score: Minimum relevance score (0.0 to 1.0)
            use_semantic_search: Whether to use semantic search
            
        Returns:
            List of matching articles with relevance scores
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, category, tags, limit)
            cached_results = self._get_from_cache(cache_key)
            if cached_results is not None:
                return cached_results
            
            if use_semantic_search and self._vector_store and self._embedding_model:
                results = await self._semantic_search(
                    query=query,
                    category=category,
                    tags=tags,
                    limit=limit,
                    min_score=min_score or self.config.min_relevance_score
                )
            else:
                results = await self._keyword_search(
                    query=query,
                    category=category,
                    tags=tags,
                    limit=limit
                )
            
            # Cache the results
            self._add_to_cache(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}", exc_info=True)
            return []
    
    async def _semantic_search(
        self,
        query: str,
        category: Optional[ArticleCategory] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[SearchResult]:
        """
        Perform semantic search using vector embeddings.
        """
        try:
            # Get query embedding
            query_embedding = self._embedding_model.encode(query)
            
            # Search in vector store
            if self.config.vector_store_type == "faiss":
                # For FAISS, we need to maintain our own ID mapping
                if not hasattr(self, '_faiss_id_map'):
                    return []
                    
                # Search for similar vectors
                D, I = self._vector_store.search(
                    query_embedding.reshape(1, -1).astype('float32'),
                    k=min(limit * 2, len(self._faiss_id_map))
                )
                
                # Get article IDs and scores
                results = []
                for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                    article_id = self._faiss_id_map.get(idx)
                    if not article_id:
                        continue
                        
                    # Get the article
                    article = await self.get_article(article_id)
                    if not article:
                        continue
                        
                    # Apply filters
                    if category and article.category != category:
                        continue
                        
                    if tags and not any(tag in article.tags for tag in tags):
                        continue
                        
                    # Calculate score (convert distance to similarity)
                    score = 1.0 / (1.0 + distance)
                    if score < min_score:
                        continue
                        
                    results.append(SearchResult(
                        article_id=article.article_id,
                        title=article.title,
                        content=article.summary or article.content[:500],
                        score=score,
                        category=article.category,
                        last_updated=article.updated_at,
                        metadata=article.metadata
                    ))
                    
                    if len(results) >= limit:
                        break
                        
                return results
                
            elif self.config.vector_store_type == "pinecone":
                # Search in Pinecone
                results = []
                query_response = self._vector_store.query(
                    vector=query_embedding.tolist(),
                    top_k=limit * 2,
                    include_metadata=True,
                    filter={
                        "category": {"$eq": category.value} if category else None,
                        "tags": {"$in": tags} if tags else None
                    }
                )
                
                for match in query_response.matches:
                    article_id = match.id
                    article = await self.get_article(article_id)
                    if not article:
                        continue
                        
                    results.append(SearchResult(
                        article_id=article.article_id,
                        title=article.title,
                        content=article.summary or article.content[:500],
                        score=match.score,
                        category=article.category,
                        last_updated=article.updated_at,
                        metadata=article.metadata
                    ))
                    
                    if len(results) >= limit:
                        break
                        
                return results
                
            else:
                # Fall back to keyword search
                return await self._keyword_search(
                    query=query,
                    category=category,
                    tags=tags,
                    limit=limit
                )
                
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}", exc_info=True)
            return []
    
    async def _keyword_search(
        self,
        query: str,
        category: Optional[ArticleCategory] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Perform keyword-based search.
        """
        try:
            # Simple keyword matching (for demo purposes)
            query_terms = set(re.findall(r'\w+', query.lower()))
            
            results = []
            
            for article_id, article_data in self._storage.items():
                article = Article(**article_data)
                
                # Apply filters
                if category and article.category != category:
                    continue
                    
                if tags and not any(tag in article.tags for tag in tags):
                    continue
                
                # Simple keyword matching
                content = f"{article.title} {article.summary or ''} {' '.join(article.tags)}".lower()
                matches = sum(1 for term in query_terms if term in content)
                
                if matches > 0:
                    # Simple scoring based on term matches (for demo)
                    score = min(1.0, matches / len(query_terms) * 1.5)
                    
                    results.append(SearchResult(
                        article_id=article.article_id,
                        title=article.title,
                        content=article.summary or article.content[:500],
                        score=score,
                        category=article.category,
                        last_updated=article.updated_at,
                        metadata=article.metadata
                    ))
            
            # Sort by score (descending)
            results.sort(key=lambda x: x.score, reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}", exc_info=True)
            return []
    
    async def _update_article_embeddings(self, article: Article) -> None:
        """
        Update vector embeddings for an article.
        """
        try:
            if not self._embedding_model:
                return
                
            # Generate embedding for the article
            text = f"{article.title}. {article.summary or article.content[:1000]}"
            embedding = self._embedding_model.encode(text)
            
            if self.config.vector_store_type == "faiss":
                # For FAISS, we need to maintain our own ID mapping
                if not hasattr(self, '_faiss_id_map'):
                    self._faiss_id_map = {}
                    self._next_faiss_id = 0
                
                # Add to FAISS index
                if not hasattr(self, '_faiss_embeddings'):
                    self._faiss_embeddings = []
                
                # Add or update the embedding
                if article.article_id in self._faiss_id_map.values():
                    # Update existing
                    idx = next((i for i, aid in self._faiss_id_map.items() if aid == article.article_id), None)
                    if idx is not None:
                        self._faiss_embeddings[idx] = embedding
                else:
                    # Add new
                    idx = self._next_faiss_id
                    self._faiss_embeddings.append(embedding)
                    self._faiss_id_map[idx] = article.article_id
                    self._next_faiss_id += 1
                
                # Update the FAISS index
                if hasattr(self, '_faiss_index_initialized') and self._faiss_index_initialized:
                    self._vector_store.add(embedding.reshape(1, -1).astype('float32'))
                else:
                    self._vector_store.add(np.array(self._faiss_embeddings, dtype='float32'))
                    self._faiss_index_initialized = True
                
            elif self.config.vector_store_type == "pinecone":
                # Upsert to Pinecone
                self._vector_store.upsert(
                    vectors=[(
                        article.article_id,
                        embedding.tolist(),
                        {
                            "title": article.title,
                            "category": article.category.value,
                            "tags": article.tags,
                            "status": article.status.value
                        }
                    )]
                )
                
        except Exception as e:
            logger.error(f"Failed to update article embeddings: {str(e)}", exc_info=True)
    
    def _generate_cache_key(
        self,
        query: str,
        category: Optional[ArticleCategory] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> str:
        """Generate a cache key for search results."""
        key_parts = [
            f"q:{query.lower().strip()}",
            f"cat:{category.value if category else 'all'}",
            f"tags:{','.join(sorted(tags)) if tags else 'none'}",
            f"lim:{limit}"
        ]
        return "|".join(key_parts)
    
    def _get_from_cache(self, key: str) -> Optional[List[SearchResult]]:
        """Get a value from cache."""
        if not self.config.cache_ttl:
            return None
            
        cached = self._cache.get(key)
        if not cached:
            return None
            
        timestamp = self._cache_timestamps.get(key, 0)
        if (datetime.utcnow().timestamp() - timestamp) > self.config.cache_ttl:
            # Cache expired
            del self._cache[key]
            if key in self._cache_timestamps:
                del self._cache_timestamps[key]
            return None
            
        return cached
    
    def _add_to_cache(self, key: str, value: List[SearchResult]) -> None:
        """Add a value to the cache."""
        if not self.config.cache_ttl:
            return
            
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.utcnow().timestamp()
    
    def _invalidate_cache(self) -> None:
        """Invalidate the entire cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    async def delete_article(self, article_id: str) -> bool:
        """
        Delete an article from the knowledge base.
        
        Args:
            article_id: ID of the article to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            if article_id not in self._storage:
                return False
                
            # Remove from storage
            del self._storage[article_id]
            
            # Remove from vector store if applicable
            if self._vector_store and hasattr(self, '_faiss_id_map'):
                # For FAISS, we'll just mark it as deleted in our ID map
                # The actual FAISS index won't be modified
                self._faiss_id_map = {
                    idx: aid for idx, aid in self._faiss_id_map.items()
                    if aid != article_id
                }
            
            # Invalidate cache
            self._invalidate_cache()
            
            logger.info(f"Deleted article: {article_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete article {article_id}: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_knowledge_base():
        # Create a knowledge base with in-memory storage
        kb = KnowledgeBaseIntegration({
            "storage_type": "memory",
            "vector_store_type": None,  # Disable vector store for this example
            "cache_ttl": 300  # 5 minutes
        })
        
        # Add some test articles
        articles = [
            {
                "title": "How to reset your password",
                "content": "To reset your password, go to the login page and click 'Forgot Password'...",
                "summary": "Instructions for resetting your account password",
                "category": ArticleCategory.HOW_TO,
                "tags": ["password", "authentication", "account"]
            },
            {
                "title": "Troubleshooting login issues",
                "content": "If you're having trouble logging in, try these steps...",
                "summary": "Common solutions for login problems",
                "category": ArticleCategory.TROUBLESHOOTING,
                "tags": ["login", "authentication", "troubleshooting"]
            },
            {
                "title": "Getting started with our platform",
                "content": "Welcome to our platform! Here's how to get started...",
                "summary": "Beginner's guide to using our platform",
                "category": ArticleCategory.GETTING_STARTED,
                "tags": ["onboarding", "getting started", "tutorial"]
            }
        ]
        
        # Add articles
        for article in articles:
            article_id = await kb.add_article(article)
            print(f"Added article: {article_id} - {article['title']}")
        
        # Search for articles
        query = "I forgot my password"
        print(f"\nSearching for: {query}")
        results = await kb.search_articles(query, limit=2)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result.title}")
            print(f"Score: {result.score:.3f}")
            print(f"Content: {result.content[:100]}...")
        
        # Get a specific article
        if results:
            article_id = results[0].article_id
            print(f"\nFetching article: {article_id}")
            article = await kb.get_article(article_id)
            if article:
                print(f"Title: {article.title}")
                print(f"Views: {article.views}")
        
        # Delete an article
        if results:
            article_id = results[0].article_id
            print(f"\nDeleting article: {article_id}")
            success = await kb.delete_article(article_id)
            print(f"Delete successful: {success}")
    
    asyncio.run(test_knowledge_base())
