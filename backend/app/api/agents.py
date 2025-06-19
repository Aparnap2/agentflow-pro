from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
import json
import asyncio

from ..models import agent, auth
from ..services.auth_service import AuthService
from ..db.database import DatabaseService

router = APIRouter()
security = HTTPBearer()

def get_db() -> DatabaseService:
    return DatabaseService()

def get_auth_service() -> AuthService:
    return AuthService()

@router.get("/", response_model=List[agent.AgentConfig])
async def list_agents(
    role: Optional[agent.AgentRole] = None,
    department: Optional[agent.Department] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """List available agents with optional filtering"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # In a real implementation, fetch agents from database with filters
        # This is a simplified example
        query = "SELECT * FROM agents WHERE is_active = true"
        params = []
        
        if role:
            query += " AND role = $1"
            params.append(role.value)
            
        if department:
            query += f" AND {' AND '.join([f'department = ${i+2}' for i, d in enumerate([department])])}"
            params.extend([d.value for d in [department]])
            
        agents = await db.fetch(query, *params)
        return [dict(agent) for agent in agents]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agents: {str(e)}"
        )

@router.get("/{agent_id}", response_model=agent.AgentConfig)
async def get_agent(
    agent_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """Get agent by ID"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Get agent from database
        agent_data = await db.fetchrow(
            "SELECT * FROM agents WHERE agent_id = $1 AND is_active = true",
            agent_id
        )
        
        if not agent_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
            
        return dict(agent_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent: {str(e)}"
        )

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: str,
    token: str
):
    """WebSocket endpoint for agent communication"""
    try:
        # Authenticate user
        auth_service = AuthService()
        try:
            user = await auth_service.verify_token(token)
        except Exception as e:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        await websocket.accept()
        
        # In a real implementation, you would register this connection
        # with a connection manager and handle bi-directional communication
        
        try:
            while True:
                data = await websocket.receive_text()
                # Process incoming message
                message = json.loads(data)
                
                # Echo back for now
                await websocket.send_json({
                    "type": "response",
                    "content": f"Received: {message}"
                })
                
        except WebSocketDisconnect:
            # Handle disconnection
            pass
            
    except Exception as e:
        # Log the error
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.close()
        except:
            pass

@router.post("/{agent_id}/invoke", response_model=Dict[str, Any])
async def invoke_agent(
    agent_id: str,
    input_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: DatabaseService = Depends(get_db)
):
    """Invoke an agent with input data"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Get agent configuration
        agent_config = await db.fetchrow(
            "SELECT * FROM agents WHERE agent_id = $1 AND is_active = true",
            agent_id
        )
        
        if not agent_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # In a real implementation, you would invoke the agent's logic here
        # This is a simplified example
        response = {
            "agent_id": agent_id,
            "status": "success",
            "result": f"Processed input: {input_data}",
            "metadata": {
                "agent_name": agent_config.get('name', 'Unknown'),
                "role": agent_config.get('role'),
                "timestamp": str(datetime.utcnow())
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error invoking agent: {str(e)}"
        )
