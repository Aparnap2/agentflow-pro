# AgentFlow Pro Backend - Complete MVP with LangGraph Orchestration
# File: main.py

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from datetime import datetime, timedelta
from uuid import uuid4, UUID
import asyncio
import json
import logging
from enum import Enum
from dataclasses import dataclass, asdict
import asyncpg
from contextlib import asynccontextmanager
import os
from pathlib import Path

# LangChain/LangGraph imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from typing_extensions import TypedDict

# Specialized imports
import redis.asyncio as redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from neo4j import AsyncGraphDatabase
import httpx
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
import graphiti

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")
    
    # Database connections
    POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost/agentflow")
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
    
    # Stripe Configuration
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_...")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24
    
    # Rate Limiting per plan (per day)
    STARTER_PLAN_API_CALLS = 1000
    STARTER_PLAN_LLM_TOKENS = 100000
    PRO_PLAN_API_CALLS = 10000
    PRO_PLAN_LLM_TOKENS = 1000000
    ENTERPRISE_PLAN_API_CALLS = 100000
    ENTERPRISE_PLAN_LLM_TOKENS = 10000000
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)

settings = Settings()

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

# =============================================================================
# TENANT & AUTH MODELS
# =============================================================================

class PlanType(str, Enum):
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class PricingModel(str, Enum):
    FREEMIUM = "freemium"
    USAGE_BASED = "usage_based"
    OUTCOME_BASED = "outcome_based"
    SUBSCRIPTION = "subscription"

class OutcomeMetric(str, Enum):
    CONTRACTS_PROCESSED = "contracts_processed"
    LEADS_GENERATED = "leads_generated"
    CLAIMS_RESOLVED = "claims_resolved"
    DOCUMENTS_ANALYZED = "documents_analyzed"
    PATIENTS_PROCESSED = "patients_processed"
    ORDERS_FULFILLED = "orders_fulfilled"

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class AgentRole(str, Enum):
    COFOUNDER = "cofounder"
    MANAGER = "manager"
    # Vertical Industry Agents (as per playbook)
    LEGAL_AGENT = "legal_agent"
    FINANCE_AGENT = "finance_agent"
    HEALTHCARE_AGENT = "healthcare_agent"
    MANUFACTURING_AGENT = "manufacturing_agent"
    ECOMMERCE_AGENT = "ecommerce_agent"
    COACHING_AGENT = "coaching_agent"
    # Generic Support Agents
    SALES = "sales"
    SUPPORT = "support"
    GROWTH = "growth"

class TenantInfo(BaseModel):
    tenant_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    plan: PlanType
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    api_calls_quota: int
    llm_tokens_quota: int
    is_active: bool = True

class UserInfo(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    email: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class TokenData(BaseModel):
    user_id: str
    tenant_id: str
    email: str
    role: UserRole

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    tenant_name: str
    plan: PlanType = PlanType.STARTER

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
    tenant: TenantInfo

class RateLimitInfo(BaseModel):
    tenant_id: str
    window_start: datetime
    api_calls: int
    llm_tokens: int
    api_calls_limit: int
    llm_tokens_limit: int

class BillingInfo(BaseModel):
    invoice_id: str
    tenant_id: str
    stripe_invoice_id: Optional[str]
    status: str
    amount_due: int  # in cents
    paid_at: Optional[datetime] = None

class OutcomeBasedUsage(BaseModel):
    tenant_id: str
    agent_id: str
    outcome_metric: OutcomeMetric
    count: int
    rate_per_outcome: float  # price per outcome in cents
    total_amount: int  # total amount in cents
    recorded_at: datetime = Field(default_factory=datetime.now)

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Department(str, Enum):
    LEADERSHIP = "leadership"
    OPERATIONS = "operations"
    SALES = "sales"
    MARKETING = "marketing"
    SUPPORT = "support"
    FINANCE = "finance"
    HR = "hr"

class MessageType(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL = "tool"

class AgentConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: AgentRole
    department: Department
    level: int  # 1=CoFounder, 2=CEO, 3=Managers, 4=Specialists
    manager_id: Optional[str] = None
    direct_reports: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)
    system_prompt: str = ""
    max_concurrent_tasks: int = 5
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    memory_context: Dict[str, Any] = Field(default_factory=dict)

class TaskRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[str] = None
    department: Optional[Department] = None
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)  # Document IDs for RAG

    @validator('deadline')
    def validate_deadline(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Deadline must be in the future')
        return v

class TaskResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str]
    assigned_agent: Optional[AgentConfig] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_chain: List[Dict[str, Any]] = Field(default_factory=list)
    error_message: Optional[str] = None
    escalation_reason: Optional[str] = None

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    agent_id: Optional[str] = None
    message: str
    message_type: MessageType = MessageType.HUMAN
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    
class DocumentUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    content_type: str
    size: int
    processed: bool = False
    chunks_count: int = 0
    uploaded_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# =============================================================================
# LANGGRAPH STATE DEFINITIONS
# =============================================================================

class AgentState(TypedDict):
    messages: List[BaseMessage]
    task_id: str
    agent_id: str
    context: Dict[str, Any]
    next_agent: Optional[str]
    escalate: bool
    final_result: Optional[Dict[str, Any]]
    reasoning_steps: List[Dict[str, Any]]

class OrchestrationState(TypedDict):
    user_request: str
    task_breakdown: List[Dict[str, Any]]
    assigned_agents: List[str]
    results: Dict[str, Any]
    coordination_messages: List[BaseMessage]
    final_output: Optional[Dict[str, Any]]

# =============================================================================
# MEMORY SERVICE WITH GRAPHITI
# =============================================================================

