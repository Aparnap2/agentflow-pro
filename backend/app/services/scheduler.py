from typing import Dict, List, Any, Optional, Callable
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
from croniter import croniter
import json

logger = logging.getLogger(__name__)

class TriggerType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"
    WEBHOOK = "webhook"
    EVENT = "event"
    MANUAL = "manual"

class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"

class Schedule(BaseModel):
    """Schedule definition model"""
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]  # cron expression, interval, webhook config, etc.
    workflow_id: str
    workflow_input: Dict[str, Any] = {}
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    max_executions: Optional[int] = None
    execution_count: int = 0
    last_execution: Optional[str] = None
    next_execution: Optional[str] = None
    created_at: str
    updated_at: str
    created_by: str

class ScheduleExecution(BaseModel):
    """Schedule execution record"""
    execution_id: str
    schedule_id: str
    workflow_id: str
    trigger_type: TriggerType
    triggered_at: str
    workflow_thread_id: Optional[str] = None
    status: str  # triggered, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None

class SchedulerService:
    def __init__(self, workflow_orchestrator=None, redis_service=None):
        self.workflow_orchestrator = workflow_orchestrator
        self.redis_service = redis_service
        self.schedules: Dict[str, Schedule] = {}
        self.execution_history: Dict[str, ScheduleExecution] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.webhook_endpoints: Dict[str, str] = {}  # webhook_id -> schedule_id
        self._scheduler_running = False

    async def start_scheduler(self):
        """Start the scheduler service"""
        if self._scheduler_running:
            logger.warning("Scheduler is already running")
            return
        
        self._scheduler_running = True
        logger.info("Starting scheduler service")
        
        # Start the main scheduler loop
        asyncio.create_task(self._scheduler_loop())

    async def stop_scheduler(self):
        """Stop the scheduler service"""
        self._scheduler_running = False
        
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        self.running_tasks.clear()
        logger.info("Scheduler service stopped")

    async def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new schedule"""
        try:
            schedule_id = str(uuid.uuid4())
            
            # Validate trigger configuration
            if not await self._validate_trigger_config(schedule_data["trigger_type"], schedule_data["trigger_config"]):
                return {"error": "Invalid trigger configuration"}
            
            schedule = Schedule(
                id=schedule_id,
                name=schedule_data["name"],
                description=schedule_data.get("description", ""),
                trigger_type=TriggerType(schedule_data["trigger_type"]),
                trigger_config=schedule_data["trigger_config"],
                workflow_id=schedule_data["workflow_id"],
                workflow_input=schedule_data.get("workflow_input", {}),
                max_executions=schedule_data.get("max_executions"),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                created_by=schedule_data.get("created_by", "system")
            )
            
            # Calculate next execution time
            schedule.next_execution = await self._calculate_next_execution(schedule)
            
            # Store the schedule
            self.schedules[schedule_id] = schedule
            
            # Store in Redis if available
            if self.redis_service:
                await self.redis_service.set(
                    f"schedule:{schedule_id}",
                    schedule.json(),
                    expire=None  # Persistent
                )
            
            # Set up webhook endpoint if needed
            if schedule.trigger_type == TriggerType.WEBHOOK:
                webhook_id = schedule.trigger_config.get("webhook_id", schedule_id)
                self.webhook_endpoints[webhook_id] = schedule_id
            
            logger.info(f"Created schedule {schedule_id}: {schedule.name}")
            return {
                "status": "created",
                "schedule_id": schedule_id,
                "schedule": schedule.dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to create schedule: {e}")
            return {"error": str(e)}

    async def _validate_trigger_config(self, trigger_type: str, config: Dict[str, Any]) -> bool:
        """Validate trigger configuration"""
        try:
            if trigger_type == TriggerType.CRON:
                cron_expr = config.get("cron_expression")
                if not cron_expr:
                    return False
                # Validate cron expression
                croniter(cron_expr)
                return True
                
            elif trigger_type == TriggerType.INTERVAL:
                interval_seconds = config.get("interval_seconds")
                return isinstance(interval_seconds, int) and interval_seconds > 0
                
            elif trigger_type == TriggerType.WEBHOOK:
                return "webhook_id" in config or "webhook_path" in config
                
            elif trigger_type == TriggerType.EVENT:
                return "event_type" in config
                
            elif trigger_type == TriggerType.MANUAL:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error validating trigger config: {e}")
            return False

    async def _calculate_next_execution(self, schedule: Schedule) -> Optional[str]:
        """Calculate the next execution time for a schedule"""
        try:
            if schedule.trigger_type == TriggerType.CRON:
                cron_expr = schedule.trigger_config["cron_expression"]
                cron = croniter(cron_expr, datetime.now())
                return cron.get_next(datetime).isoformat()
                
            elif schedule.trigger_type == TriggerType.INTERVAL:
                interval_seconds = schedule.trigger_config["interval_seconds"]
                next_time = datetime.now() + timedelta(seconds=interval_seconds)
                return next_time.isoformat()
                
            # Webhook, event, and manual triggers don't have predictable next execution times
            return None
            
        except Exception as e:
            logger.error(f"Error calculating next execution for schedule {schedule.id}: {e}")
            return None

    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self._scheduler_running:
            try:
                current_time = datetime.now()
                
                # Check all active schedules
                for schedule in list(self.schedules.values()):
                    if schedule.status != ScheduleStatus.ACTIVE:
                        continue
                    
                    # Check if max executions reached
                    if schedule.max_executions and schedule.execution_count >= schedule.max_executions:
                        schedule.status = ScheduleStatus.DISABLED
                        continue
                    
                    # Check if it's time to execute
                    if await self._should_execute_now(schedule, current_time):
                        await self._trigger_schedule(schedule)
                
                # Sleep for a short interval before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error

    async def _should_execute_now(self, schedule: Schedule, current_time: datetime) -> bool:
        """Check if a schedule should be executed now"""
        try:
            if not schedule.next_execution:
                return False
            
            next_execution_time = datetime.fromisoformat(schedule.next_execution)
            return current_time >= next_execution_time
            
        except Exception as e:
            logger.error(f"Error checking execution time for schedule {schedule.id}: {e}")
            return False

    async def _trigger_schedule(self, schedule: Schedule):
        """Trigger a scheduled workflow execution"""
        try:
            execution_id = f"{schedule.id}_{datetime.now().timestamp()}"
            
            # Create execution record
            execution = ScheduleExecution(
                execution_id=execution_id,
                schedule_id=schedule.id,
                workflow_id=schedule.workflow_id,
                trigger_type=schedule.trigger_type,
                triggered_at=datetime.now().isoformat(),
                status="triggered"
            )
            
            self.execution_history[execution_id] = execution
            
            # Update schedule
            schedule.execution_count += 1
            schedule.last_execution = datetime.now().isoformat()
            schedule.next_execution = await self._calculate_next_execution(schedule)
            schedule.updated_at = datetime.now().isoformat()
            
            # Trigger workflow execution
            if self.workflow_orchestrator:
                workflow_result = await self.workflow_orchestrator.run_workflow(
                    schedule.workflow_id,
                    schedule.workflow_input
                )
                
                execution.workflow_thread_id = workflow_result.get("thread_id")
                execution.status = "running"
                
                # Start monitoring task
                monitor_task = asyncio.create_task(
                    self._monitor_workflow_execution(execution_id, workflow_result.get("thread_id"))
                )
                self.running_tasks[execution_id] = monitor_task
            else:
                execution.status = "failed"
                execution.error = "No workflow orchestrator available"
                execution.completed_at = datetime.now().isoformat()
            
            logger.info(f"Triggered schedule {schedule.id}: {schedule.name}")
            
        except Exception as e:
            logger.error(f"Error triggering schedule {schedule.id}: {e}")
            if execution_id in self.execution_history:
                self.execution_history[execution_id].status = "failed"
                self.execution_history[execution_id].error = str(e)
                self.execution_history[execution_id].completed_at = datetime.now().isoformat()

    async def _monitor_workflow_execution(self, execution_id: str, thread_id: Optional[str]):
        """Monitor workflow execution and update execution record"""
        try:
            if not thread_id or not self.workflow_orchestrator:
                return
            
            # Poll workflow status
            max_wait = 3600  # 1 hour max
            wait_time = 0
            
            while wait_time < max_wait:
                workflow_state = await self.workflow_orchestrator.get_workflow_state("", thread_id)
                
                if workflow_state.get("status") in ["completed", "failed"]:
                    execution = self.execution_history[execution_id]
                    execution.status = workflow_state["status"]
                    execution.result = workflow_state.get("result")
                    execution.error = workflow_state.get("error")
                    execution.completed_at = datetime.now().isoformat()
                    break
                
                await asyncio.sleep(30)  # Check every 30 seconds
                wait_time += 30
            
            # Cleanup
            if execution_id in self.running_tasks:
                del self.running_tasks[execution_id]
                
        except Exception as e:
            logger.error(f"Error monitoring workflow execution {execution_id}: {e}")

    async def trigger_webhook(self, webhook_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a webhook-based schedule"""
        try:
            if webhook_id not in self.webhook_endpoints:
                return {"error": f"Webhook {webhook_id} not found"}
            
            schedule_id = self.webhook_endpoints[webhook_id]
            schedule = self.schedules.get(schedule_id)
            
            if not schedule or schedule.status != ScheduleStatus.ACTIVE:
                return {"error": f"Schedule {schedule_id} not active"}
            
            # Update workflow input with webhook payload
            workflow_input = {**schedule.workflow_input, "webhook_payload": payload}
            
            # Create temporary schedule for this execution
            temp_schedule = Schedule(**schedule.dict())
            temp_schedule.workflow_input = workflow_input
            
            await self._trigger_schedule(temp_schedule)
            
            return {
                "status": "triggered",
                "schedule_id": schedule_id,
                "webhook_id": webhook_id
            }
            
        except Exception as e:
            logger.error(f"Error triggering webhook {webhook_id}: {e}")
            return {"error": str(e)}

    async def trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger event-based schedules"""
        try:
            triggered_schedules = []
            
            for schedule in self.schedules.values():
                if (schedule.trigger_type == TriggerType.EVENT and 
                    schedule.status == ScheduleStatus.ACTIVE and
                    schedule.trigger_config.get("event_type") == event_type):
                    
                    # Update workflow input with event data
                    workflow_input = {**schedule.workflow_input, "event_data": event_data}
                    
                    # Create temporary schedule for this execution
                    temp_schedule = Schedule(**schedule.dict())
                    temp_schedule.workflow_input = workflow_input
                    
                    await self._trigger_schedule(temp_schedule)
                    triggered_schedules.append(schedule.id)
            
            return {
                "status": "triggered",
                "event_type": event_type,
                "triggered_schedules": triggered_schedules
            }
            
        except Exception as e:
            logger.error(f"Error triggering event {event_type}: {e}")
            return {"error": str(e)}

    async def manual_trigger(self, schedule_id: str, workflow_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manually trigger a schedule"""
        try:
            if schedule_id not in self.schedules:
                return {"error": f"Schedule {schedule_id} not found"}
            
            schedule = self.schedules[schedule_id]
            
            if workflow_input:
                # Create temporary schedule with custom input
                temp_schedule = Schedule(**schedule.dict())
                temp_schedule.workflow_input = {**schedule.workflow_input, **workflow_input}
                await self._trigger_schedule(temp_schedule)
            else:
                await self._trigger_schedule(schedule)
            
            return {
                "status": "triggered",
                "schedule_id": schedule_id
            }
            
        except Exception as e:
            logger.error(f"Error manually triggering schedule {schedule_id}: {e}")
            return {"error": str(e)}

    async def list_schedules(self, status: Optional[ScheduleStatus] = None) -> List[Dict[str, Any]]:
        """List all schedules, optionally filtered by status"""
        try:
            schedules = []
            
            for schedule in self.schedules.values():
                if status and schedule.status != status:
                    continue
                schedules.append(schedule.dict())
            
            # Sort by creation time
            schedules.sort(key=lambda x: x["created_at"], reverse=True)
            
            return schedules
            
        except Exception as e:
            logger.error(f"Failed to list schedules: {e}")
            return []

    async def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific schedule"""
        try:
            if schedule_id in self.schedules:
                return self.schedules[schedule_id].dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get schedule {schedule_id}: {e}")
            return None

    async def update_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a schedule"""
        try:
            if schedule_id not in self.schedules:
                return {"error": f"Schedule {schedule_id} not found"}
            
            schedule = self.schedules[schedule_id]
            
            # Update allowed fields
            allowed_updates = ["name", "description", "status", "trigger_config", "workflow_input", "max_executions"]
            for key, value in updates.items():
                if key in allowed_updates:
                    setattr(schedule, key, value)
            
            # Recalculate next execution if trigger config changed
            if "trigger_config" in updates:
                schedule.next_execution = await self._calculate_next_execution(schedule)
            
            schedule.updated_at = datetime.now().isoformat()
            
            # Update in Redis if available
            if self.redis_service:
                await self.redis_service.set(
                    f"schedule:{schedule_id}",
                    schedule.json(),
                    expire=None
                )
            
            logger.info(f"Updated schedule {schedule_id}")
            return {
                "status": "updated",
                "schedule_id": schedule_id,
                "schedule": schedule.dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to update schedule {schedule_id}: {e}")
            return {"error": str(e)}

    async def delete_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Delete a schedule"""
        try:
            if schedule_id not in self.schedules:
                return {"error": f"Schedule {schedule_id} not found"}
            
            schedule = self.schedules[schedule_id]
            
            # Cancel any running tasks
            for execution_id, task in list(self.running_tasks.items()):
                if execution_id.startswith(schedule_id):
                    task.cancel()
                    del self.running_tasks[execution_id]
            
            # Remove webhook endpoint if exists
            if schedule.trigger_type == TriggerType.WEBHOOK:
                webhook_id = schedule.trigger_config.get("webhook_id", schedule_id)
                if webhook_id in self.webhook_endpoints:
                    del self.webhook_endpoints[webhook_id]
            
            # Remove from storage
            del self.schedules[schedule_id]
            
            # Remove from Redis if available
            if self.redis_service:
                await self.redis_service.delete(f"schedule:{schedule_id}")
            
            logger.info(f"Deleted schedule {schedule_id}")
            return {"status": "deleted", "schedule_id": schedule_id}
            
        except Exception as e:
            logger.error(f"Failed to delete schedule {schedule_id}: {e}")
            return {"error": str(e)}

    async def get_execution_history(self, schedule_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history"""
        try:
            executions = []
            
            for execution in self.execution_history.values():
                if schedule_id and execution.schedule_id != schedule_id:
                    continue
                executions.append(execution.dict())
            
            # Sort by trigger time (most recent first)
            executions.sort(key=lambda x: x["triggered_at"], reverse=True)
            
            return executions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []