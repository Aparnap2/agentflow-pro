from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from loguru import logger

from ..services.ai.orchestrator import AIOrchestrator

router = APIRouter()

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get overview metrics for the admin dashboard
    """
    try:
        # Mock data - replace with actual implementation
        return {
            "status": "operational",
            "uptime": "99.98%",
            "metrics": {
                "total_agents": 5,
                "active_agents": 3,
                "total_tasks": 1245,
                "tasks_today": 87,
                "success_rate": 94.5,
                "avg_response_time": 1.2,
                "active_sessions": 24,
                "cpu_usage": 42.5,
                "memory_usage": 65.8,
            },
            "recent_activities": [
                {
                    "id": f"act_{i}",
                    "type": random.choice(["task_completed", "agent_started", "error_occurred"]),
                    "message": f"Sample activity {i}",
                    "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                    "severity": random.choice(["info", "warning", "error"])
                } for i in range(5, 0, -1)
            ]
        }
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard overview: {str(e)}"
        )

@router.get("/system-metrics")
async def get_system_metrics(
    time_range: str = "1h",
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get system metrics (CPU, memory, disk, network)
    
    Args:
        time_range: Time range for metrics (e.g., 1h, 24h, 7d)
    """
    try:
        # Mock data - replace with actual implementation
        points = 60  # Default to 60 data points
        if time_range.endswith('h'):
            points = int(time_range[:-1]) * 60
        elif time_range.endswith('d'):
            points = int(time_range[:-1]) * 24 * 60 // 10  # Sample every 10 minutes for longer ranges
            
        now = datetime.utcnow()
        timestamps = [(now - timedelta(minutes=i)).isoformat() for i in range(points, 0, -1)]
        
        def generate_metric(base: float, variation: float) -> List[float]:
            return [max(0, min(100, base + random.uniform(-variation, variation))) 
                   for _ in range(points)]
        
        return {
            "time_range": time_range,
            "timestamps": timestamps,
            "cpu": {
                "usage": generate_metric(40, 30),
                "cores": 8,
                "load_avg": [random.uniform(0.5, 2.0) for _ in range(3)]
            },
            "memory": {
                "total_gb": 32,
                "used_gb": generate_metric(16, 8),
                "cached_gb": generate_metric(4, 2),
                "swap_used_gb": generate_metric(2, 1)
            },
            "disk": {
                "total_gb": 500,
                "used_gb": generate_metric(200, 50),
                "read_mb": [max(0, random.normal(50, 20)) for _ in range(points)],
                "write_mb": [max(0, random.normal(30, 15)) for _ in range(points)]
            },
            "network": {
                "bytes_sent": [random.randint(1000, 10000) for _ in range(points)],
                "bytes_recv": [random.randint(1000, 15000) for _ in range(points)],
                "connections": random.randint(50, 200)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )

@router.get("/activity-logs")
async def get_activity_logs(
    limit: int = 50,
    offset: int = 0,
    severity: Optional[str] = None,
    orchestrator: AIOrchestrator = Depends()
) -> Dict[str, Any]:
    """
    Get system activity logs
    
    Args:
        limit: Number of logs to return
        offset: Pagination offset
        severity: Filter by severity (info, warning, error)
    """
    try:
        # Mock data - replace with actual implementation
        severities = ["info", "warning", "error"]
        log_types = ["system", "auth", "api", "task", "agent"]
        
        logs = [
            {
                "id": f"log_{i}",
                "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 1000))).isoformat(),
                "type": random.choice(log_types),
                "severity": random.choice(severities),
                "message": f"This is a sample {severity if severity else 'log'} message #{i}",
                "source": f"service-{random.randint(1, 5)}",
                "metadata": {
                    "user_id": f"user_{random.randint(1, 10)}",
                    "ip": f"192.168.1.{random.randint(1, 255)}",
                    "duration_ms": random.randint(10, 5000)
                }
            }
            for i in range(1, limit + 1)
        ]
        
        # Apply severity filter if provided
        if severity:
            logs = [log for log in logs if log["severity"] == severity]
        
        # Sort by timestamp descending
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        total = len(logs)
        paginated_logs = logs[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": paginated_logs
        }
        
    except Exception as e:
        logger.error(f"Error getting activity logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity logs: {str(e)}"
        )
