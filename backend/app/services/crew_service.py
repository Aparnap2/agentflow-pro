"""Service layer for crew-related operations."""
from typing import Dict, List, Optional, Any, Type, TypeVar, Union
from datetime import datetime, timezone
import logging
from uuid import uuid4, UUID

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.db.repository import get_repository
from app.db.models import CrewNode, AgentNode, WorkflowNode, Relationship, RelationshipType
from app.api.schemas.crew import (
    CrewCreate, CrewUpdate, CrewResponse, CrewListResponse,
    CrewExecutionRequest, CrewExecutionResponse, CrewStatsResponse,
    CrewMember, CrewMemberRole
)

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=CrewNode)

class CrewService:
    """Service for managing crews and their operations."""
    
    def __init__(self, repo=None):
        """Initialize with an optional repository instance."""
        self.repo = repo or get_repository()
    
    async def create_crew(self, crew_data: CrewCreate, created_by: str) -> CrewResponse:
        """Create a new crew."""
        try:
            # Create the crew node
            crew_node = CrewNode(
                name=crew_data.name,
                description=crew_data.description,
                members=[member.dict() for member in crew_data.members],
                config=crew_data.config,
                metadata={
                    **crew_data.metadata,
                    "created_by": created_by,
                    "status": "active" if crew_data.is_active else "inactive"
                }
            )
            
            # Save to database
            created_crew = await self.repo.create_node(crew_node)
            
            # Create relationships with workflow if specified
            if crew_data.workflow_id:
                await self._link_workflow(created_crew.id, crew_data.workflow_id)
            
            # Create relationships with members
            for member in crew_data.members:
                await self._add_member(created_crew.id, member.agent_id, member.role, member.permissions)
            
            # Convert to response model
            return self._to_crew_response(created_crew)
            
        except Exception as e:
            logger.error(f"Failed to create crew: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create crew: {str(e)}"
            )
    
    async def get_crew(self, crew_id: str) -> CrewResponse:
        """Get a crew by ID."""
        try:
            crew = await self.repo.get_node(crew_id, CrewNode)
            if not crew:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Crew with ID {crew_id} not found"
                )
            return self._to_crew_response(crew)
        except Exception as e:
            logger.error(f"Failed to get crew: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get crew: {str(e)}"
            )
    
    async def list_crews(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> CrewListResponse:
        """List crews with optional filtering and pagination."""
        try:
            # Build query
            query = """
            MATCH (c:Crew:Node)
            WHERE 1=1
            """
            
            params = {}
            
            # Add filters
            if name:
                query += " AND c.name CONTAINS $name"
                params["name"] = name
                
            if is_active is not None:
                query += " AND c.is_active = $is_active"
                params["is_active"] = is_active
                
            if tags:
                query += " AND any(tag IN $tags WHERE tag IN c.tags)"
                params["tags"] = tags
            
            # Add pagination
            skip = (page - 1) * size
            query += """
            RETURN c
            ORDER BY c.created_at DESC
            SKIP $skip
            LIMIT $limit
            """
            params["skip"] = skip
            params["limit"] = size
            
            # Get total count
            count_query = """
            MATCH (c:Crew:Node)
            RETURN count(c) as total
            """
            
            with self.repo.driver.session() as session:
                # Get total count
                count_result = session.run(count_query)
                total = count_result.single()["total"]
                
                # Get paginated results
                result = session.run(query, **params)
                crews = [self._to_crew_response(CrewNode(**record["c"])) for record in result]
                
                return CrewListResponse(
                    items=crews,
                    total=total,
                    page=page,
                    size=len(crews),
                    has_more=(skip + len(crews)) < total
                )
                
        except Exception as e:
            logger.error(f"Failed to list crews: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list crews: {str(e)}"
            )
    
    async def update_crew(self, crew_id: str, update_data: CrewUpdate) -> CrewResponse:
        """Update an existing crew."""
        try:
            # Get existing crew
            crew = await self.repo.get_node(crew_id, CrewNode)
            if not crew:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Crew with ID {crew_id} not found"
                )
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if field == "metadata" and update_data.metadata is not None:
                    crew.metadata.update(update_data.metadata)
                elif field != "metadata":
                    setattr(crew, field, value)
            
            # Update timestamps
            crew.updated_at = datetime.now(timezone.utc)
            
            # Save updates
            updated_crew = await self.repo.update_node(crew)
            return self._to_crew_response(updated_crew)
            
        except Exception as e:
            logger.error(f"Failed to update crew: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update crew: {str(e)}"
            )
    
    async def delete_crew(self, crew_id: str) -> bool:
        """Delete a crew by ID."""
        try:
            # First, check if the crew exists
            crew = await self.repo.get_node(crew_id, CrewNode)
            if not crew:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Crew with ID {crew_id} not found"
                )
            
            # Delete the crew node and its relationships
            await self.repo.delete_node(crew_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete crew: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete crew: {str(e)}"
            )
    
    async def execute_crew(
        self,
        crew_id: str,
        execution_data: CrewExecutionRequest,
        user_id: str
    ) -> CrewExecutionResponse:
        """Execute a crew with the given input data."""
        try:
            # Get the crew and validate
            crew = await self.repo.get_node(crew_id, CrewNode)
            if not crew:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Crew with ID {crew_id} not found"
                )
            
            # Check if crew is active
            if not crew.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot execute an inactive crew"
                )
            
            # Create execution record
            execution_id = str(uuid4())
            execution_data = {
                "id": execution_id,
                "crew_id": crew_id,
                "status": "pending",
                "input_data": execution_data.input_data,
                "context": execution_data.context,
                "created_by": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {}
            }
            
            # TODO: Implement actual execution logic
            # For now, just return a mock response
            
            return CrewExecutionResponse(
                execution_id=execution_id,
                status="pending",
                metadata={
                    "message": "Crew execution started",
                    "crew_id": crew_id,
                    "user_id": user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to execute crew: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute crew: {str(e)}"
            )
    
    async def get_crew_stats(self, crew_id: str) -> CrewStatsResponse:
        """Get statistics for a crew."""
        try:
            # Get the crew
            crew = await self.repo.get_node(crew_id, CrewNode)
            if not crew:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Crew with ID {crew_id} not found"
                )
            
            # TODO: Implement actual statistics calculation
            # For now, return mock data
            
            return CrewStatsResponse(
                crew_id=crew_id,
                executions_count=0,
                avg_execution_time=0.0,
                success_rate=0.0,
                last_executed=None,
                member_stats={},
                metadata={"message": "Statistics not yet implemented"}
            )
            
        except Exception as e:
            logger.error(f"Failed to get crew stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get crew stats: {str(e)}"
            )
    
    # Helper methods
    async def _link_workflow(self, crew_id: str, workflow_id: str) -> None:
        """Link a workflow to a crew."""
        # Check if workflow exists
        workflow = await self.repo.get_node(workflow_id, WorkflowNode)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow with ID {workflow_id} not found"
            )
        
        # Create relationship
        relationship = Relationship(
            source_id=crew_id,
            target_id=workflow_id,
            type=RelationshipType.USES,
            properties={"created_at": datetime.now(timezone.utc).isoformat()}
        )
        
        await self.repo.create_relationship(relationship)
    
    async def _add_member(
        self,
        crew_id: str,
        agent_id: str,
        role: CrewMemberRole = CrewMemberRole.MEMBER,
        permissions: Optional[List[str]] = None
    ) -> None:
        """Add a member to a crew."""
        # Check if agent exists
        agent = await self.repo.get_node(agent_id, AgentNode)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        # Create relationship
        relationship = Relationship(
            source_id=crew_id,
            target_id=agent_id,
            type=RelationshipType.HAS_MEMBER,
            properties={
                "role": role,
                "permissions": permissions or [],
                "joined_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        await self.repo.create_relationship(relationship)
    
    def _to_crew_response(self, crew_node: CrewNode) -> CrewResponse:
        """Convert a CrewNode to a CrewResponse."""
        return CrewResponse(
            id=crew_node.id,
            name=crew_node.name,
            description=crew_node.description,
            is_active=crew_node.is_active,
            members=crew_node.members,
            workflow_id=crew_node.workflow_id,
            config=crew_node.config,
            tags=crew_node.metadata.get("tags", []),
            metadata=crew_node.metadata,
            created_at=crew_node.created_at,
            updated_at=crew_node.updated_at
        )

# Singleton instance
_crew_service = None

def get_crew_service() -> CrewService:
    """Get a singleton instance of the crew service."""
    global _crew_service
    if _crew_service is None:
        _crew_service = CrewService()
    return _crew_service
