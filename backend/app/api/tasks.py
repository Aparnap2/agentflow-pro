from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional

from ..models import task, auth
from ..services.auth_service import AuthService
from ..services.redis_service import RedisService
from ..db.database import DatabaseService

router = APIRouter()
security = HTTPBearer()

def get_db() -> DatabaseService:
    return DatabaseService()

def get_auth_service() -> AuthService:
    return AuthService()

def get_redis_service() -> RedisService:
    return RedisService()

@router.post("/", response_model=task.TaskResponse)
async def create_task(
    task_request: task.TaskRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """Create a new task"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Create task response
        task_response = task.TaskResponse(
            **task_request.dict(),
            created_by=current_user.user_id,
            status=task.TaskStatus.PENDING
        )
        
        # Save to database
        await db.save_task(task_response)
        
        # In a real implementation, you would start task processing here
        # background_tasks.add_task(process_task, task_id=task_response.id)
        
        return task_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )

@router.get("/{task_id}", response_model=task.TaskResponse)
async def get_task(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """Get task by ID"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Get task from database
        task_data = await db.get_task(task_id)
        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Check permissions (simplified)
        if task_data['created_by'] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this task"
            )
            
        return task_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task: {str(e)}"
        )

@router.get("/", response_model=List[task.TaskResponse])
async def list_tasks(
    status: Optional[task.TaskStatus] = None,
    limit: int = 100,
    offset: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """List tasks with optional filtering"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Build query
        query = "SELECT * FROM tasks WHERE created_by = $1"
        params = [current_user.user_id]
        
        if status:
            query += " AND status = $2"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT $2 OFFSET $3"
        params.extend([limit, offset])
        
        # Execute query
        tasks = await db.fetch(query, *params)
        return [dict(task) for task in tasks]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}"
        )

@router.put("/{task_id}", response_model=task.TaskResponse)
async def update_task(
    task_id: str,
    task_update: task.TaskRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """Update task"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Get existing task
        existing_task = await db.get_task(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
        # Check permissions
        if existing_task['created_by'] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task"
            )
        
        # Update task
        updated_task = {**existing_task, **task_update.dict(exclude_unset=True)}
        updated_task['updated_at'] = datetime.utcnow()
        
        # Save to database
        await db.save_task(updated_task)
        
        return updated_task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}"
        )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """Delete task"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Get existing task
        existing_task = await db.get_task(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
            
        # Check permissions
        if existing_task['created_by'] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )
        
        # Delete task
        await db.execute("DELETE FROM tasks WHERE task_id = $1", task_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        )
