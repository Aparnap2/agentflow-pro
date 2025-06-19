import asyncpg
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models import auth, task, agent

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None

    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
            await self._create_tables()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def _create_tables(self):
        """Create necessary database tables"""
        sql = """
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            plan TEXT NOT NULL,
            stripe_customer_id TEXT,
            api_calls_quota INTEGER NOT NULL,
            llm_tokens_quota INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY,
            tenant_id UUID REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS tasks (
            task_id UUID PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            assigned_to UUID REFERENCES users(user_id) ON DELETE SET NULL,
            created_by UUID REFERENCES users(user_id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            result JSONB,
            execution_log JSONB[],
            reasoning_chain JSONB[],
            error_message TEXT,
            escalation_reason TEXT
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id UUID PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
            agent_id UUID,
            message TEXT NOT NULL,
            message_type TEXT NOT NULL,
            context JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS documents (
            document_id UUID PRIMARY KEY,
            filename TEXT NOT NULL,
            content_type TEXT NOT NULL,
            size INTEGER NOT NULL,
            processed BOOLEAN DEFAULT false,
            chunks_count INTEGER DEFAULT 0,
            metadata JSONB,
            uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(sql)
            logger.info("Database tables verified/created")

    async def save_task(self, task: task.TaskResponse):
        """Save task to database"""
        sql = """
        INSERT INTO tasks (
            task_id, title, description, status, priority, assigned_to, 
            created_by, created_at, updated_at, completed_at, result, 
            execution_log, reasoning_chain, error_message, escalation_reason
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                sql,
                task.id, task.title, task.description, task.status.value, 
                task.priority.value, task.assigned_to, task.created_by,
                task.created_at, task.updated_at, task.completed_at, 
                task.result, task.execution_log, task.reasoning_chain,
                task.error_message, task.escalation_reason
            )

    async def get_task(self, task_id: str):
        """Get task by ID"""
        sql = "SELECT * FROM tasks WHERE task_id = $1"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(sql, task_id)
            return dict(row) if row else None

    async def save_chat_message(self, message: agent.ChatMessage):
        """Save chat message to database"""
        sql = """
        INSERT INTO chat_messages (
            message_id, session_id, user_id, agent_id, message, 
            message_type, context, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                sql,
                message.id, message.session_id, message.user_id, message.agent_id,
                message.message, message.message_type, message.context, message.timestamp
            )

    async def get_chat_history(self, session_id: str, limit: int = 50):
        """Get chat history for a session"""
        sql = """
        SELECT * FROM chat_messages 
        WHERE session_id = $1 
        ORDER BY created_at DESC 
        LIMIT $2
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, session_id, limit)
            return [dict(row) for row in rows]

    async def save_document(self, doc: agent.DocumentUpload):
        """Save document metadata to database"""
        sql = """
        INSERT INTO documents (
            document_id, filename, content_type, size, 
            processed, chunks_count, metadata, uploaded_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                sql,
                doc.id, doc.filename, doc.content_type, doc.size,
                doc.processed, doc.chunks_count, doc.metadata, doc.uploaded_at
            )
