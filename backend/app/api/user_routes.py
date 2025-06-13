from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from uuid import uuid4
from loguru import logger

from ..services.ai.orchestrator import AIOrchestrator

router = APIRouter()

# Mock user database
mock_users = [
    {
        "id": "user_1",
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "status": "active",
        "last_login": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "permissions": ["read", "write", "delete", "admin"]
    },
    {
        "id": "user_2",
        "email": "developer@example.com",
        "name": "Developer One",
        "role": "developer",
        "status": "active",
        "last_login": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "created_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
        "permissions": ["read", "write"]
    },
    {
        "id": "user_3",
        "email": "viewer@example.com",
        "name": "Viewer User",
        "role": "viewer",
        "status": "inactive",
        "last_login": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
        "permissions": ["read"]
    }
]

@router.get("/users", response_model=List[Dict[str, Any]])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
    orchestrator: AIOrchestrator = Depends()
) -> List[Dict[str, Any]]:
    """
    List all users with optional filtering
    """
    try:
        users = mock_users.copy()
        
        # Apply filters
        if status:
            users = [u for u in users if u["status"] == status.lower()]
        if role:
            users = [u for u in users if u["role"] == role.lower()]
        if search:
            search = search.lower()
            users = [u for u in users 
                    if search in u["name"].lower() 
                    or search in u["email"].lower()
                    or search in u["id"].lower()]
        
        # Apply pagination
        return users[skip:skip + limit]
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: str,
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get user by ID
    """
    try:
        user = next((u for u in mock_users if u["id"] == user_id), None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: Dict[str, Any] = Body(...),
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Create a new user
    """
    try:
        # Validate required fields
        required_fields = ["email", "name", "role"]
        for field in required_fields:
            if field not in user_data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required field: {field}"
                )
        
        # Check if user with email already exists
        if any(u["email"] == user_data["email"] for u in mock_users):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = {
            "id": f"user_{len(mock_users) + 1}",
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data["role"],
            "status": user_data.get("status", "active"),
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "permissions": user_data.get("permissions", [])
        }
        
        # In a real app, you would save to database here
        mock_users.append(new_user)
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: Dict[str, Any] = Body(...),
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Update an existing user
    """
    try:
        # Find user
        user_idx = next((i for i, u in enumerate(mock_users) if u["id"] == user_id), None)
        if user_idx is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Update user data
        updated_user = {**mock_users[user_idx], **user_data}
        
        # In a real app, you would update the database here
        mock_users[user_idx] = updated_user
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    orchestrator: AIOrchestrator = Depends()
) -> None:
    """
    Delete a user
    """
    try:
        # Find user
        user_idx = next((i for i, u in enumerate(mock_users) if u["id"] == user_id), None)
        if user_idx is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # In a real app, you would delete from database here
        mock_users.pop(user_idx)
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    days: int = 30,
    limit: int = 50,
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get user activity logs
    """
    try:
        # Check if user exists
        if not any(u["id"] == user_id for u in mock_users):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        
        # Generate mock activity data
        activity_types = ["login", "logout", "api_call", "settings_update", "password_change"]
        
        activities = [
            {
                "id": f"act_{i}",
                "type": random.choice(activity_types),
                "timestamp": (datetime.utcnow() - timedelta(
                    days=random.randint(0, days-1),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )).isoformat(),
                "ip": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(80, 120)}.0.0.0 Safari/537.36",
                "details": {
                    "endpoint": f"/api/{random.choice(['users', 'agents', 'tasks'])}",
                    "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                    "status_code": random.choice([200, 201, 204, 400, 401, 403, 404, 500]),
                    "duration_ms": random.randint(50, 2000)
                }
            }
            for i in range(1, limit + 1)
        ]
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Calculate some statistics
        activity_by_type = {}
        for act in activities:
            activity_by_type[act["type"]] = activity_by_type.get(act["type"], 0) + 1
        
        return {
            "user_id": user_id,
            "total_activities": len(activities),
            "activity_by_type": activity_by_type,
            "activities": activities[:limit]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user activity for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity: {str(e)}"
        )
