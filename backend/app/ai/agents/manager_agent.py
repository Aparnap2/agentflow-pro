"""
Manager Agent for team coordination and operational management.
"""

from typing import Dict, Any, List, Optional, Union, Type, TypeVar, Callable
from enum import Enum, auto
import json
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator, HttpUrl
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_agent import BaseAgent, AgentConfig, AgentResponse, AgentState
from ..integrations import (
    get_project_management_integration,
    get_communication_integration,
    get_hr_integration,
    get_document_integration
)

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    """Status of a task."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    CODE_REVIEW = "code_review"
    QA = "qa"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TeamMember(BaseModel):
    """Team member information."""
    id: str
    name: str
    email: str
    role: str
    skills: List[str] = Field(default_factory=list)
    capacity_hours: float = 40.0
    current_workload: float = 0.0  # 0-100% of capacity
    projects: List[str] = Field(default_factory=list)
    join_date: datetime = Field(default_factory=datetime.utcnow)

class Task(BaseModel):
    """A work item to be completed."""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[str] = None
    reporter_id: str
    project_id: str
    story_points: Optional[int] = None
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    labels: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    time_estimate_hours: Optional[float] = None
    time_spent_hours: float = 0.0
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class Project(BaseModel):
    """Project information."""
    id: str
    name: str
    description: str
    status: str  # planning, active, on_hold, completed, cancelled
    start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    team_member_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TeamMetrics(BaseModel):
    """Team performance metrics."""
    velocity: float  # Story points completed per sprint
    capacity: float  # Total available capacity in hours
    utilization: float  # Current utilization percentage
    avg_lead_time: float  # Average time to complete tasks in days
    avg_cycle_time: float  # Average time from start to completion
    open_tasks: int
    completed_tasks: int
    blocked_tasks: int
    overdue_tasks: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ManagerAgent(BaseAgent):
    """
    Manager Agent responsible for team coordination and operational management.
    
    This agent provides capabilities for:
    - Task assignment and tracking
    - Team workload management
    - Project planning and execution
    - Performance monitoring
    - Team communication and collaboration
    - Resource allocation
    - Process improvement
    - Risk management
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.team_members: Dict[str, TeamMember] = {}
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.metrics = TeamMetrics(
            velocity=0.0,
            capacity=0.0,
            utilization=0.0,
            avg_lead_time=0.0,
            avg_cycle_time=0.0,
            open_tasks=0,
            completed_tasks=0,
            blocked_tasks=0,
            overdue_tasks=0
        )
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.project_management = get_project_management_integration()
            self.communication = get_communication_integration()
            self.hr = get_hr_integration()
            self.docs = get_document_integration()
            logger.info("Manager Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Manager Agent integrations: {str(e)}")
            raise
    
    async def add_team_member(self, member_data: Dict[str, Any]) -> AgentResponse:
        """
        Add a new team member.
        
        Args:
            member_data: Dictionary containing team member details
            
        Returns:
            AgentResponse with created team member or error
        """
        try:
            member = TeamMember(**member_data)
            self.team_members[member.id] = member
            
            # Update team metrics
            self._update_team_capacity()
            
            logger.info(f"Added team member: {member.name} ({member.role})")
            
            return AgentResponse(
                success=True,
                output={"team_member": member.dict()},
                message=f"Added team member: {member.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to add team member: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    def _update_team_capacity(self) -> None:
        """Update team capacity based on current team members."""
        total_capacity = sum(
            member.capacity_hours * (1 - member.current_workload / 100)
            for member in self.team_members.values()
        )
        
        self.metrics.capacity = total_capacity
        
        # Calculate utilization
        total_workload = sum(
            member.capacity_hours * (member.current_workload / 100)
            for member in self.team_members.values()
        )
        
        total_available = sum(member.capacity_hours for member in self.team_members.values())
        self.metrics.utilization = (total_workload / total_available * 100) if total_available > 0 else 0
    
    async def create_project(self, project_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new project.
        
        Args:
            project_data: Dictionary containing project details
            
        Returns:
            AgentResponse with created project or error
        """
        try:
            project = Project(**project_data)
            self.projects[project.id] = project
            
            logger.info(f"Created project: {project.name}")
            
            # Create project in project management tool
            await self.project_management.create_project({
                "name": project.name,
                "description": project.description,
                "start_date": project.start_date,
                "target_end_date": project.target_end_date,
                "tags": project.tags
            })
            
            return AgentResponse(
                success=True,
                output={"project": project.dict()},
                message=f"Created project: {project.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create project: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def create_task(self, task_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new task.
        
        Args:
            task_data: Dictionary containing task details
            
        Returns:
            AgentResponse with created task or error
        """
        try:
            task = Task(**task_data)
            self.tasks[task.id] = task
            
            # Update project task count if project exists
            if task.project_id in self.projects:
                project = self.projects[task.project_id]
                project.updated_at = datetime.utcnow()
            
            # Create task in project management tool
            await self.project_management.create_task({
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "assignee_id": task.assignee_id,
                "project_id": task.project_id,
                "due_date": task.due_date,
                "labels": task.labels,
                "time_estimate_hours": task.time_estimate_hours
            })
            
            logger.info(f"Created task: {task.title}")
            
            # Update metrics
            self._update_task_metrics()
            
            return AgentResponse(
                success=True,
                output={"task": task.dict()},
                message=f"Created task: {task.title}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create task: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    def _update_task_metrics(self) -> None:
        """Update task-related metrics."""
        now = datetime.utcnow()
        
        open_tasks = 0
        completed_tasks = 0
        blocked_tasks = 0
        overdue_tasks = 0
        total_cycle_time = 0.0
        completed_count = 0
        
        for task in self.tasks.values():
            if task.status == TaskStatus.DONE:
                completed_tasks += 1
                if task.updated_at and task.created_at:
                    cycle_time = (task.updated_at - task.created_at).total_seconds() / 3600 / 24  # in days
                    total_cycle_time += cycle_time
                    completed_count += 1
            elif task.status == TaskStatus.BLOCKED:
                blocked_tasks += 1
            else:
                open_tasks += 1
                if task.due_date and task.due_date < now:
                    overdue_tasks += 1
        
        # Update metrics
        self.metrics.open_tasks = open_tasks
        self.metrics.completed_tasks = completed_tasks
        self.metrics.blocked_tasks = blocked_tasks
        self.metrics.overdue_tasks = overdue_tasks
        
        # Calculate average cycle time for completed tasks
        if completed_count > 0:
            self.metrics.avg_cycle_time = total_cycle_time / completed_count
    
    async def assign_task(
        self, 
        task_id: str, 
        assignee_id: str, 
        force: bool = False
    ) -> AgentResponse:
        """
        Assign a task to a team member.
        
        Args:
            task_id: ID of the task to assign
            assignee_id: ID of the team member to assign to
            force: If True, assign even if it exceeds capacity
            
        Returns:
            AgentResponse with updated task or error
        """
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            if assignee_id not in self.team_members:
                raise ValueError(f"Team member {assignee_id} not found")
            
            task = self.tasks[task_id]
            assignee = self.team_members[assignee_id]
            
            # Check if assignee has capacity
            task_effort = task.time_estimate_hours or 8  # Default to 1 day
            
            if not force and (assignee.current_workload + task_effort) > assignee.capacity_hours:
                return AgentResponse(
                    success=False,
                    error=f"Assignee {assignee.name} would exceed capacity with this task",
                    metadata={
                        "current_workload": assignee.current_workload,
                        "capacity": assignee.capacity_hours,
                        "required_additional": task_effort
                    }
                )
            
            # Update task
            old_assignee_id = task.assignee_id
            task.assignee_id = assignee_id
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.utcnow()
            
            # Update assignee's workload
            if old_assignee_id and old_assignee_id in self.team_members:
                old_assignee = self.team_members[old_assignee_id]
                old_assignee.current_workload -= task_effort
                
            assignee.current_workload += task_effort
            
            # Update team metrics
            self._update_team_capacity()
            
            # Update task in project management tool
            await self.project_management.update_task(task_id, {
                "assignee_id": assignee_id,
                "status": task.status
            })
            
            logger.info(f"Assigned task {task_id} to {assignee.name}")
            
            # Notify assignee
            await self.communication.send_message(
                channel=f"@{assignee.email}",
                message=f"📋 You've been assigned to task: {task.title}\n"
                       f"🔗 [View Task]({self._get_task_url(task_id)})"
            )
            
            return AgentResponse(
                success=True,
                output={"task": task.dict()},
                message=f"Assigned task to {assignee.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to assign task: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    def _get_task_url(self, task_id: str) -> str:
        """Generate a URL to view the task in the project management tool."""
        # This would be implemented based on the actual project management tool being used
        base_url = self.project_management.get_base_url()
        return f"{base_url}/tasks/{task_id}"
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: Union[str, TaskStatus],
        comment: Optional[str] = None
    ) -> AgentResponse:
        """
        Update a task's status.
        
        Args:
            task_id: ID of the task to update
            status: New status
            comment: Optional comment about the status change
            
        Returns:
            AgentResponse with updated task or error
        """
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            
            # Validate status transition
            current_status = TaskStatus(task.status)
            new_status = TaskStatus(status)
            
            # Basic validation of status transition
            if current_status == new_status:
                return AgentResponse(
                    success=True,
                    output={"task": task.dict()},
                    message="Status unchanged"
                )
            
            # Update task
            old_status = task.status
            task.status = new_status
            task.updated_at = datetime.utcnow()
            
            # Update task in project management tool
            await self.project_management.update_task(task_id, {
                "status": new_status,
                "comment": comment
            })
            
            logger.info(f"Updated task {task_id} status from {old_status} to {new_status}")
            
            # Handle status-specific actions
            if new_status == TaskStatus.DONE:
                await self._on_task_completed(task)
            elif new_status == TaskStatus.BLOCKED:
                await self._on_task_blocked(task, comment)
            
            # Update metrics
            self._update_task_metrics()
            
            return AgentResponse(
                success=True,
                output={"task": task.dict()},
                message=f"Updated task status to {new_status}"
            )
            
        except Exception as e:
            error_msg = f"Failed to update task status: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _on_task_completed(self, task: Task) -> None:
        """Handle actions when a task is marked as done."""
        # Update assignee's workload
        if task.assignee_id and task.assignee_id in self.team_members:
            assignee = self.team_members[task.assignee_id]
            task_effort = task.time_estimate_hours or 8
            assignee.current_workload = max(0, assignee.current_workload - task_effort)
            
            # Update team capacity
            self._update_team_capacity()
        
        # Log completion
        logger.info(f"Task completed: {task.title}")
        
        # Notify relevant stakeholders
        if task.reporter_id and task.reporter_id in self.team_members:
            reporter = self.team_members[task.reporter_id]
            await self.communication.send_message(
                channel=f"@{reporter.email}",
                message=f"✅ Task completed: {task.title}\n"
                       f"By: {self.team_members[task.assignee_id].name if task.assignee_id else 'Unassigned'}\n"
                       f"🔗 [View Task]({self._get_task_url(task.id)})"
            )
    
    async def _on_task_blocked(self, task: Task, reason: Optional[str] = None) -> None:
        """Handle actions when a task is blocked."""
        # Notify relevant stakeholders
        if task.assignee_id and task.assignee_id in self.team_members:
            assignee = self.team_members[task.assignee_id]
            
            message = f"🚨 Task blocked: {task.title}\n"
            if reason:
                message += f"Reason: {reason}\n"
            message += f"🔗 [View Task]({self._get_task_url(task.id)})"
            
            # Notify assignee
            await self.communication.send_message(
                channel=f"@{assignee.email}",
                message=message
            )
            
            # Notify manager if different from assignee
            if task.reporter_id and task.reporter_id != task.assignee_id and task.reporter_id in self.team_members:
                await self.communication.send_message(
                    channel=f"@{self.team_members[task.reporter_id].email}",
                    message=f"🚨 Task blocked: {task.title}\n"
                           f"Assigned to: {assignee.name}\n"
                           f"Reason: {reason or 'No reason provided'}\n"
                           f"🔗 [View Task]({self._get_task_url(task.id)})"
                )
    
    async def get_team_metrics(self) -> AgentResponse:
        """
        Get current team performance metrics.
        
        Returns:
            AgentResponse with team metrics
        """
        try:
            # Update metrics before returning
            self._update_team_capacity()
            self._update_task_metrics()
            
            return AgentResponse(
                success=True,
                output={"metrics": self.metrics.dict()},
                message="Retrieved team metrics"
            )
            
        except Exception as e:
            error_msg = f"Failed to get team metrics: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def optimize_workload(self) -> AgentResponse:
        """
        Optimize workload distribution across team members.
        
        Returns:
            AgentResponse with optimization results
        """
        try:
            # Get all unassigned tasks
            unassigned_tasks = [
                task for task in self.tasks.values() 
                if not task.assignee_id and task.status != TaskStatus.DONE
            ]
            
            # Sort tasks by priority (critical first) and then by due date (earliest first)
            unassigned_tasks.sort(
                key=lambda t: (
                    t.priority != TaskPriority.CRITICAL,
                    t.due_date or datetime.max
                )
            )
            
            # Get team members with available capacity
            available_members = [
                member for member in self.team_members.values()
                if member.current_workload < member.capacity_hours * 0.9  # Leave 10% buffer
            ]
            
            if not available_members:
                return AgentResponse(
                    success=False,
                    error="No team members with available capacity",
                    metadata={
                        "unassigned_tasks": len(unassigned_tasks),
                        "available_members": 0
                    }
                )
            
            # Sort members by current workload (least busy first)
            available_members.sort(key=lambda m: m.current_workload)
            
            # Assign tasks to available members
            assignments = {}
            for task in unassigned_tasks:
                task_effort = task.time_estimate_hours or 8
                
                # Find first available member with enough capacity
                for member in available_members:
                    if (member.current_workload + task_effort) <= member.capacity_hours * 0.9:  # 90% threshold
                        # Assign task
                        await self.assign_task(task.id, member.id)
                        
                        # Track assignment
                        if member.id not in assignments:
                            assignments[member.id] = []
                        assignments[member.id].append(task.id)
                        
                        # Update member's workload
                        member.current_workload += task_effort
                        break
            
            # Update team metrics
            self._update_team_capacity()
            
            return AgentResponse(
                success=True,
                output={
                    "assignments": assignments,
                    "unassigned_tasks_remaining": len([
                        t for t in unassigned_tasks 
                        if t.id not in [tid for tasks in assignments.values() for tid in tasks]
                    ]),
                    "metrics": self.metrics.dict()
                },
                message=f"Assigned {sum(len(tasks) for tasks in assignments.values())} tasks to team members"
            )
            
        except Exception as e:
            error_msg = f"Failed to optimize workload: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        # Initialize Manager Agent
        config = {
            "name": "Engineering Manager Agent",
            "description": "Manages engineering team tasks and projects",
            "llm": {
                "model": "gpt-4"
            }
        }
        
        manager = ManagerAgent(config=config)
        
        # Add team members
        await manager.add_team_member({
            "id": "dev1",
            "name": "Alice Developer",
            "email": "alice@example.com",
            "role": "Senior Developer",
            "skills": ["python", "backend", "api"],
            "capacity_hours": 40.0
        })
        
        await manager.add_team_member({
            "id": "dev2",
            "name": "Bob Developer",
            "email": "bob@example.com",
            "role": "Frontend Developer",
            "skills": ["javascript", "react", "frontend"],
            "capacity_hours": 35.0
        })
        
        # Create a project
        await manager.create_project({
            "id": "proj1",
            "name": "New Feature Development",
            "description": "Build and deploy new user dashboard",
            "status": "planning",
            "start_date": datetime.utcnow(),
            "target_end_date": datetime.utcnow() + timedelta(days=30),
            "tags": ["feature", "dashboard"]
        })
        
        # Create some tasks
        await manager.create_task({
            "id": "task1",
            "title": "Design database schema",
            "description": "Design and document the database schema for the new feature",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.HIGH,
            "reporter_id": "dev1",
            "project_id": "proj1",
            "time_estimate_hours": 8.0,
            "labels": ["backend", "database"]
        })
        
        await manager.create_task({
            "id": "task2",
            "title": "Create API endpoints",
            "description": "Implement REST API endpoints for the new feature",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.HIGH,
            "reporter_id": "dev1",
            "project_id": "proj1",
            "time_estimate_hours": 16.0,
            "labels": ["backend", "api"]
        })
        
        await manager.create_task({
            "id": "task3",
            "title": "Design UI mockups",
            "description": "Create mockups for the new dashboard UI",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.MEDIUM,
            "reporter_id": "dev2",
            "project_id": "proj1",
            "time_estimate_hours": 12.0,
            "labels": ["frontend", "design"]
        })
        
        # Assign tasks
        await manager.assign_task("task1", "dev1")
        await manager.assign_task("task2", "dev1")
        await manager.assign_task("task3", "dev2")
        
        # Update task status
        await manager.update_task_status("task1", TaskStatus.IN_PROGRESS)
        await manager.update_task_status("task3", TaskStatus.IN_PROGRESS)
        
        # Complete a task
        await manager.update_task_status("task1", TaskStatus.DONE, "Completed database schema design")
        
        # Optimize workload
        optimization = await manager.optimize_workload()
        print("Workload optimization result:", optimization.output)
        
        # Get team metrics
        metrics = await manager.get_team_metrics()
        print("\nTeam metrics:", metrics.output["metrics"])
    
    asyncio.run(main())
