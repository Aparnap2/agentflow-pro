from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class HILStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TIMEOUT = "timeout"

class HILRequest(BaseModel):
    """Human-in-the-loop request model"""
    id: str
    workflow_id: str
    thread_id: str
    agent_id: str
    request_type: str  # approval, input, review, etc.
    title: str
    description: str
    context: Dict[str, Any]
    proposed_action: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, Any]]] = None
    priority: str = "medium"  # low, medium, high, urgent
    timeout_minutes: Optional[int] = None
    created_at: str
    status: HILStatus = HILStatus.PENDING

class HILResponse(BaseModel):
    """Human response to HIL request"""
    request_id: str
    status: HILStatus
    response_data: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None
    responded_by: str
    responded_at: str

class HumanInLoopService:
    def __init__(self, redis_service=None, notification_service=None):
        self.redis_service = redis_service
        self.notification_service = notification_service
        self.pending_requests: Dict[str, HILRequest] = {}
        self.completed_requests: Dict[str, HILResponse] = {}
        self.workflow_hil_map: Dict[str, List[str]] = {}  # workflow_id -> list of HIL request IDs

    async def create_hil_request(
        self,
        workflow_id: str,
        thread_id: str,
        agent_id: str,
        request_type: str,
        title: str,
        description: str,
        context: Dict[str, Any],
        proposed_action: Optional[Dict[str, Any]] = None,
        options: Optional[List[Dict[str, Any]]] = None,
        priority: str = "medium",
        timeout_minutes: Optional[int] = None
    ) -> str:
        """Create a new human-in-the-loop request"""
        try:
            request_id = str(uuid.uuid4())
            
            hil_request = HILRequest(
                id=request_id,
                workflow_id=workflow_id,
                thread_id=thread_id,
                agent_id=agent_id,
                request_type=request_type,
                title=title,
                description=description,
                context=context,
                proposed_action=proposed_action,
                options=options,
                priority=priority,
                timeout_minutes=timeout_minutes,
                created_at=datetime.now().isoformat()
            )
            
            # Store the request
            self.pending_requests[request_id] = hil_request
            
            # Map to workflow
            if workflow_id not in self.workflow_hil_map:
                self.workflow_hil_map[workflow_id] = []
            self.workflow_hil_map[workflow_id].append(request_id)
            
            # Store in Redis if available for persistence
            if self.redis_service:
                await self.redis_service.set(
                    f"hil_request:{request_id}",
                    hil_request.json(),
                    expire=timeout_minutes * 60 if timeout_minutes else 3600  # 1 hour default
                )
            
            # Send notification if service available
            if self.notification_service:
                await self.notification_service.send_hil_notification(hil_request)
            
            logger.info(f"Created HIL request {request_id} for workflow {workflow_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to create HIL request: {e}")
            raise

    async def respond_to_hil_request(
        self,
        request_id: str,
        status: HILStatus,
        response_data: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None,
        responded_by: str = "human"
    ) -> Dict[str, Any]:
        """Respond to a human-in-the-loop request"""
        try:
            if request_id not in self.pending_requests:
                return {'error': f'HIL request {request_id} not found'}
            
            hil_request = self.pending_requests[request_id]
            
            # Create response
            response = HILResponse(
                request_id=request_id,
                status=status,
                response_data=response_data,
                comments=comments,
                responded_by=responded_by,
                responded_at=datetime.now().isoformat()
            )
            
            # Move from pending to completed
            del self.pending_requests[request_id]
            self.completed_requests[request_id] = response
            
            # Update workflow HIL map
            if hil_request.workflow_id in self.workflow_hil_map:
                if request_id in self.workflow_hil_map[hil_request.workflow_id]:
                    self.workflow_hil_map[hil_request.workflow_id].remove(request_id)
            
            # Store response in Redis if available
            if self.redis_service:
                await self.redis_service.set(
                    f"hil_response:{request_id}",
                    response.json(),
                    expire=86400  # 24 hours
                )
                # Remove the request from Redis
                await self.redis_service.delete(f"hil_request:{request_id}")
            
            logger.info(f"HIL request {request_id} responded with status: {status}")
            return {
                'status': 'success',
                'request_id': request_id,
                'response': response.dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to respond to HIL request {request_id}: {e}")
            return {'error': str(e)}

    async def get_hil_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific HIL request"""
        try:
            # Check pending requests first
            if request_id in self.pending_requests:
                return self.pending_requests[request_id].dict()
            
            # Check completed requests
            if request_id in self.completed_requests:
                response = self.completed_requests[request_id]
                # Get original request from Redis if available
                if self.redis_service:
                    request_data = await self.redis_service.get(f"hil_request:{request_id}")
                    if request_data:
                        return {
                            'request': HILRequest.parse_raw(request_data).dict(),
                            'response': response.dict()
                        }
                return {'response': response.dict()}
            
            # Try Redis if available
            if self.redis_service:
                request_data = await self.redis_service.get(f"hil_request:{request_id}")
                if request_data:
                    return HILRequest.parse_raw(request_data).dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get HIL request {request_id}: {e}")
            return None

    async def list_pending_requests(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all pending HIL requests, optionally filtered by workflow"""
        try:
            requests = []
            
            if workflow_id:
                # Filter by workflow
                request_ids = self.workflow_hil_map.get(workflow_id, [])
                for request_id in request_ids:
                    if request_id in self.pending_requests:
                        requests.append(self.pending_requests[request_id].dict())
            else:
                # Return all pending requests
                requests = [req.dict() for req in self.pending_requests.values()]
            
            # Sort by priority and creation time
            priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
            requests.sort(key=lambda x: (priority_order.get(x['priority'], 2), x['created_at']))
            
            return requests
            
        except Exception as e:
            logger.error(f"Failed to list pending HIL requests: {e}")
            return []

    async def pause_workflow(self, workflow_id: str, reason: str = "Awaiting human input") -> Dict[str, Any]:
        """Pause a workflow for human input"""
        try:
            # This integrates with the workflow orchestrator
            pause_info = {
                'workflow_id': workflow_id,
                'status': 'paused',
                'reason': reason,
                'paused_at': datetime.now().isoformat()
            }
            
            # Store pause info in Redis if available
            if self.redis_service:
                await self.redis_service.set(
                    f"workflow_pause:{workflow_id}",
                    str(pause_info),
                    expire=3600  # 1 hour
                )
            
            logger.info(f"Workflow {workflow_id} paused: {reason}")
            return pause_info
            
        except Exception as e:
            logger.error(f"Failed to pause workflow {workflow_id}: {e}")
            return {'error': str(e)}

    async def resume_workflow(self, workflow_id: str, human_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resume a paused workflow"""
        try:
            resume_info = {
                'workflow_id': workflow_id,
                'status': 'resumed',
                'resumed_at': datetime.now().isoformat(),
                'human_input': human_input
            }
            
            # Remove pause info from Redis if available
            if self.redis_service:
                await self.redis_service.delete(f"workflow_pause:{workflow_id}")
            
            logger.info(f"Workflow {workflow_id} resumed")
            return resume_info
            
        except Exception as e:
            logger.error(f"Failed to resume workflow {workflow_id}: {e}")
            return {'error': str(e)}

    async def get_workflow_hil_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get HIL status for a workflow"""
        try:
            pending_requests = await self.list_pending_requests(workflow_id)
            
            # Check if workflow is paused
            paused = False
            pause_info = None
            if self.redis_service:
                pause_data = await self.redis_service.get(f"workflow_pause:{workflow_id}")
                if pause_data:
                    paused = True
                    pause_info = eval(pause_data)  # Convert string back to dict
            
            return {
                'workflow_id': workflow_id,
                'paused': paused,
                'pause_info': pause_info,
                'pending_requests_count': len(pending_requests),
                'pending_requests': pending_requests
            }
            
        except Exception as e:
            logger.error(f"Failed to get HIL status for workflow {workflow_id}: {e}")
            return {'error': str(e)}

    async def timeout_expired_requests(self):
        """Handle timeout for expired HIL requests"""
        try:
            current_time = datetime.now()
            expired_requests = []
            
            for request_id, request in self.pending_requests.items():
                if request.timeout_minutes:
                    created_time = datetime.fromisoformat(request.created_at)
                    elapsed_minutes = (current_time - created_time).total_seconds() / 60
                    
                    if elapsed_minutes > request.timeout_minutes:
                        expired_requests.append(request_id)
            
            # Handle expired requests
            for request_id in expired_requests:
                await self.respond_to_hil_request(
                    request_id,
                    HILStatus.TIMEOUT,
                    comments="Request timed out",
                    responded_by="system"
                )
            
            if expired_requests:
                logger.info(f"Handled {len(expired_requests)} expired HIL requests")
            
        except Exception as e:
            logger.error(f"Failed to handle expired HIL requests: {e}")

    def get_status(self, workflow_id: str) -> Dict:
        """Legacy method for backward compatibility"""
        # This is a simplified version for backward compatibility
        pending_count = len(self.workflow_hil_map.get(workflow_id, []))
        return {
            'workflow_id': workflow_id,
            'pending_requests': pending_count,
            'status': 'paused' if pending_count > 0 else 'running'
        }