class GraphitiMemoryService:
    def __init__(self, neo4j_driver):
        self.neo4j_driver = neo4j_driver
        self.graphiti_client = None
        
    async def initialize(self):
        """Initialize Graphiti client"""
        self.graphiti_client = graphiti.Graphiti(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
        await self.graphiti_client.build_indices_and_constraints()

    async def store_memory(self, agent_id: str, content: str, metadata: Dict[str, Any] = None):
        """Store memory using Graphiti"""
        if not self.graphiti_client:
            await self.initialize()
            
        try:
            # Create episodic memory
            await self.graphiti_client.add_episodic_memory(
                content=content,
                source_description=f"Agent {agent_id} memory",
                metadata={
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Extract and store entities/relationships
            entities = await self.graphiti_client.extract_entities(content)
            for entity in entities:
                await self.graphiti_client.add_entity(
                    name=entity.name,
                    labels=entity.labels,
                    metadata={"source": agent_id}
                )
                
        except Exception as e:
            logger.error(f"Error storing memory for agent {agent_id}: {e}")

    async def retrieve_memory(self, agent_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant memories"""
        if not self.graphiti_client:
            await self.initialize()
            
        try:
            # Search episodic memories
            memories = await self.graphiti_client.search_episodic_memories(
                query=query,
                limit=limit,
                metadata_filter={"agent_id": agent_id}
            )
            
            return [
                {
                    "content": memory.content,
                    "timestamp": memory.metadata.get("timestamp"),
                    "relevance_score": memory.score
                }
                for memory in memories
            ]
        except Exception as e:
            logger.error(f"Error retrieving memory for agent {agent_id}: {e}")
            return []

    async def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive agent context"""
        if not self.graphiti_client:
            await self.initialize()
            
        try:
            # Get recent interactions
            recent_memories = await self.graphiti_client.search_episodic_memories(
                query="",
                limit=20,
                metadata_filter={"agent_id": agent_id}
            )
            
            # Get connected entities
            entities = await self.graphiti_client.get_entities(
                metadata_filter={"source": agent_id}
            )
            
            return {
                "recent_memories": [m.content for m in recent_memories[:5]],
                "key_entities": [e.name for e in entities[:10]],
                "memory_count": len(recent_memories),
                "entity_count": len(entities)
            }
        except Exception as e:
            logger.error(f"Error getting context for agent {agent_id}: {e}")
            return {}

# =============================================================================
# QDRANT RAG SERVICE
# =============================================================================

class QdrantRAGService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.collection_name = "agentflow_docs"
        self.doc_converter = DocumentConverter()
        
    async def initialize(self):
        """Initialize Qdrant collection"""
        try:
            collections = self.client.get_collections()
            if self.collection_name not in [c.name for c in collections.collections]:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
        except Exception as e:
            logger.error(f"Error initializing Qdrant: {e}")

    async def process_document(self, file_path: str, doc_id: str) -> DocumentUpload:
        """Process document using Docling and store in Qdrant"""
        try:
            # Convert document using Docling
            result = self.doc_converter.convert(file_path)
            
            # Extract text content
            full_text = result.document.export_to_markdown()
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            chunks = text_splitter.split_text(full_text)
            
            # Generate embeddings and store
            points = []
            for i, chunk in enumerate(chunks):
                embedding = await self._get_embedding(chunk)
                points.append(
                    PointStruct(
                        id=f"{doc_id}_{i}",
                        vector=embedding,
                        payload={
                            "document_id": doc_id,
                            "chunk_index": i,
                            "content": chunk,
                            "metadata": {
                                "filename": Path(file_path).name,
                                "processed_at": datetime.now().isoformat()
                            }
                        }
                    )
                )
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            return DocumentUpload(
                id=doc_id,
                filename=Path(file_path).name,
                content_type="application/pdf",  # Adjust based on file type
                size=Path(file_path).stat().st_size,
                processed=True,
                chunks_count=len(chunks)
            )
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    async def search_documents(self, query: str, limit: int = 5, doc_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Search documents using RAG"""
        try:
            query_embedding = await self._get_embedding(query)
            
            # Build filter
            filter_condition = None
            if doc_ids:
                filter_condition = {
                    "must": [
                        {"key": "document_id", "match": {"any": doc_ids}}
                    ]
                }
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=filter_condition
            )
            
            return [
                {
                    "content": result.payload["content"],
                    "document_id": result.payload["document_id"],
                    "chunk_index": result.payload["chunk_index"],
                    "score": result.score,
                    "metadata": result.payload.get("metadata", {})
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        return await self.embeddings.aembed_query(text)

# =============================================================================
# UPSTASH REDIS SERVICE
# =============================================================================

# =============================================================================
# AUTHENTICATION SERVICE
# =============================================================================

import jwt
import bcrypt

class AuthService:
    def __init__(self, db_service):
        self.db_service = db_service
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_data: TokenData) -> str:
        """Create JWT access token"""
        to_encode = {
            "user_id": user_data.user_id,
            "tenant_id": user_data.tenant_id,
            "email": user_data.email,
            "role": user_data.role.value,
            "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
        }
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return TokenData(
                user_id=payload["user_id"],
                tenant_id=payload["tenant_id"],
                email=payload["email"],
                role=UserRole(payload["role"])
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def register_user(self, request: RegisterRequest) -> AuthResponse:
        """Register new user and tenant"""
        async with self.db_service.pool.acquire() as conn:
            # Check if email already exists
            existing_user = await conn.fetchrow("SELECT user_id FROM users WHERE email = $1", request.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create tenant
            tenant_id = str(uuid4())
            
            # Set quotas based on plan
            if request.plan == PlanType.STARTER:
                api_quota = settings.STARTER_PLAN_API_CALLS
                token_quota = settings.STARTER_PLAN_LLM_TOKENS
            elif request.plan == PlanType.PRO:
                api_quota = settings.PRO_PLAN_API_CALLS
                token_quota = settings.PRO_PLAN_LLM_TOKENS
            else:  # ENTERPRISE
                api_quota = settings.ENTERPRISE_PLAN_API_CALLS
                token_quota = settings.ENTERPRISE_PLAN_LLM_TOKENS
            
            await conn.execute("""
                INSERT INTO tenants (tenant_id, name, plan, api_calls_quota, llm_tokens_quota)
                VALUES ($1, $2, $3, $4, $5)
            """, tenant_id, request.tenant_name, request.plan.value, api_quota, token_quota)
            
            # Create user
            user_id = str(uuid4())
            hashed_password = self.hash_password(request.password)
            
            await conn.execute("""
                INSERT INTO users (user_id, tenant_id, email, hashed_password, role)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, tenant_id, request.email, hashed_password, UserRole.OWNER.value)
            
            # Create response objects
            tenant = TenantInfo(
                tenant_id=tenant_id,
                name=request.tenant_name,
                plan=request.plan,
                api_calls_quota=api_quota,
                llm_tokens_quota=token_quota
            )
            
            user = UserInfo(
                user_id=user_id,
                tenant_id=tenant_id,
                email=request.email,
                role=UserRole.OWNER
            )
            
            token_data = TokenData(
                user_id=user_id,
                tenant_id=tenant_id,
                email=request.email,
                role=UserRole.OWNER
            )
            
            access_token = self.create_access_token(token_data)
            
            return AuthResponse(
                access_token=access_token,
                user=user,
                tenant=tenant
            )
    
    async def login_user(self, request: LoginRequest) -> AuthResponse:
        """Login user"""
        async with self.db_service.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT u.user_id, u.tenant_id, u.email, u.hashed_password, u.role,
                       t.name, t.plan, t.api_calls_quota, t.llm_tokens_quota, t.stripe_customer_id
                FROM users u
                JOIN tenants t ON u.tenant_id = t.tenant_id
                WHERE u.email = $1 AND u.is_active = TRUE AND t.is_active = TRUE
            """, request.email)
            
            if not row or not self.verify_password(request.password, row['hashed_password']):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            tenant = TenantInfo(
                tenant_id=str(row['tenant_id']),
                name=row['name'],
                plan=PlanType(row['plan']),
                stripe_customer_id=row['stripe_customer_id'],
                api_calls_quota=row['api_calls_quota'],
                llm_tokens_quota=row['llm_tokens_quota']
            )
            
            user = UserInfo(
                user_id=str(row['user_id']),
                tenant_id=str(row['tenant_id']),
                email=row['email'],
                role=UserRole(row['role'])
            )
            
            token_data = TokenData(
                user_id=str(row['user_id']),
                tenant_id=str(row['tenant_id']),
                email=row['email'],
                role=UserRole(row['role'])
            )
            
            access_token = self.create_access_token(token_data)
            
            return AuthResponse(
                access_token=access_token,
                user=user,
                tenant=tenant
            )

# =============================================================================
# REDIS SERVICE (Updated for tenant-aware rate limiting)
# =============================================================================

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    async def set_cache(self, key: str, value: Any, ttl: int = 3600):
        """Set cache with TTL"""
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value"""
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def check_rate_limit(self, tenant_id: str, tenant_plan: PlanType) -> tuple[bool, RateLimitInfo]:
        """Check tenant rate limiting with token bucket algorithm"""
        today = datetime.now().strftime('%Y%m%d')
        
        # Get plan limits
        if tenant_plan == PlanType.STARTER:
            api_limit = settings.STARTER_PLAN_API_CALLS
            token_limit = settings.STARTER_PLAN_LLM_TOKENS
        elif tenant_plan == PlanType.PRO:
            api_limit = settings.PRO_PLAN_API_CALLS
            token_limit = settings.PRO_PLAN_LLM_TOKENS
        else:  # ENTERPRISE
            api_limit = settings.ENTERPRISE_PLAN_API_CALLS
            token_limit = settings.ENTERPRISE_PLAN_LLM_TOKENS
        
        # Redis keys for daily usage
        api_key = f"rate_limit:api:{tenant_id}:{today}"
        token_key = f"rate_limit:tokens:{tenant_id}:{today}"
        
        # Get current usage
        current_api_calls = int(await self.redis.get(api_key) or 0)
        current_tokens = int(await self.redis.get(token_key) or 0)
        
        rate_limit_info = RateLimitInfo(
            tenant_id=tenant_id,
            window_start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            api_calls=current_api_calls,
            llm_tokens=current_tokens,
            api_calls_limit=api_limit,
            llm_tokens_limit=token_limit
        )
        
        # Check if within limits
        within_limits = (current_api_calls < api_limit and current_tokens < token_limit)
        
        return within_limits, rate_limit_info

    async def increment_usage(self, tenant_id: str, api_calls: int = 1, llm_tokens: int = 0):
        """Increment usage counters"""
        today = datetime.now().strftime('%Y%m%d')
        
        api_key = f"rate_limit:api:{tenant_id}:{today}"
        token_key = f"rate_limit:tokens:{tenant_id}:{today}"
        
        # Increment counters
        await self.redis.incrby(api_key, api_calls)
        await self.redis.expire(api_key, 86400)  # 24 hours
        
        if llm_tokens > 0:
            await self.redis.incrby(token_key, llm_tokens)
            await self.redis.expire(token_key, 86400)  # 24 hours

# =============================================================================
# STRIPE BILLING SERVICE
# =============================================================================

import stripe

class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    async def create_customer(self, tenant: TenantInfo, user: UserInfo) -> str:
        """Create Stripe customer"""
        customer = stripe.Customer.create(
            email=user.email,
            name=tenant.name,
            metadata={
                'tenant_id': tenant.tenant_id,
                'user_id': user.user_id,
                'plan': tenant.plan.value
            }
        )
        return customer.id
    
    async def create_checkout_session(self, tenant_id: str, plan: PlanType, success_url: str, cancel_url: str):
        """Create Stripe checkout session"""
        price_ids = {
            PlanType.STARTER: "price_starter_monthly",  # Replace with actual Stripe price IDs
            PlanType.PRO: "price_pro_monthly",
            PlanType.ENTERPRISE: "price_enterprise_monthly"
        }
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_ids[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'tenant_id': tenant_id}
        )
        
        return session
    
    async def handle_webhook(self, payload: bytes, sig_header: str):
        """Handle Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'invoice.payment_succeeded':
                # Handle successful payment
                invoice = event['data']['object']
                tenant_id = invoice['metadata'].get('tenant_id')
                
                if tenant_id:
                    # Update tenant status, reset usage, etc.
                    pass
                    
            elif event['type'] == 'invoice.payment_failed':
                # Handle failed payment
                invoice = event['data']['object']
                tenant_id = invoice['metadata'].get('tenant_id')
                
                if tenant_id:
                    # Throttle tenant, send notification, etc.
                    pass
                    
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")

# =============================================================================
# LANGGRAPH AGENT NODES
# =============================================================================

class AgentNodes:
    def __init__(self, memory_service: GraphitiMemoryService, rag_service: QdrantRAGService):
        self.memory_service = memory_service
        self.rag_service = rag_service
        # Use OpenRouter for model access as per playbook
        self.llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model="anthropic/claude-3.5-sonnet",  # Using Claude as specified in playbook
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://agentflow.pro",
            }
        )

    async def cofounder_node(self, state: AgentState) -> AgentState:
        """Co-Founder strategic decision making"""
        agent_id = "cofounder"
        
        # Retrieve agent context and memories
        context = await self.memory_service.get_agent_context(agent_id)
        relevant_memories = await self.memory_service.retrieve_memory(
            agent_id, 
            state["messages"][-1].content if state["messages"] else "",
            limit=5
        )
        
        # Create system prompt
        system_prompt = f"""
        You are Sarah Chen, Co-Founder and Strategic Visionary of AgentFlow Pro.
        
        Your role:
        - Make high-level strategic decisions
        - Provide vision and direction for the company
        - Evaluate opportunities and risks
        - Guide the CEO and leadership team
        
        Context from your memory:
        {json.dumps(context, indent=2)}
        
        Relevant past experiences:
        {json.dumps(relevant_memories, indent=2)}
        
        Always think strategically, consider long-term implications, and provide clear direction.
        If this requires coordination with other team members, indicate who should be involved.
        """
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state["messages"]})
        
        # Store in memory
        await self.memory_service.store_memory(
            agent_id,
            f"User request: {state['messages'][-1].content}\nMy response: {response.content}",
            {"task_id": state["task_id"], "type": "strategic_decision"}
        )
        
        # Update state
        state["messages"].append(response)
        state["reasoning_steps"].append({
            "agent": "cofounder",
            "reasoning": "Analyzed strategic implications and provided high-level direction",
            "decision": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine next step - CoFounder delegates to Manager
        if "delegate to manager" in response.content.lower() or "assign to manager" in response.content.lower():
            state["next_agent"] = "manager"
        else:
            # Default delegation to manager for execution
            state["next_agent"] = "manager"
        
        return state

    async def manager_node(self, state: AgentState) -> AgentState:
        """Manager Agent - Coordinates specialist agents"""
        agent_id = "manager"
        
        context = await self.memory_service.get_agent_context(agent_id)
        relevant_memories = await self.memory_service.retrieve_memory(
            agent_id,
            state["messages"][-1].content,
            limit=5
        )
        
        system_prompt = f"""
        You are Alex Thompson, Manager Agent at AgentFlow Pro.
        
        Your role:
        - Execute strategic decisions from the Co-Founder
        - Coordinate specialized agents (Sales, Support, Growth, DevOps, Legal)
        - Break down complex goals into actionable tasks
        - Manage workflow and consolidate results
        - Provide weekly summaries to the Co-Founder
        
        Context: {json.dumps(context, indent=2)}
        Memories: {json.dumps(relevant_memories, indent=2)}
        
        Analyze the request and determine which specialist agents should be involved.
        Break down the work into specific tasks and coordinate the workflow.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state["messages"]})
        
        await self.memory_service.store_memory(
            agent_id,
            f"Strategic directive: {state['messages'][-2].content}\nExecution plan: {response.content}",
            {"task_id": state["task_id"], "type": "workflow_coordination"}
        )
        
        state["messages"].append(response)
        state["reasoning_steps"].append({
            "agent": "manager",
            "reasoning": "Analyzed requirements and developed coordination strategy",
            "decision": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine next specialist agent based on content (prioritize vertical agents)
        content_lower = response.content.lower()
        
        # Check for vertical industry agents first
        if any(word in content_lower for word in ["legal", "contract", "compliance", "litigation", "law"]):
            state["next_agent"] = "legal_agent"
        elif any(word in content_lower for word in ["finance", "portfolio", "tax", "financial", "investment"]):
            state["next_agent"] = "finance_agent"
        elif any(word in content_lower for word in ["healthcare", "medical", "patient", "hipaa", "clinic"]):
            state["next_agent"] = "healthcare_agent"
        elif any(word in content_lower for word in ["manufacturing", "production", "quality", "assembly", "maintenance"]):
            state["next_agent"] = "manufacturing_agent"
        elif any(word in content_lower for word in ["ecommerce", "shopify", "cart", "product", "e-commerce"]):
            state["next_agent"] = "ecommerce_agent"
        elif any(word in content_lower for word in ["coaching", "coach", "training", "mentoring", "consulting"]):
            state["next_agent"] = "coaching_agent"
        
        # Fallback to generic agents
        elif "sales" in content_lower or "revenue" in content_lower or "leads" in content_lower:
            state["next_agent"] = "sales"
        elif "support" in content_lower or "customer" in content_lower or "tickets" in content_lower:
            state["next_agent"] = "support"
        elif "growth" in content_lower or "marketing" in content_lower or "campaigns" in content_lower:
            state["next_agent"] = "growth"
        else:
            # Default to sales for business-related tasks
            state["next_agent"] = "sales"
        
        return state

    async def specialist_node(self, state: AgentState, agent_role: str) -> AgentState:
        """Generic specialist node for department heads"""
        agent_id = agent_role
        
        # Get agent-specific context
        context = await self.memory_service.get_agent_context(agent_id)
        relevant_memories = await self.memory_service.retrieve_memory(
            agent_id,
            state["messages"][-1].content,
            limit=5
        )
        
        # Get relevant documents if specified
        rag_context = ""
        if state.get("context", {}).get("documents"):
            doc_results = await self.rag_service.search_documents(
                state["messages"][-1].content,
                limit=3,
                doc_ids=state["context"]["documents"]
            )
            rag_context = "\n".join([doc["content"] for doc in doc_results])
        
        # Role-specific prompts matching PRD vertical agents
        role_prompts = {
            # Vertical Industry Agents (as per playbook)
            "legal_agent": """
            You are Sarah Wilson, Legal Tech Specialist at AgentFlow Pro.
            Specialized in: Contract analysis, legal research, e-discovery, litigation support, regulatory compliance.
            Tools: contract_analysis, legal_research, e_discovery, compliance_checking, litigation_support.
            Focus on accuracy, data privacy, and regulatory compliance for legal industry clients.
            """,
            "finance_agent": """
            You are Michael Chen, Financial Advisory Specialist at AgentFlow Pro.
            Specialized in: Portfolio analysis, tax law interpretation, compliance documents, financial modeling.
            Tools: portfolio_analysis, tax_code_retrieval, compliance_docs, financial_modeling, risk_assessment.
            Focus on regulatory compliance, tax optimization, and portfolio management for SMB financial advisors.
            """,
            "healthcare_agent": """
            You are Dr. Lisa Park, Healthcare Specialist at AgentFlow Pro.
            Specialized in: Patient data analysis, treatment planning, HIPAA-compliant automation, medical FAQ.
            Tools: patient_data_analysis, treatment_planning, hipaa_compliance, medical_faq, appointment_scheduling.
            Focus on HIPAA compliance, patient care optimization, and administrative automation for small clinics.
            """,
            "manufacturing_agent": """
            You are Robert Kim, Manufacturing Specialist at AgentFlow Pro.
            Specialized in: Predictive maintenance, quality control, smart assembly guidance, production optimization.
            Tools: predictive_maintenance, quality_control, assembly_guidance, machine_vision, production_optimization.
            Focus on automation, predictive maintenance, and quality control for manufacturing operations.
            """,
            "ecommerce_agent": """
            You are Jennifer Lopez, E-commerce Specialist at AgentFlow Pro.
            Specialized in: Abandoned cart recovery, product recommendations, Shopify automation, WhatsApp integration.
            Tools: cart_recovery, product_recommendations, shopify_integration, whatsapp_automation, review_analysis.
            Focus on conversion optimization and customer retention for Shopify stores and e-commerce businesses.  
            """,
            "coaching_agent": """
            You are David Martinez, Coaching Industry Specialist at AgentFlow Pro.
            Specialized in: Lead follow-up automation, client management, CRM integration, performance tracking.
            Tools: lead_followup, client_management, crm_integration, email_automation, performance_tracking.
            Focus on lead nurturing, client management, and performance analytics for coaches and consultants.
            """,
            # Generic Support Agents
            "sales": """
            You are Elena Rodriguez, Sales Agent at AgentFlow Pro.
            Focus on: lead generation, client acquisition, revenue growth, CRM management, sales pipelines.
            Use LangChain tools for sales automation and customer relationship management.
            """,
            "support": """
            You are Amanda Green, Support Agent at AgentFlow Pro.
            Focus on: customer satisfaction, issue resolution, support processes, client success, retention.
            Use LangChain tools for ticket management and customer analytics.
            """,
            "growth": """
            You are Maria Garcia, Growth Agent at AgentFlow Pro.
            Focus on: marketing campaigns, growth hacking, user acquisition, retention strategies, analytics.
            Use LangChain tools for campaign management and growth analytics.
            """
        }
        
        system_prompt = f"""
        {role_prompts.get(agent_role, f"You are a {agent_role} at AgentFlow Pro.")}
        
        Context: {json.dumps(context, indent=2)}
        Memories: {json.dumps(relevant_memories, indent=2)}
        
        Relevant Documents:
        {rag_context}
        
        Provide specific, actionable recommendations within your area of expertise.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state["messages"]})
        
        await self.memory_service.store_memory(
            agent_id,
            f"Task: {state['messages'][-1].content}\nRecommendation: {response.content}",
            {"task_id": state["task_id"], "type": "specialist_analysis"}
        )
        
        state["messages"].append(response)
        state["reasoning_steps"].append({
            "agent": agent_role,
            "reasoning": f"Applied {agent_role} expertise to provide specialized recommendations",
            "decision": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        return state

# =============================================================================
# LANGGRAPH ORCHESTRATOR
# =============================================================================

class LangGraphOrchestrator:
    def __init__(self, memory_service: GraphitiMemoryService, rag_service: QdrantRAGService):
        self.memory_service = memory_service
        self.rag_service = rag_service
        self.agent_nodes = AgentNodes(memory_service, rag_service)
        self.agents = self._initialize_agents()
        self.workflows = {}
        self._build_workflows()

    def _initialize_agents(self) -> Dict[str, AgentConfig]:
        """Initialize agent configurations"""
        agents = {}
        
        # Co-Founder Agent
        cofounder = AgentConfig(
            id="cofounder",
            name="Sarah Chen",
            role=AgentRole.COFOUNDER,
            department=Department.LEADERSHIP,
            level=1,
            system_prompt="Strategic visionary focused on long-term growth and direction",
            tools=["strategic_planning", "market_analysis", "investor_relations"],
            specializations=["Strategic Vision", "Market Analysis", "Leadership"],
            performance_metrics={
                "decisions_made": 45,
                "strategic_accuracy": 92.0,
                "team_satisfaction": 4.8
            }
        )
        
        # Manager Agent
        manager = AgentConfig(
            id="manager",
            name="Alex Thompson",
            role=AgentRole.MANAGER,
            department=Department.OPERATIONS,
            level=2,
            manager_id="cofounder",
            system_prompt="Workflow coordinator focused on task distribution and execution",
            tools=["team_coordination", "workflow_management", "reporting"],
            specializations=["Workflow Management", "Team Coordination", "Execution"],
            performance_metrics={
                "tasks_coordinated": 120,
                "team_efficiency": 89.0,
                "goal_achievement": 94.0
            }
        )
        
        # Vertical Industry Agents (as per playbook)
        legal_agent = AgentConfig(
            id="legal_agent",
            name="Sarah Wilson",
            role=AgentRole.LEGAL_AGENT,
            department=Department.OPERATIONS,
            level=3,
            manager_id="manager",
            system_prompt="Legal Tech specialist for contract analysis, legal research, and e-discovery. Handles litigation support and compliance checking.",
            tools=["contract_analysis", "legal_research", "e_discovery", "compliance_checking", "litigation_support"],
            specializations=["Contract Law", "Legal Research", "E-Discovery", "Regulatory Compliance"],
            performance_metrics={
                "contracts_processed": 45,
                "legal_research_queries": 120,
                "compliance_score": 98.0
            }
        )
        
        finance_agent = AgentConfig(
            id="finance_agent",
            name="Michael Chen",
            role=AgentRole.FINANCE_AGENT,
            department=Department.FINANCE,
            level=3,
            manager_id="manager",
            system_prompt="Financial Advisory specialist for portfolio analysis, tax law interpretation, and compliance document processing.",
            tools=["portfolio_analysis", "tax_code_retrieval", "compliance_docs", "financial_modeling", "risk_assessment"],
            specializations=["Portfolio Management", "Tax Law", "Financial Compliance", "Risk Analysis"],
            performance_metrics={
                "portfolios_analyzed": 35,
                "tax_queries_resolved": 180,
                "compliance_reports": 22
            }
        )
        
        healthcare_agent = AgentConfig(
            id="healthcare_agent",
            name="Dr. Lisa Park",
            role=AgentRole.HEALTHCARE_AGENT,
            department=Department.SUPPORT,
            level=3,
            manager_id="manager",
            system_prompt="Healthcare specialist focused on patient data analysis, treatment planning, and HIPAA-compliant administrative automation.",
            tools=["patient_data_analysis", "treatment_planning", "hipaa_compliance", "medical_faq", "appointment_scheduling"],
            specializations=["Patient Care", "Treatment Planning", "HIPAA Compliance", "Medical Records"],
            performance_metrics={
                "patients_processed": 150,
                "treatment_plans_created": 45,
                "compliance_score": 99.5
            }
        )
        
        manufacturing_agent = AgentConfig(
            id="manufacturing_agent",
            name="Robert Kim",
            role=AgentRole.MANUFACTURING_AGENT,
            department=Department.OPERATIONS,
            level=3,
            manager_id="manager",
            system_prompt="Manufacturing specialist for predictive maintenance, quality control, and smart assembly guidance.",
            tools=["predictive_maintenance", "quality_control", "assembly_guidance", "machine_vision", "production_optimization"],
            specializations=["Predictive Maintenance", "Quality Control", "Assembly Automation", "Production Optimization"],
            performance_metrics={
                "maintenance_predictions": 25,
                "quality_checks": 500,
                "assembly_guides_created": 15
            }
        )
        
        ecommerce_agent = AgentConfig(
            id="ecommerce_agent",
            name="Jennifer Lopez",
            role=AgentRole.ECOMMERCE_AGENT,
            department=Department.SALES,
            level=3,
            manager_id="manager",
            system_prompt="E-commerce specialist for abandoned cart recovery, product recommendations, and Shopify store automation.",
            tools=["cart_recovery", "product_recommendations", "shopify_integration", "whatsapp_automation", "review_analysis"],
            specializations=["Cart Recovery", "Product Recommendations", "Shopify Automation", "Customer Retention"],
            performance_metrics={
                "carts_recovered": 180,
                "recommendations_generated": 1200,
                "conversion_rate_improvement": 15.5
            }
        )
        
        coaching_agent = AgentConfig(
            id="coaching_agent",
            name="David Martinez",
            role=AgentRole.COACHING_AGENT,
            department=Department.SALES,
            level=3,
            manager_id="manager",
            system_prompt="Coaching industry specialist for lead follow-up automation and client management.",
            tools=["lead_followup", "client_management", "crm_integration", "email_automation", "performance_tracking"],
            specializations=["Lead Nurturing", "Client Management", "CRM Automation", "Performance Analytics"],
            performance_metrics={
                "leads_followed_up": 320,
                "clients_managed": 85,
                "conversion_rate": 22.0
            }
        )
        
        # Generic Support Agents  
        sales_agent = AgentConfig(
            id="sales",
            name="Elena Rodriguez",
            role=AgentRole.SALES,
            department=Department.SALES,
            level=3,
            manager_id="manager",
            system_prompt="General sales expert focused on revenue growth and client acquisition",
            tools=["crm_management", "lead_scoring", "sales_analytics"],
            specializations=["B2B Sales", "Client Relations", "Revenue Optimization"],
            performance_metrics={
                "deals_closed": 28,
                "conversion_rate": 18.5,
                "revenue_generated": 450000
            }
        )
        
        support_agent = AgentConfig(
            id="support",
            name="Amanda Green",
            role=AgentRole.SUPPORT,
            department=Department.SUPPORT,
            level=3,
            manager_id="manager",
            system_prompt="Customer support expert focused on satisfaction and retention",
            tools=["ticket_management", "customer_analytics", "satisfaction_tracking"],
            specializations=["Customer Success", "Issue Resolution", "Retention"],
            performance_metrics={
                "tickets_resolved": 340,
                "satisfaction_score": 4.7,
                "resolution_time": 2.3
            }
        )
        
        growth_agent = AgentConfig(
            id="growth",
            name="Maria Garcia",
            role=AgentRole.GROWTH,
            department=Department.MARKETING,
            level=3,
            manager_id="manager",
            system_prompt="Growth expert focused on marketing campaigns and user acquisition",
            tools=["campaign_management", "analytics", "growth_hacking"],
            specializations=["Growth Marketing", "User Acquisition", "Analytics"],
            performance_metrics={
                "campaigns_launched": 15,
                "engagement_rate": 12.3,
                "lead_generation": 850
            }
        )
        
        all_agents = [
            cofounder, manager,
            # Vertical Industry Agents
            legal_agent, finance_agent, healthcare_agent, 
            manufacturing_agent, ecommerce_agent, coaching_agent,
            # Generic Support Agents
            sales_agent, support_agent, growth_agent
        ]
        
        for agent in all_agents:
            agents[agent.id] = agent
            
        return agents

    def _build_workflows(self):
        """Build LangGraph workflows following PRD agent hierarchy"""
        
        # Main orchestration workflow
        workflow = StateGraph(AgentState)
        
        # Add agent nodes following PRD hierarchy: CoFounder → Manager → Vertical Specialists
        workflow.add_node("cofounder", self.agent_nodes.cofounder_node)
        workflow.add_node("manager", self.agent_nodes.manager_node)
        
        # Vertical Industry Agents
        workflow.add_node("legal_agent", lambda state: self.agent_nodes.specialist_node(state, "legal_agent"))
        workflow.add_node("finance_agent", lambda state: self.agent_nodes.specialist_node(state, "finance_agent"))
        workflow.add_node("healthcare_agent", lambda state: self.agent_nodes.specialist_node(state, "healthcare_agent"))
        workflow.add_node("manufacturing_agent", lambda state: self.agent_nodes.specialist_node(state, "manufacturing_agent"))
        workflow.add_node("ecommerce_agent", lambda state: self.agent_nodes.specialist_node(state, "ecommerce_agent"))
        workflow.add_node("coaching_agent", lambda state: self.agent_nodes.specialist_node(state, "coaching_agent"))
        
        # Generic Support Agents
        workflow.add_node("sales", lambda state: self.agent_nodes.specialist_node(state, "sales"))
        workflow.add_node("support", lambda state: self.agent_nodes.specialist_node(state, "support"))
        workflow.add_node("growth", lambda state: self.agent_nodes.specialist_node(state, "growth"))
        
        # Add conditional edges based on next_agent
        def route_agent(state: AgentState) -> str:
            next_agent = state.get("next_agent")
            if next_agent and next_agent in self.agents:
                return next_agent
            elif state.get("escalate"):
                return "cofounder"
            else:
                return END
        
        # Set up routing - CoFounder delegates to Manager
        workflow.add_conditional_edges(
            "cofounder",
            route_agent,
            ["manager", END]
        )
        
        # Manager delegates to appropriate specialists (both vertical and generic)
        all_specialists = [
            "legal_agent", "finance_agent", "healthcare_agent", 
            "manufacturing_agent", "ecommerce_agent", "coaching_agent",
            "sales", "support", "growth"
        ]
        
        workflow.add_conditional_edges(
            "manager",
            route_agent,
            all_specialists + [END]
        )
        
        # All specialists report back to Manager or complete
        for specialist in all_specialists:
            workflow.add_conditional_edges(
                specialist,
                route_agent,
                ["manager", END]
            )
        
        # Set entry point
        workflow.set_entry_point("cofounder")
        
        # Compile workflow
        memory = MemorySaver()
        self.workflows["main"] = workflow.compile(checkpointer=memory)

    async def process_task(self, task: TaskRequest, user_id: str) -> TaskResponse:
        """Process task through agent workflow"""
        task_id = str(uuid4())
        
        # Create initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=f"{task.title}: {task.description}")],
            task_id=task_id,
            agent_id="cofounder",
            context=task.context,
            next_agent=None,
            escalate=False,
            final_result=None,
            reasoning_steps=[]
        )
        
        try:
            # Run workflow
            config = {"configurable": {"thread_id": task_id}}
            final_state = await self.workflows["main"].ainvoke(initial_state, config)
            
            # Create response
            task_response = TaskResponse(
                id=task_id,
                title=task.title,
                description=task.description,
                status=TaskStatus.COMPLETED,
                priority=task.priority,
                assigned_to=final_state.get("agent_id"),
                created_by=user_id,
                result=final_state.get("final_result"),
                reasoning_chain=final_state.get("reasoning_steps", [])
            )
            
            return task_response
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            return TaskResponse(
                id=task_id,
                title=task.title,
                description=task.description,
                status=TaskStatus.FAILED,
                priority=task.priority,
                created_by=user_id,
                error_message=str(e)
            )

# =============================================================================
# DATABASE SERVICES
# =============================================================================

class DatabaseService:
    def __init__(self):
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(settings.POSTGRES_URL)
            await self._create_tables()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
            
    async def _create_tables(self):
        """Create database tables following PRD schema"""
        async with self.pool.acquire() as conn:
            # Enable pgvector extension for embeddings
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Tenants table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    tenant_id UUID PRIMARY KEY,
                    name TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    stripe_customer_id TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    api_calls_quota INTEGER NOT NULL,
                    llm_tokens_quota BIGINT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Enable Row Level Security
            await conn.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
            await conn.execute("""
                CREATE POLICY IF NOT EXISTS tenant_isolation ON users
                USING (tenant_id = current_setting('app.current_tenant_id')::UUID)
            """)
            
            # Agent States table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    state_id SERIAL PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    agent_name TEXT NOT NULL,
                    state_json JSONB NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Memory Records table with pgvector
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_records (
                    record_id SERIAL PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    agent_name TEXT NOT NULL,
                    embedding VECTOR(1536),
                    text TEXT NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Tasks table (tenant-aware)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id UUID PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) NOT NULL,
                    priority VARCHAR(50) NOT NULL,
                    assigned_to VARCHAR(100),
                    created_by UUID REFERENCES users(user_id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    result JSONB,
                    execution_log JSONB DEFAULT '[]'::jsonb,
                    reasoning_chain JSONB DEFAULT '[]'::jsonb,
                    error_message TEXT,
                    escalation_reason TEXT
                )
            """)
            
            # Chat messages table (tenant-aware)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id UUID PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    session_id VARCHAR(100) NOT NULL,
                    user_id UUID REFERENCES users(user_id),
                    agent_id VARCHAR(100),
                    message TEXT NOT NULL,
                    message_type VARCHAR(50) NOT NULL,
                    context JSONB DEFAULT '{}'::jsonb,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Invoices table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id UUID PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    stripe_invoice_id TEXT,
                    status TEXT NOT NULL,
                    amount_due BIGINT NOT NULL,
                    paid_at TIMESTAMPTZ
                )
            """)
            
            # Rate limits table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    tenant_id UUID PRIMARY KEY REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    window_start TIMESTAMPTZ NOT NULL,
                    api_calls INT DEFAULT 0,
                    llm_tokens BIGINT DEFAULT 0
                )
            """)
            
            # Documents table (tenant-aware)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    filename VARCHAR(255) NOT NULL,
                    content_type VARCHAR(100),
                    size INTEGER,
                    processed BOOLEAN DEFAULT FALSE,
                    chunks_count INTEGER DEFAULT 0,
                    uploaded_at TIMESTAMP DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                )
            """)
            
            # Outcome-based usage tracking table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS outcome_usage (
                    usage_id SERIAL PRIMARY KEY,
                    tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    agent_id TEXT NOT NULL,
                    outcome_metric TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1,
                    rate_per_outcome DECIMAL(10,2) NOT NULL,
                    total_amount BIGINT NOT NULL,
                    recorded_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create indexes for performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_tenant_id ON tasks(tenant_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_tenant_id ON chat_messages(tenant_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_states_tenant_id ON agent_states(tenant_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_records_tenant_id ON memory_records(tenant_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_tenant_id ON documents(tenant_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_outcome_usage_tenant_id ON outcome_usage(tenant_id)")

    async def save_task(self, task: TaskResponse):
        """Save task to database"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO tasks (
                    id, title, description, status, priority, assigned_to, created_by,
                    created_at, updated_at, completed_at, result, execution_log,
                    reasoning_chain, error_message, escalation_reason
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at,
                    completed_at = EXCLUDED.completed_at,
                    result = EXCLUDED.result,
                    execution_log = EXCLUDED.execution_log,
                    reasoning_chain = EXCLUDED.reasoning_chain,
                    error_message = EXCLUDED.error_message,
                    escalation_reason = EXCLUDED.escalation_reason
            """, 
                task.id, task.title, task.description, task.status.value, task.priority.value,
                task.assigned_to, task.created_by, task.created_at, task.updated_at,
                task.completed_at, json.dumps(task.result) if task.result else None,
                json.dumps(task.execution_log), json.dumps(task.reasoning_chain),
                task.error_message, task.escalation_reason
            )

    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get task by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", task_id)
            if row:
                return TaskResponse(
                    id=str(row['id']),
                    title=row['title'],
                    description=row['description'],
                    status=TaskStatus(row['status']),
                    priority=TaskPriority(row['priority']),
                    assigned_to=row['assigned_to'],
                    created_by=row['created_by'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    completed_at=row['completed_at'],
                    result=json.loads(row['result']) if row['result'] else None,
                    execution_log=json.loads(row['execution_log']),
                    reasoning_chain=json.loads(row['reasoning_chain']),
                    error_message=row['error_message'],
                    escalation_reason=row['escalation_reason']
                )
        return None

    async def get_user_tasks(self, user_id: str, limit: int = 50) -> List[TaskResponse]:
        """Get tasks for a user"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM tasks WHERE created_by = $1 ORDER BY created_at DESC LIMIT $2",
                user_id, limit
            )
            return [
                TaskResponse(
                    id=str(row['id']),
                    title=row['title'],
                    description=row['description'],
                    status=TaskStatus(row['status']),
                    priority=TaskPriority(row['priority']),
                    assigned_to=row['assigned_to'],
                    created_by=row['created_by'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    completed_at=row['completed_at'],
                    result=json.loads(row['result']) if row['result'] else None,
                    execution_log=json.loads(row['execution_log']),
                    reasoning_chain=json.loads(row['reasoning_chain']),
                    error_message=row['error_message'],
                    escalation_reason=row['escalation_reason']
                )
                for row in rows
            ]

    async def save_chat_message(self, message: ChatMessage):
        """Save chat message"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_messages (
                    id, session_id, user_id, agent_id, message, message_type, context, timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                message.id, message.session_id, message.user_id, message.agent_id,
                message.message, message.message_type.value, json.dumps(message.context),
                message.timestamp
            )

    async def get_chat_history(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat history for session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM chat_messages WHERE session_id = $1 
                   ORDER BY timestamp DESC LIMIT $2""",
                session_id, limit
            )
            return [
                ChatMessage(
                    id=str(row['id']),
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    agent_id=row['agent_id'],
                    message=row['message'],
                    message_type=MessageType(row['message_type']),
                    context=json.loads(row['context']),
                    timestamp=row['timestamp']
                )
                for row in reversed(rows)
            ]

    async def save_document(self, doc: DocumentUpload):
        """Save document metadata"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO documents (
                    id, filename, content_type, size, processed, chunks_count, uploaded_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO UPDATE SET
                    processed = EXCLUDED.processed,
                    chunks_count = EXCLUDED.chunks_count
            """,
                doc.id, doc.filename, doc.content_type, doc.size,
                doc.processed, doc.chunks_count, doc.uploaded_at,
                json.dumps(doc.metadata)
            )

