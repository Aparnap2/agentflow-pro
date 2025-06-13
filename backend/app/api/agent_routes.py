from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from loguru import logger

from ..services.ai.orchestrator import AIOrchestrator

router = APIRouter()

@router.get("/agents")
async def list_agents(
    status: Optional[str] = None,
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    List all available agents with their status and metrics
    
    Args:
        status: Filter agents by status (active, inactive, error)
    """
    try:
        # Mock data - replace with actual implementation
        statuses = ["active", "inactive", "error", "starting", "stopping"]
        agent_types = ["support", "sales", "developer", "analyst", "researcher"]
        
        agents = [
            {
                "id": f"agent_{i}",
                "name": f"{agent_type.capitalize()} Agent {i}",
                "type": agent_type,
                "status": random.choice(statuses),
                "last_active": (datetime.utcnow() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
                "metrics": {
                    "tasks_completed": random.randint(10, 1000),
                    "success_rate": round(random.uniform(80.0, 99.9), 1),
                    "avg_response_time": round(random.uniform(0.5, 5.0), 2),
                    "cpu_usage": round(random.uniform(5.0, 95.0), 1),
                    "memory_usage": round(random.uniform(100, 500), 1),
                },
                "capabilities": [
                    f"{cap}" for cap in random.sample(
                        ["web_search", "data_analysis", "code_generation", 
                         "document_processing", "api_integration", "nlp"], 
                        k=random.randint(1, 4)
                    )
                ]
            }
            for i, agent_type in enumerate(random.choices(agent_types, k=8), 1)
        ]
        
        # Apply status filter if provided
        if status:
            agents = [agent for agent in agents if agent["status"] == status.lower()]
        
        return {
            "total": len(agents),
            "agents": agents
        }
        
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )

@router.get("/agents/{agent_id}")
async def get_agent_details(
    agent_id: str,
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get detailed information about a specific agent
    """
    try:
        # Mock data - replace with actual implementation
        agent_types = ["support", "sales", "developer", "analyst", "researcher"]
        agent_type = random.choice(agent_types)
        statuses = ["active", "inactive", "error", "starting", "stopping"]
        
        # Generate time series data for metrics
        days = 7
        dates = [(datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range(days, 0, -1)]
        
        def generate_metric(base: float, variation: float) -> List[float]:
            return [max(0, base + random.uniform(-variation, variation)) 
                   for _ in range(days)]
        
        return {
            "id": agent_id,
            "name": f"{agent_type.capitalize()} Agent {agent_id.split('_')[-1]}",
            "type": agent_type,
            "status": random.choice(statuses),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "last_active": (datetime.utcnow() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
            "configuration": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 30,
                "retry_attempts": 3
            },
            "metrics": {
                "time_series": {
                    "dates": dates,
                    "tasks_completed": [random.randint(5, 50) for _ in range(days)],
                    "success_rate": generate_metric(90.0, 5.0),
                    "avg_response_time": generate_metric(2.0, 1.5)
                },
                "total_tasks": random.randint(100, 5000),
                "success_rate": round(random.uniform(80.0, 99.9), 1),
                "avg_response_time": round(random.uniform(0.5, 5.0), 2),
                "error_rate": round(random.uniform(0.1, 5.0), 1),
                "cpu_usage": round(random.uniform(5.0, 95.0), 1),
                "memory_usage": round(random.uniform(100, 500), 1),
            },
            "capabilities": [
                "web_search", "data_analysis", "code_generation", "document_processing"
            ][:random.randint(2, 4)],
            "recent_activities": [
                {
                    "id": f"act_{i}",
                    "type": random.choice(["task_completed", "error", "warning", "info"]),
                    "message": f"Sample activity {i} for agent {agent_id}",
                    "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                    "details": {"key": f"value_{i}"}
                } for i in range(5, 0, -1)
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting agent details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent details: {str(e)}"
        )

@router.post("/agents/{agent_id}/control")
async def control_agent(
    agent_id: str,
    action: str = Query(..., regex="^(start|stop|restart|pause|resume)$"),
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Control an agent's state
    
    Args:
        agent_id: ID of the agent to control
        action: Action to perform (start, stop, restart, pause, resume)
    """
    try:
        # Mock implementation - replace with actual control logic
        logger.info(f"Received {action} command for agent {agent_id}")
        
        # Simulate some processing time
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "message": f"Agent {agent_id} {action} command received",
            "agent_id": agent_id,
            "status": action + "ing" if not action.endswith('e') else action + "ing",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error controlling agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to control agent: {str(e)}"
        )

@router.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(
    agent_id: str,
    time_range: str = "1h",
    metrics: str = "all",
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get detailed metrics for a specific agent
    
    Args:
        agent_id: ID of the agent
        time_range: Time range for metrics (e.g., 1h, 24h, 7d)
        metrics: Comma-separated list of metrics to return (or 'all')
    """
    try:
        # Parse time range
        if time_range.endswith('h'):
            points = int(time_range[:-1]) * 12  # 5-minute intervals
        elif time_range.endswith('d'):
            points = int(time_range[:-1]) * 24 * 12  # 5-minute intervals
        else:
            points = 12  # Default to 1 hour at 5-minute intervals
        
        # Generate timestamps
        now = datetime.utcnow()
        interval_minutes = 5  # 5-minute intervals
        timestamps = [(now - timedelta(minutes=i*interval_minutes)).isoformat() 
                     for i in range(points, 0, -1)]
        
        # Generate mock metrics
        def generate_metric(base: float, variation: float) -> List[float]:
            return [max(0, base + random.uniform(-variation, variation)) 
                   for _ in range(points)]
        
        # Available metrics
        all_metrics = {
            "cpu_usage": generate_metric(40, 30),
            "memory_usage_mb": generate_metric(200, 150),
            "response_time_ms": generate_metric(500, 300),
            "requests_per_minute": [random.randint(5, 50) for _ in range(points)],
            "error_rate": generate_metric(2, 1.5),
            "token_usage": [random.randint(1000, 5000) for _ in range(points)]
        }
        
        # Filter metrics if needed
        if metrics.lower() != 'all':
            requested_metrics = metrics.split(',')
            all_metrics = {k: v for k, v in all_metrics.items() 
                         if k in requested_metrics}
        
        return {
            "agent_id": agent_id,
            "time_range": time_range,
            "timestamps": timestamps,
            "metrics": all_metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting agent metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent metrics: {str(e)}"
        )
