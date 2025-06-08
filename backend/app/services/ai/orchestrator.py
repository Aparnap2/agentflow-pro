import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from loguru import logger
from ..core.config import settings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from qdrant_client import QdrantClient
from qdrant_client.http import models
from upstash_redis import Redis
import hashlib
from datetime import datetime, timedelta

# Import embedding utilities
from app.ai.embeddings import EmbeddingUtils, embedding_utils

# Initialize embedding utilities
embedding_utils = EmbeddingUtils()

class AIOrchestrator:
    def __init__(self):
        self.workflow = self._create_workflow()
        self.llm_router = self._setup_llm_router()
        self.redis = Redis.from_params(
            url=settings.REDIS_URL,
            token=settings.REDIS_TOKEN
        )
        self.qdrant = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self._init_qdrant_collection()
    
    def _init_qdrant_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            collections = self.qdrant.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if settings.QDRANT_COLLECTION not in collection_names:
                self.qdrant.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config={
                        "text": models.VectorParams(
                            size=768,  # Adjust based on your embedding model
                            distance=models.Distance.COSINE
                        )
                    }
                )
                logger.info(f"Created Qdrant collection: {settings.QDRANT_COLLECTION}")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {str(e)}")
            raise
    
    async def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result from Redis"""
        try:
            cached = await self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Error getting cache: {str(e)}")
            return None
    
    async def _set_cached_result(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Cache result in Redis with TTL"""
        try:
            await self.redis.setex(key, ttl_seconds, json.dumps(value))
        except Exception as e:
            logger.warning(f"Error setting cache: {str(e)}")
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters"""
        key_str = "".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return f"{prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    async def crawl_website(self, url: str, extract_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Crawl a website and optionally extract structured data"""
        cache_key = self._generate_cache_key("crawl", url=url, schema=json.dumps(extract_schema or {}))
        
        # Check cache first
        if cached := await self._get_cached_result(cache_key):
            logger.info(f"Cache hit for URL: {url}")
            return cached
        
        browser_conf = BrowserConfig(
            headless=True,
            browser="chromium",
            proxy=None,
            timeout=30000  # 30 seconds
        )
        
        run_conf = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=JsonCssExtractionStrategy(extract_schema) if extract_schema else None
        )
        
        try:
            async with AsyncWebCrawler(config=browser_conf) as crawler:
                result = await crawler.arun(url=url, config=run_conf)
                
                response = {
                    "url": url,
                    "markdown": result.markdown.raw_markdown if result.markdown else "",
                    "extracted_data": json.loads(result.extracted_content) if result.extracted_content else {},
                    "screenshot": result.screenshot if hasattr(result, 'screenshot') else None,
                    "status": "success"
                }
                
                # Cache the result
                await self._set_cached_result(cache_key, response)
                return response
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "status": "error"
            }
    
    async def store_embeddings(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Store text and its embeddings in Qdrant
        
        Args:
            text: The text to embed and store
            metadata: Additional metadata to store with the text
            collection_name: Optional collection name (defaults to settings.QDRANT_COLLECTION)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate embeddings using our embedding utility
            embeddings = await embedding_utils.get_embeddings([text])
            if not embeddings or not embeddings[0]:
                logger.error("Failed to generate embeddings")
                return False
                
            # Create a unique ID for the document
            doc_id = hashlib.md5(text.encode()).hexdigest()
            
            # Prepare metadata
            metadata = metadata or {}
            metadata.update({
                "text": text, 
                "timestamp": datetime.utcnow().isoformat(),
                "source": metadata.get("source", "unknown")
            })
            
            # Store in Qdrant
            collection = collection_name or settings.QDRANT_COLLECTION
            self.qdrant.upsert(
                collection_name=collection,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector={"text": embeddings[0]},
                        payload=metadata
                    )
                ]
            )
            logger.info(f"Stored embeddings for document in collection '{collection}': {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embeddings: {str(e)}")
            return False
    
    async def search_similar(
        self, 
        query: str, 
        limit: int = 5,
        collection_name: Optional[str] = None,
        score_threshold: float = 0.7,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in Qdrant using vector similarity
        
        Args:
            query: The query text to find similar content for
            limit: Maximum number of results to return
            collection_name: Optional collection name (defaults to settings.QDRANT_COLLECTION)
            score_threshold: Minimum similarity score (0-1) for results
            metadata_filters: Optional metadata filters to apply to the search
            
        Returns:
            List of similar documents with scores and metadata
        """
        try:
            # Generate query embedding
            query_embedding = await embedding_utils.get_embeddings([query])
            if not query_embedding or not query_embedding[0]:
                logger.error("Failed to generate query embedding")
                return []
                
            # Prepare filters
            filter_conditions = []
            if metadata_filters:
                for key, value in metadata_filters.items():
                    filter_conditions.append(models.FieldCondition(
                        key=f"metadata.{key}",
                        match=models.MatchValue(value=value)
                    ))
            
            # Build the query filter
            query_filter = models.Filter(
                must=filter_conditions if filter_conditions else None
            )
            
            # Search in Qdrant
            collection = collection_name or settings.QDRANT_COLLECTION
            search_result = self.qdrant.search(
                collection_name=collection,
                query_vector=("text", query_embedding[0]),
                query_filter=query_filter if filter_conditions else None,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for hit in search_result:
                payload = hit.payload or {}
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": payload,
                    "text": payload.get("text", "")[:500] + ("..." if len(payload.get("text", "")) > 500 else ""),
                    "metadata": {
                        k: v for k, v in payload.items() 
                        if k not in ["text", "vector"]
                    }
                })
            
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            return []
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user message through the AI workflow with enhanced capabilities"""
        try:
            # Check if message contains a URL and needs web crawling
            urls = self._extract_urls(message)
            crawled_data = {}
            
            if urls:
                for url in urls:
                    # Use a simple schema for news/article sites
                    schema = {
                        "title": "h1",
                        "content": ["article", ".content"],
                        "author": ["[itemprop='author']", ".author"],
                        "date": ["[itemprop='datePublished']", "time", ".date"]
                    }
                    crawled_data[url] = await self.crawl_website(url, schema)
            
            # Initialize state with crawled data
            state = {
                "messages": [{"role": "user", "content": message}],
                "context": {
                    **context,
                    "crawled_data": crawled_data,
                    "crawl_timestamp": datetime.utcnow().isoformat()
                },
                "intermediate_steps": [],
                "final_output": None
            }
            
            # Execute workflow
            for node in self.workflow:
                state = await node.process(state, self.llm_router)
            
            # Store conversation in vector DB for future reference
            if state.get("final_output"):
                await self.store_embeddings(
                    text=message,
                    metadata={
                        "response": state["final_output"],
                        "context": context,
                        "type": "conversation"
                    }
                )
            
            return {
                "response": state["final_output"], 
                "context": state["context"],
                "sources": self._extract_sources(state)
            }
            
        except Exception as e:
            logger.error(f"Error in AI processing: {str(e)}", exc_info=True)
            raise
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        return re.findall(url_pattern, text)
    
    def _extract_sources(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sources from the workflow state"""
        sources = []
        
        # Add crawled URLs as sources
        if "crawled_data" in state.get("context", {}):
            for url, data in state["context"]["crawled_data"].items():
                if data.get("status") == "success":
                    sources.append({
                        "type": "webpage",
                        "url": url,
                        "title": data.get("extracted_data", {}).get("title", url)
                    })
        
        # Add vector search results if any
        if "vector_search_results" in state.get("context", {}):
            for result in state["context"]["vector_search_results"]:
                sources.append({
                    "type": "knowledge_base",
                    "id": result.get("id"),
                    "score": result.get("score", 0),
                    "text_preview": result.get("text", "")[:200] + "..."
                })
        
        return sources

    def _create_workflow(self) -> List['BaseNode']:
        """Create and return the workflow nodes"""
        return [
            IntentClassifierNode(),
            KnowledgeRetrievalNode(),
            TaskPlannerNode(),
            CrewExecutorNode(),
            ResponseGeneratorNode()
        ]
    
    def _setup_llm_router(self):
        """Initialize LLM router for different tasks"""
        return {
            "analysis": {"model": "deepseek-v3", "provider": "openrouter"},
            "programming": {"model": "qwen-7b", "provider": "openrouter"},
            "general": {"model": "gemini-pro", "provider": "google"},
            "default": {"model": "gpt-4", "provider": "openai"}
        }

class BaseNode:
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        raise NotImplementedError("Subclasses must implement process method")

class IntentClassifierNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Classifying intent...")
        message = state["messages"][-1]["content"].lower()
        
        if any(word in message for word in ["analyze", "analysis", "understand", "explain"]):
            state["intent"] = "analysis"
        elif any(word in message for word in ["code", "program", "script", "function"]):
            state["intent"] = "programming"
        else:
            state["intent"] = "general"
            
        logger.info(f"Classified intent: {state['intent']}")
        return state

class KnowledgeRetrievalNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Retrieving relevant knowledge...")
        # TODO: Implement RAG with Qdrant
        state["retrieved_knowledge"] = []
        return state

class TaskPlannerNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Planning tasks...")
        state["tasks"] = [{
            "id": "task_1",
            "description": "Process user query",
            "type": state.get("intent", "general"),
            "status": "pending"
        }]
        return state

class CrewExecutorNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Executing tasks with CrewAI...")
        for task in state.get("tasks", []):
            task["status"] = "completed"
        return state

class ResponseGeneratorNode(BaseNode):
    async def process(self, state: Dict, llm_router: Dict) -> Dict:
        logger.info("Generating response...")
        state["final_output"] = {
            "response": f"Processed your request with intent: {state.get('intent', 'general')}",
            "context": state.get("context", {}),
            "metadata": {
                "model": llm_router.get(state.get("intent", "default"), {})
            }
        }
        return state