# =============================================================================
# WEBSOCKET MANAGER
# =============================================================================

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
            
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

# =============================================================================
# AUTHENTICATION
# =============================================================================

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Verify JWT token and return user data"""
    try:
        token = credentials.credentials
        return auth_service.verify_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_tenant_info(current_user: TokenData = Depends(get_current_user)) -> tuple[TokenData, TenantInfo]:
    """Get current user and tenant information"""
    async with db_service.pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT t.tenant_id, t.name, t.plan, t.stripe_customer_id, 
                   t.api_calls_quota, t.llm_tokens_quota, t.is_active
            FROM tenants t
            WHERE t.tenant_id = $1 AND t.is_active = TRUE
        """, current_user.tenant_id)
        
        if not row:
            raise HTTPException(status_code=403, detail="Tenant not found or inactive")
        
        tenant = TenantInfo(
            tenant_id=str(row['tenant_id']),
            name=row['name'],
            plan=PlanType(row['plan']),
            stripe_customer_id=row['stripe_customer_id'],
            api_calls_quota=row['api_calls_quota'],
            llm_tokens_quota=row['llm_tokens_quota'],
            is_active=row['is_active']
        )
        
        return current_user, tenant

async def check_rate_limit_middleware(user_tenant: tuple[TokenData, TenantInfo] = Depends(get_current_tenant_info)):
    """Check rate limits for tenant"""
    user, tenant = user_tenant
    
    within_limits, rate_info = await redis_service.check_rate_limit(tenant.tenant_id, tenant.plan)
    
    if not within_limits:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please upgrade your plan or wait for the next billing cycle.",
            headers={
                "X-RateLimit-Limit-API": str(rate_info.api_calls_limit),
                "X-RateLimit-Remaining-API": str(max(0, rate_info.api_calls_limit - rate_info.api_calls)),
                "X-RateLimit-Limit-Tokens": str(rate_info.llm_tokens_limit),
                "X-RateLimit-Remaining-Tokens": str(max(0, rate_info.llm_tokens_limit - rate_info.llm_tokens))
            }
        )
    
    return user, tenant

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AgentFlow Pro Backend...")
    
    # Initialize services
    global db_service, memory_service, rag_service, redis_service, orchestrator, ws_manager
    
    db_service = DatabaseService()
    await db_service.initialize()
    
    # Initialize Neo4j connection
    neo4j_driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    memory_service = GraphitiMemoryService(neo4j_driver)
    await memory_service.initialize()
    
    rag_service = QdrantRAGService()
    await rag_service.initialize()
    
    redis_service = RedisService()
    
    auth_service = AuthService(db_service)
    
    stripe_service = StripeService()
    
    orchestrator = LangGraphOrchestrator(memory_service, rag_service)
    
    ws_manager = WebSocketManager()
    
    logger.info("AgentFlow Pro Backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AgentFlow Pro Backend...")
    if db_service.pool:
        await db_service.pool.close()
    await neo4j_driver.close()

