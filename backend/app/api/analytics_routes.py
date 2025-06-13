from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
from loguru import logger

from ..services.ai.orchestrator import AIOrchestrator

router = APIRouter()

@router.get("/analytics")
async def get_analytics(
    period: str = "7d",
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get analytics data for the dashboard
    
    Args:
        period: Time period for analytics (e.g., 7d, 30d, 90d)
        
    Returns:
        Dict containing analytics data
    """
    try:
        # Generate mock data for now - replace with actual implementation
        days = int(period[:-1]) if period.endswith('d') else 7
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days-1)
        
        # Generate time series data
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range(days)]
        
        # Mock data generation
        def generate_series(base: int, variance: int = 5) -> List[int]:
            return [max(0, base + random.randint(-variance, variance)) for _ in range(days)]
        
        return {
            "period": period,
            "time_series": {
                "dates": dates,
                "active_users": generate_series(100, 20),
                "tasks_completed": generate_series(500, 50),
                "messages_processed": generate_series(2000, 200),
            },
            "summary": {
                "total_users": 1245,
                "active_users": 342,
                "tasks_completed": 3567,
                "success_rate": 92.5,
                "avg_response_time": 1.2,
            },
            "agent_performance": [
                {"name": "Support Agent", "tasks": 1245, "success_rate": 94.2},
                {"name": "Sales Agent", "tasks": 987, "success_rate": 89.5},
                {"name": "Dev Agent", "tasks": 756, "success_rate": 91.8},
            ],
            "task_distribution": {
                "labels": ["Support", "Sales", "Development", "Other"],
                "data": [45, 30, 20, 5]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics data: {str(e)}"
        )

@router.get("/agent-performance")
async def get_agent_performance(
    agent_id: Optional[str] = None,
    time_range: str = "7d",
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get performance metrics for agents
    
    Args:
        agent_id: Optional agent ID to get specific agent metrics
        time_range: Time range for metrics (e.g., 7d, 30d)
        
    Returns:
        Dict containing agent performance data
    """
    try:
        # Mock data - replace with actual implementation
        days = int(time_range[:-1]) if time_range.endswith('d') else 7
        
        if agent_id:
            # Return specific agent metrics
            return {
                "agent_id": agent_id,
                "name": f"Agent {agent_id[:6]}",
                "role": "Support",
                "tasks_completed": random.randint(50, 200),
                "success_rate": round(random.uniform(85.0, 99.9), 1),
                "avg_response_time": round(random.uniform(0.5, 5.0), 2),
                "time_range": time_range,
                "metrics": {
                    "dates": [(datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d') 
                             for i in range(days, 0, -1)],
                    "tasks": [random.randint(5, 20) for _ in range(days)],
                    "success_rates": [round(random.uniform(80.0, 100.0), 1) for _ in range(days)],
                }
            }
        else:
            # Return list of agents with summary metrics
            return {
                "time_range": time_range,
                "agents": [
                    {
                        "id": f"agent_{i}",
                        "name": f"Agent {i}",
                        "role": role,
                        "tasks_completed": random.randint(50, 200),
                        "success_rate": round(random.uniform(85.0, 99.9), 1),
                        "avg_response_time": round(random.uniform(0.5, 5.0), 2),
                    }
                    for i, role in enumerate(["Support", "Sales", "Developer", "Analyst"], 1)
                ]
            }
            
    except Exception as e:
        logger.error(f"Error getting agent performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent performance: {str(e)}"
        )
