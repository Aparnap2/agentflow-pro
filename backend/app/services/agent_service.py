"""Service layer for agent-related operations."""
from typing import Dict, List, Optional, Any, Type, TypeVar, Union
from datetime import datetime, timezone
import logging
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.db.repository import get_repository
from app.db.models import AgentNode, NodeType, Relationship, RelationshipType
from app.api.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse,
    ProcessTaskRequest, ProcessTaskResponse, AgentStatsResponse
)

logger = logging.getLogger(__name__)
T = TypeVar('T')

class AgentService:
    """Service for managing agents and their operations."""
    
    def __init__(self, repo=None):
        """Initialize with an optional repository instance."""
        self.repo = repo or get_repository()
    
    async def create_agent(self, agent_data: AgentCreate) -> AgentResponse:
        """Create a new agent."""
        try:
            # Create the agent node
            agent_node = AgentNode(
                name=agent_data.name,
                description=agent_data.description,
                config={
                    "agent_type": agent_data.agent_type,
                    "is_active": agent_data.is_active,
                    "tags": agent_data.tags,
                    "metadata": agent_data.metadata,
                },
                tools=[tool.dict() for tool in agent_data.tools],
                llm_config=agent_data.llm_config.dict(),
            )
            
            # Save to database
            created_agent = await self.repo.create_node(agent_node)
            
            # Convert to response model
            return self._to_agent_response(created_agent)
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create agent: {str(e)}"
            )
    
    async def get_agent(self, agent_id: str) -> AgentResponse:
        """Get an agent by ID."""
        try:
            agent = await self.repo.get_node(agent_id, AgentNode)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent with ID {agent_id} not found"
                )
            return self._to_agent_response(agent)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get agent: {str(e)}"
            )
    
    async def list_agents(
        self,
        page: int = 1,
        size: int = 10,
        agent_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> AgentListResponse:
        """List agents with pagination and filtering."""
        try:
            skip = (page - 1) * size
            
            # Build filters
            filters = {}
            if agent_type:
                filters["config.agent_type"] = agent_type
            if is_active is not None:
                filters["config.is_active"] = is_active
            if tags:
                # This is a simplified filter - in a real app, you'd want to use array operations
                filters["config.tags"] = tags[0]  # Just use the first tag for now
            
            # Get paginated results
            nodes = await self.repo.find_nodes(
                AgentNode,
                filters=filters,
                skip=skip,
                limit=size
            )
            
            # Get total count for pagination
            total = len(await self.repo.find_nodes(AgentNode, filters=filters))
            
            # Convert to response models
            items = [self._to_agent_response(node) for node in nodes]
            
            return AgentListResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                has_more=(skip + len(items)) < total
            )
            
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list agents: {str(e)}"
            )
    
    async def update_agent(self, agent_id: str, agent_data: AgentUpdate) -> AgentResponse:
        """Update an existing agent."""
        try:
            # Get existing agent
            existing = await self.repo.get_node(agent_id, AgentNode)
            if not existing:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent with ID {agent_id} not found"
                )
            
            # Update fields if provided
            update_data = agent_data.dict(exclude_unset=True)
            
            # Handle config updates
            config = existing.properties.get("config", {})
            if "name" in update_data:
                existing.name = update_data["name"]
            if "description" in update_data:
                existing.description = update_data["description"]
            if "agent_type" in update_data:
                config["agent_type"] = update_data["agent_type"]
            if "is_active" in update_data:
                config["is_active"] = update_data["is_active"]
            if "metadata" in update_data:
                config["metadata"] = update_data["metadata"]
            if "tags" in update_data:
                config["tags"] = update_data["tags"]
            
            # Handle tools and llm_config updates
            if "tools" in update_data:
                existing.tools = [tool.dict() for tool in update_data["tools"]]
            if "llm_config" in update_data:
                existing.llm_config = update_data["llm_config"].dict()
            
            # Update the config
            existing.properties["config"] = config
            
            # Save updates
            updated = await self.repo.update_node(existing)
            
            return self._to_agent_response(updated)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update agent: {str(e)}"
            )
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent by ID."""
        try:
            deleted = await self.repo.delete_node(agent_id, AgentNode)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent with ID {agent_id} not found"
                )
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete agent: {str(e)}"
            )
    
    async def process_task(
        self,
        agent_id: str,
        task_data: ProcessTaskRequest
    ) -> ProcessTaskResponse:
        """Process a task with the specified agent."""
        try:
            # Get the agent
            agent = await self.get_agent(agent_id)
            
            # In a real implementation, this would use the agent's tools and LLM
            # to process the task. For now, we'll just return a mock response.
            
            # TODO: Implement actual task processing with the agent
            task_id = str(uuid4())
            
            return ProcessTaskResponse(
                task_id=task_id,
                status="completed",
                result={
                    "output": f"Processed task with agent {agent_id}: {task_data.task}",
                    "context": task_data.context
                },
                metadata={
                    "agent_id": agent_id,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "model": agent.llm_config.get("model", "unknown")
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to process task with agent {agent_id}: {e}")
            return ProcessTaskResponse(
                task_id=str(uuid4()),
                status="failed",
                error=f"Failed to process task: {str(e)}",
                metadata={
                    "agent_id": agent_id,
                    "error_type": type(e).__name__
                }
            )
    
    async def get_agent_stats(self, agent_id: str) -> AgentStatsResponse:
        """Get statistics for an agent."""
        try:
            # Verify agent exists
            await self.get_agent(agent_id)
            
            # In a real implementation, this would calculate actual statistics
            # from task execution history. For now, return mock data.
            
            return AgentStatsResponse(
                agent_id=agent_id,
                tasks_processed=42,  # Mock value
                avg_processing_time=1.23,  # Mock value (seconds)
                success_rate=0.95,  # Mock value (95% success rate)
                last_active=datetime.now(timezone.utc),
                metadata={
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get stats for agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get agent stats: {str(e)}"
            )
    
    def _to_agent_response(self, node: AgentNode) -> AgentResponse:
        """Convert an AgentNode to an AgentResponse."""
        config = node.properties.get("config", {})
        return AgentResponse(
            id=node.id,
            name=node.name,
            description=node.description,
            agent_type=config.get("agent_type", "general"),
            is_active=config.get("is_active", True),
            metadata=config.get("metadata", {}),
            tags=config.get("tags", []),
            tools=node.tools,
            llm_config=node.llm_config,
            created_at=node.created_at,
            updated_at=node.updated_at
        )

# Singleton instance
_agent_service = None

def get_agent_service() -> AgentService:
    """Get a singleton instance of the agent service."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