# Initialize FastAPI app
app = FastAPI(
    title="AgentFlow Pro Backend",
    description="Complete AI Agent Orchestration Platform with LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (initialized in lifespan)
db_service: DatabaseService = None
memory_service: GraphitiMemoryService = None
rag_service: QdrantRAGService = None
redis_service: RedisService = None
auth_service: AuthService = None
stripe_service: StripeService = None
orchestrator: LangGraphOrchestrator = None
ws_manager: WebSocketManager = None

# =============================================================================
# API ROUTES
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AgentFlow Pro Backend is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user and tenant"""
    return await auth_service.register_user(request)

@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    return await auth_service.login_user(request)

@app.get("/auth/me")
async def get_current_user_info(user_tenant: tuple[TokenData, TenantInfo] = Depends(get_current_tenant_info)):
    """Get current user and tenant information"""
    user, tenant = user_tenant
    return {
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "tenant_id": user.tenant_id
        },
        "tenant": {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "plan": tenant.plan.value,
            "api_calls_quota": tenant.api_calls_quota,
            "llm_tokens_quota": tenant.llm_tokens_quota
        }
    }

# =============================================================================
# BILLING ROUTES
# =============================================================================

@app.post("/billing/create-checkout-session")
async def create_checkout_session(
    plan: PlanType,
    success_url: str,
    cancel_url: str,
    user_tenant: tuple[TokenData, TenantInfo] = Depends(get_current_tenant_info)
):
    """Create Stripe checkout session"""
    user, tenant = user_tenant
    
    # Only owners can change billing
    if user.role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Only tenant owners can manage billing")
    
    session = await stripe_service.create_checkout_session(
        tenant.tenant_id, plan, success_url, cancel_url
    )
    
    return {"checkout_url": session.url}

@app.post("/billing/webhook")
async def stripe_webhook(request: httpx.Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    await stripe_service.handle_webhook(payload, sig_header)
    
    return {"status": "success"}

@app.get("/billing/usage")
async def get_usage_info(user_tenant: tuple[TokenData, TenantInfo] = Depends(get_current_tenant_info)):
    """Get current usage information"""
    user, tenant = user_tenant
    
    within_limits, rate_info = await redis_service.check_rate_limit(tenant.tenant_id, tenant.plan)
    
    return {
        "tenant_id": tenant.tenant_id,
        "plan": tenant.plan.value,
        "usage": {
            "api_calls": rate_info.api_calls,
            "api_calls_limit": rate_info.api_calls_limit,
            "llm_tokens": rate_info.llm_tokens,
            "llm_tokens_limit": rate_info.llm_tokens_limit,
            "within_limits": within_limits
        },
        "window_start": rate_info.window_start.isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected" if db_service.pool else "disconnected",
            "memory": "connected" if memory_service else "disconnected",
            "rag": "connected" if rag_service else "disconnected",
            "redis": "connected" if redis_service else "disconnected"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents", response_model=List[AgentConfig])
async def get_agents(user_tenant: tuple[TokenData, TenantInfo] = Depends(check_rate_limit_middleware)):
    """Get all available agents"""
    user, tenant = user_tenant
    return list(orchestrator.agents.values())

@app.get("/agents/vertical", response_model=List[AgentConfig])
async def get_vertical_agents(user_tenant: tuple[TokenData, TenantInfo] = Depends(check_rate_limit_middleware)):
    """Get vertical industry agent templates (as per playbook)"""
    user, tenant = user_tenant
    
    vertical_agent_ids = [
        "legal_agent", "finance_agent", "healthcare_agent", 
        "manufacturing_agent", "ecommerce_agent", "coaching_agent"
    ]
    
    vertical_agents = [
        orchestrator.agents[agent_id] 
        for agent_id in vertical_agent_ids 
        if agent_id in orchestrator.agents
    ]
    
    return vertical_agents

@app.get("/agents/{agent_id}", response_model=AgentConfig)
async def get_agent(agent_id: str, user_tenant: tuple[TokenData, TenantInfo] = Depends(check_rate_limit_middleware)):
    """Get specific agent"""
    user, tenant = user_tenant
    
    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return orchestrator.agents[agent_id]

@app.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Create and process a new task"""
    
    # Check rate limit
    if not await redis_service.check_rate_limit(current_user):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    await redis_service.increment_rate_limit(current_user)
    
    # Process task
    task_response = await orchestrator.process_task(task, current_user)
    
    # Save to database
    background_tasks.add_task(db_service.save_task, task_response)
    
    # Send WebSocket notification
    if current_user in ws_manager.active_connections:
        await ws_manager.send_personal_message(
            json.dumps({
                "type": "task_update",
                "task_id": task_response.id,
                "status": task_response.status.value
            }),
            current_user
        )
    
    return task_response

@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """Get user's tasks"""
    return await db_service.get_user_tasks(current_user, limit)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: str = Depends(get_current_user)):
    """Get specific task"""
    task = await db_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user owns the task
    if task.created_by != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task

