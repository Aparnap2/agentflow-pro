"""Service layer for workflow-related operations."""
from typing import Dict, List, Optional, Any, Type, TypeVar, Union
from datetime import datetime, timezone
import logging
from uuid import uuid4, UUID

from fastapi import HTTPException, status
from pydantic import ValidationError

from app.db.repository import get_repository
from app.db.models import WorkflowNode, TaskNode, Relationship, RelationshipType, AgentNode
from app.api.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowListResponse,
    WorkflowExecutionRequest, WorkflowExecutionResponse, WorkflowStatsResponse,
    TaskCreate, TaskResponse, TaskStatus, WorkflowStatus, TaskType
)

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=WorkflowNode)

class WorkflowService:
    """Service for managing workflows and their operations."""
    
    def __init__(self, repo=None):
        """Initialize with an optional repository instance."""
        self.repo = repo or get_repository()
    
    async def create_workflow(self, workflow_data: WorkflowCreate, created_by: str) -> WorkflowResponse:
        """Create a new workflow."""
        try:
            # Create the workflow node
            workflow_node = WorkflowNode(
                name=workflow_data.name,
                description=workflow_data.description,
                status=workflow_data.status.value,
                is_template=workflow_data.is_template,
                metadata={
                    **workflow_data.metadata,
                    "created_by": created_by,
                    "version": 1,
                    "tags": workflow_data.tags
                },
                config=workflow_data.config
            )
            
            # Save to database
            created_workflow = await self.repo.create_node(workflow_node)
            
            # Create tasks if any
            if workflow_data.tasks:
                for task_data in workflow_data.tasks:
                    await self._create_task(created_workflow.id, task_data)
            
            return self._to_workflow_response(created_workflow)
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create workflow: {str(e)}"
            )
    
    async def get_workflow(self, workflow_id: str, include_tasks: bool = True) -> WorkflowResponse:
        """Get a workflow by ID."""
        try:
            workflow = await self.repo.get_node(workflow_id, WorkflowNode)
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with ID {workflow_id} not found"
                )
            
            # Get tasks if requested
            tasks = []
            if include_tasks:
                tasks = await self._get_workflow_tasks(workflow_id)
            
            response = self._to_workflow_response(workflow)
            response.tasks = tasks
            return response
            
        except Exception as e:
            logger.error(f"Failed to get workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get workflow: {str(e)}"
            )
    
    async def list_workflows(
        self,
        page: int = 1,
        size: int = 10,
        name: Optional[str] = None,
        status: Optional[WorkflowStatus] = None,
        is_template: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> WorkflowListResponse:
        """List workflows with optional filtering and pagination."""
        try:
            # Build query
            query = """
            MATCH (w:Workflow:Node)
            WHERE 1=1
            """
            
            params = {}
            
            # Add filters
            if name:
                query += " AND w.name CONTAINS $name"
                params["name"] = name
                
            if status is not None:
                query += " AND w.status = $status"
                params["status"] = status.value
                
            if is_template is not None:
                query += " AND w.is_template = $is_template"
                params["is_template"] = is_template
                
            if tags:
                query += " AND any(tag IN $tags WHERE tag IN w.metadata.tags)"
                params["tags"] = tags
            
            # Add pagination
            skip = (page - 1) * size
            query += """
            RETURN w
            ORDER BY w.created_at DESC
            SKIP $skip
            LIMIT $limit
            """
            params["skip"] = skip
            params["limit"] = size
            
            # Get total count
            count_query = """
            MATCH (w:Workflow:Node)
            RETURN count(w) as total
            """
            
            with self.repo.driver.session() as session:
                # Get total count
                count_result = session.run(count_query)
                total = count_result.single()["total"]
                
                # Get paginated results
                result = session.run(query, **params)
                workflows = [
                    self._to_workflow_response(WorkflowNode(**record["w"])) 
                    for record in result
                ]
                
                return WorkflowListResponse(
                    items=workflows,
                    total=total,
                    page=page,
                    size=len(workflows),
                    has_more=(skip + len(workflows)) < total
                )
                
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list workflows: {str(e)}"
            )
    
    async def update_workflow(
        self, 
        workflow_id: str, 
        update_data: WorkflowUpdate
    ) -> WorkflowResponse:
        """Update an existing workflow."""
        try:
            # Get existing workflow
            workflow = await self.repo.get_node(workflow_id, WorkflowNode)
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with ID {workflow_id} not found"
                )
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if field == "metadata" and update_data.metadata is not None:
                    workflow.metadata.update(update_data.metadata)
                elif field == "status" and value is not None:
                    setattr(workflow, field, value.value)
                elif field != "metadata":
                    setattr(workflow, field, value)
            
            # Update timestamps and version
            workflow.updated_at = datetime.now(timezone.utc)
            if "version" in workflow.metadata:
                workflow.metadata["version"] += 1
            
            # Save updates
            updated_workflow = await self.repo.update_node(workflow)
            return self._to_workflow_response(updated_workflow)
            
        except Exception as e:
            logger.error(f"Failed to update workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update workflow: {str(e)}"
            )
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow by ID."""
        try:
            # First, check if the workflow exists
            workflow = await self.repo.get_node(workflow_id, WorkflowNode)
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with ID {workflow_id} not found"
                )
            
            # Delete the workflow node and its relationships
            await self.repo.delete_node(workflow_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete workflow: {str(e)}"
            )
    
    async def execute_workflow(
        self,
        workflow_id: str,
        execution_data: WorkflowExecutionRequest,
        user_id: str
    ) -> WorkflowExecutionResponse:
        """Execute a workflow with the given input data."""
        try:
            # Get the workflow and validate
            workflow = await self.repo.get_node(workflow_id, WorkflowNode)
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with ID {workflow_id} not found"
                )
            
            # Check if workflow is active
            if workflow.status != WorkflowStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot execute a {workflow.status} workflow"
                )
            
            # Create execution record
            execution_id = str(uuid4())
            execution_data = {
                "id": execution_id,
                "workflow_id": workflow_id,
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
            
            return WorkflowExecutionResponse(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status="pending",
                metadata={
                    "message": "Workflow execution started",
                    "workflow_id": workflow_id,
                    "user_id": user_id
                },
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Failed to execute workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute workflow: {str(e)}"
            )
    
    async def get_workflow_stats(self, workflow_id: str) -> WorkflowStatsResponse:
        """Get statistics for a workflow."""
        try:
            # Get the workflow
            workflow = await self.repo.get_node(workflow_id, WorkflowNode)
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with ID {workflow_id} not found"
                )
            
            # TODO: Implement actual statistics calculation
            # For now, return mock data
            
            return WorkflowStatsResponse(
                workflow_id=workflow_id,
                executions_count=0,
                avg_execution_time=0.0,
                success_rate=0.0,
                avg_tasks_per_execution=0.0,
                most_common_errors=[],
                last_executed=None
            )
            
        except Exception as e:
            logger.error(f"Failed to get workflow stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get workflow stats: {str(e)}"
            )
    
    async def create_task(
        self,
        workflow_id: str,
        task_data: TaskCreate
    ) -> TaskResponse:
        """Create a new task in a workflow."""
        try:
            # Verify workflow exists
            workflow = await self.repo.get_node(workflow_id, WorkflowNode)
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with ID {workflow_id} not found"
                )
            
            # Create the task
            task = await self._create_task(workflow_id, task_data)
            return task
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create task: {str(e)}"
            )
    
    # Helper methods
    async def _create_task(
        self,
        workflow_id: str,
        task_data: TaskCreate
    ) -> TaskResponse:
        """Internal method to create a task."""
        # Create task node
        task_node = TaskNode(
            name=task_data.name,
            description=task_data.description,
            task_type=task_data.config.task_type.value,
            config=task_data.config.dict(),
            input_schema=task_data.config.input_schema,
            output_schema=task_data.config.output_schema,
            is_async=task_data.config.task_type != TaskType.MANUAL,
            retry_policy=task_data.config.metadata.get("retry_policy", {}),
            metadata={
                **task_data.config.metadata,
                "status": TaskStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Save task to database
        created_task = await self.repo.create_node(task_node)
        
        # Create relationship to workflow
        relationship = Relationship(
            source_id=workflow_id,
            target_id=created_task.id,
            type=RelationshipType.HAS_MEMBER,
            properties={
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
        await self.repo.create_relationship(relationship)
        
        # Create task dependencies if any
        if task_data.dependencies:
            for dep in task_data.dependencies:
                dep_rel = Relationship(
                    source_id=created_task.id,
                    target_id=dep.task_id,
                    type=RelationshipType.DEPENDS_ON,
                    properties={
                        "required": dep.required,
                        "condition": dep.condition or {},
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                await self.repo.create_relationship(dep_rel)
        
        return self._to_task_response(created_task)
    
    async def _get_workflow_tasks(self, workflow_id: str) -> List[TaskResponse]:
        """Get all tasks for a workflow."""
        query = """
        MATCH (w:Workflow:Node {id: $workflow_id})<-[:HAS_MEMBER]-(t:Task:Node)
        RETURN t
        ORDER BY t.created_at
        """
        
        with self.repo.driver.session() as session:
            result = session.run(query, workflow_id=workflow_id)
            tasks = [TaskNode(**record["t"]) for record in result]
            
            # Convert to response models
            task_responses = []
            for task in tasks:
                # Get task dependencies
                deps_query = """
                MATCH (t:Task:Node {id: $task_id})-[r:DEPENDS_ON]->(dep:Task:Node)
                RETURN dep.id as dep_id, r.required as required, r.condition as condition
                """
                deps_result = session.run(deps_query, task_id=task.id)
                dependencies = [
                    {"task_id": record["dep_id"], 
                     "required": record.get("required", True),
                     "condition": record.get("condition", {})}
                    for record in deps_result
                ]
                
                # Create response with dependencies
                task_response = self._to_task_response(task)
                task_response.dependencies = dependencies
                task_responses.append(task_response)
            
            return task_responses
    
    def _to_workflow_response(self, workflow_node: WorkflowNode) -> WorkflowResponse:
        """Convert a WorkflowNode to a WorkflowResponse."""
        return WorkflowResponse(
            id=workflow_node.id,
            name=workflow_node.name,
            description=workflow_node.description,
            status=WorkflowStatus(workflow_node.status),
            is_template=workflow_node.is_template,
            tags=workflow_node.metadata.get("tags", []),
            metadata=workflow_node.metadata,
            config=workflow_node.config,
            created_by=workflow_node.metadata.get("created_by", "system"),
            version=workflow_node.metadata.get("version", 1),
            created_at=workflow_node.created_at,
            updated_at=workflow_node.updated_at,
            tasks=[]  # Will be populated separately
        )
    
    def _to_task_response(self, task_node: TaskNode) -> TaskResponse:
        """Convert a TaskNode to a TaskResponse."""
        return TaskResponse(
            id=task_node.id,
            name=task_node.name,
            description=task_node.description,
            config=TaskConfig(**task_node.config),
            status=TaskStatus(task_node.metadata.get("status", "pending")),
            workflow_id="",  # Will be set by the caller
            created_at=datetime.fromisoformat(task_node.metadata.get("created_at")),
            updated_at=datetime.fromisoformat(task_node.metadata.get("updated_at", task_node.metadata.get("created_at"))),
            started_at=datetime.fromisoformat(task_node.metadata["started_at"]) if "started_at" in task_node.metadata else None,
            completed_at=datetime.fromisoformat(task_node.metadata["completed_at"]) if "completed_at" in task_node.metadata else None,
            dependencies=[]  # Will be set by the caller
        )

# Singleton instance
_workflow_service = None

def get_workflow_service() -> WorkflowService:
    """Get a singleton instance of the workflow service."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service