@app.post("/chat/{session_id}")
async def chat(
    session_id: str,
    message: str,
    agent_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Chat with agents"""
    
    # Save user message
    user_message = ChatMessage(
        session_id=session_id,
        user_id=current_user,
        message=message,
        message_type=MessageType.HUMAN
    )
    await db_service.save_chat_message(user_message)
    
    # Create task from chat message
    task = TaskRequest(
        title="Chat Request",
        description=message,
        priority=TaskPriority.MEDIUM
    )
    
    # Process through orchestrator
    task_response = await orchestrator.process_task(task, current_user)
    
    # Create AI response message
    ai_response = task_response.reasoning_chain[-1]["decision"] if task_response.reasoning_chain else "I'm processing your request."
    
    ai_message = ChatMessage(
        session_id=session_id,
        user_id=current_user,
        agent_id=task_response.assigned_to,
        message=ai_response,
        message_type=MessageType.AI
    )
    await db_service.save_chat_message(ai_message)
    
    return {
        "response": ai_response,
        "agent_id": task_response.assigned_to,
        "reasoning_chain": task_response.reasoning_chain
    }

@app.get("/chat/{session_id}/history", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """Get chat history"""
    return await db_service.get_chat_history(session_id, limit)

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload and process document"""
    
    # Save uploaded file
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process document
    doc_id = str(uuid4())
    try:
        doc_upload = await rag_service.process_document(file_path, doc_id)
        await db_service.save_document(doc_upload)
        
        # Clean up temp file
        os.remove(file_path)
        
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "status": "processed",
            "chunks_count": doc_upload.chunks_count
        }
        
    except Exception as e:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

@app.get("/documents/search")
async def search_documents(
    query: str,
    limit: int = 5,
    document_ids: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Search documents using RAG"""
    doc_ids = document_ids.split(",") if document_ids else None
    results = await rag_service.search_documents(query, limit, doc_ids)
    return {"results": results}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            await ws_manager.send_personal_message(f"Echo: {data}", user_id)
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(current_user: str = Depends(get_current_user)):
    """Get dashboard analytics"""
    # This would typically fetch real analytics from the database
    return {
        "total_tasks": 156,
        "completed_tasks": 142,
        "active_agents": 6,
        "avg_completion_time": "2.3 hours",
        "agent_performance": {
            agent_id: agent.performance_metrics
            for agent_id, agent in orchestrator.agents.items()
        },
        "recent_activity": [
            {
                "timestamp": (datetime.now() - timedelta(minutes=i*10)).isoformat(),
                "type": "task_completed",
                "agent": list(orchestrator.agents.keys())[i % len(orchestrator.agents)],
                "description": f"Completed task #{150 + i}"
            }
            for i in range(10)
        ]
    }

# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )