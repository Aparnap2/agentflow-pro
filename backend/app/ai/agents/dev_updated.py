"""
Updated DevAgent with comprehensive development management capabilities.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date, timedelta
from enum import Enum
import logging
from pydantic import BaseModel, Field, validator

from .base_agent import BaseAgent, AgentConfig, AgentResponse

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    """Status of a development task."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    CODE_REVIEW = "code_review"
    QA_TESTING = "qa_testing"
    DONE = "done"
    BLOCKED = "blocked"

class Priority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskType(str, Enum):
    """Types of development tasks."""
    FEATURE = "feature"
    BUG = "bug"
    REFACTOR = "refactor"
    DOCS = "documentation"
    TEST = "test"
    MAINTENANCE = "maintenance"

class PullRequestStatus(str, Enum):
    """Status of a pull request."""
    OPEN = "open"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    MERGED = "merged"
    CLOSED = "closed"

class DeploymentStatus(str, Enum):
    """Status of a deployment."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class Task(BaseModel):
    """Development task model."""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    type: TaskType = TaskType.FEATURE
    priority: Priority = Priority.MEDIUM
    assignee_id: Optional[str] = None
    reporter_id: str
    project_id: str
    story_points: Optional[int] = None
    due_date: Optional[date] = None
    labels: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class PullRequest(BaseModel):
    """Pull request model."""
    id: str
    title: str
    description: str
    status: PullRequestStatus = PullRequestStatus.OPEN
    source_branch: str
    target_branch: str
    author_id: str
    reviewers: List[str] = []
    task_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Deployment(BaseModel):
    """Deployment model."""
    id: str
    environment: str  # e.g., 'development', 'staging', 'production'
    status: DeploymentStatus = DeploymentStatus.PENDING
    commit_hash: str
    deployed_by: str
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    logs: Optional[str] = None
    metadata: Dict[str, Any] = {}

class Project(BaseModel):
    """Project model for development work."""
    id: str
    name: str
    description: str
    owner_id: str
    team_ids: List[str] = []
    start_date: date
    target_end_date: Optional[date] = None
    status: str = "active"  # active, completed, on_hold, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DevAgent(BaseAgent):
    """
    Comprehensive Development Agent with software development management capabilities.
    
    This agent provides a complete suite of development functions including:
    - Task and issue tracking
    - Code review management
    - Pull request workflows
    - Deployment coordination
    - Development environment management
    - Code quality monitoring
    - CI/CD pipeline management
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.tasks: Dict[str, Task] = {}
        self.pull_requests: Dict[str, PullRequest] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.projects: Dict[str, Project] = {}
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.vcs = get_version_control_integration()
            self.ci_cd = get_ci_cd_integration()
            self.communication = get_communication_integration()
            self.analytics = get_analytics_integration()
            logger.info("Development Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Development Agent integrations: {str(e)}")
            raise
    
    # Task Management
    async def create_task(self, task_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new development task.
        
        Args:
            task_data: Dictionary containing task details
                - title: Task title
                - description: Task description
                - type: Type of task (from TaskType enum)
                - priority: Priority level (from Priority enum)
                - assignee_id: Optional ID of assignee
                - reporter_id: ID of the reporter
                - project_id: ID of the project
                - story_points: Optional story points
                - due_date: Optional due date
                - labels: List of labels
                
        Returns:
            AgentResponse with created task or error
        """
        try:
            task = Task(**task_data)
            self.tasks[task.id] = task
            
            # Notify assignee if assigned
            if task.assignee_id:
                await self._notify_task_assignment(task)
            
            logger.info(f"Created task: {task.title} ({task.id})")
            
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
    
    async def _notify_task_assignment(self, task: Task) -> None:
        """Notify assignee about a new task assignment."""
        # In a real implementation, this would fetch user details and send a notification
        logger.info(f"Notifying user {task.assignee_id} about new task {task.id}")
        
        subject = f"New Task Assigned: {task.title}"
        
        body = f"""
        Hello,
        
        You have been assigned a new task:
        
        Title: {task.title}
        Type: {task.type.value}
        Priority: {task.priority.value}
        Status: {task.status.value}
        
        Description:
        {task.description}
        
        You can view the task here:
        {self.config.get('task_management_url', '')}/tasks/{task.id}
        
        Best regards,
        Development Team
        """
        
        await self.communication.send_notification(
            user_id=task.assignee_id,
            subject=subject,
            message=body.strip()
        )
    
    async def update_task_status(self, task_id: str, status: TaskStatus, comment: Optional[str] = None) -> AgentResponse:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status (from TaskStatus enum)
            comment: Optional comment about the status change
            
        Returns:
            AgentResponse with update status or error
        """
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
                
            task = self.tasks[task_id]
            previous_status = task.status
            task.status = status
            task.updated_at = datetime.utcnow()
            
            # Log the status change
            logger.info(f"Updated task {task_id} status from {previous_status} to {status}")
            
            # Notify relevant team members about the status change
            await self._notify_task_status_change(task, previous_status, comment)
            
            return AgentResponse(
                success=True,
                output={"task": task.dict()},
                message=f"Updated task status to {status}"
            )
            
        except Exception as e:
            error_msg = f"Failed to update task status: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_task_status_change(self, task: Task, previous_status: TaskStatus, comment: Optional[str] = None) -> None:
        """Notify relevant team members about a task status change."""
        # In a real implementation, this would fetch user details and send notifications
        if not task.assignee_id and not task.reporter_id:
            return
            
        recipients = set()
        if task.assignee_id:
            recipients.add(task.assignee_id)
        if task.reporter_id and task.reporter_id != task.assignee_id:
            recipients.add(task.reporter_id)
        
        subject = f"Task {task.id} status changed from {previous_status} to {task.status}"
        
        body = f"""
        Task: {task.title}
        Status changed: {previous_status} → {task.status}
        """
        
        if comment:
            body += f"\nComment: {comment}\n"
            
        body += f"""
        View the task here:
        {self.config.get('task_management_url', '')}/tasks/{task.id}
        """
        
        for user_id in recipients:
            await self.communication.send_notification(
                user_id=user_id,
                subject=subject,
                message=body.strip()
            )
    
    # Pull Request Management
    async def create_pull_request(self, pr_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new pull request.
        
        Args:
            pr_data: Dictionary containing PR details
                - title: PR title
                - description: PR description
                - source_branch: Source branch name
                - target_branch: Target branch name
                - author_id: ID of the PR author
                - reviewers: List of reviewer IDs
                - task_ids: List of related task IDs
                
        Returns:
            AgentResponse with created PR or error
        """
        try:
            pr = PullRequest(**pr_data)
            self.pull_requests[pr.id] = pr
            
            # Create PR in version control system
            await self.vcs.create_pull_request(pr.dict())
            
            # Notify reviewers
            await self._notify_reviewers(pr)
            
            logger.info(f"Created PR: {pr.title} ({pr.id})")
            
            return AgentResponse(
                success=True,
                output={"pull_request": pr.dict()},
                message=f"Created PR: {pr.title}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create pull request: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_reviewers(self, pr: PullRequest) -> None:
        """Notify reviewers about a new PR."""
        if not pr.reviewers:
            return
            
        subject = f"PR Review Requested: {pr.title}"
        
        body = f"""
        Hello,
        
        You have been requested to review a pull request:
        
        Title: {pr.title}
        Author: {pr.author_id}
        Source: {pr.source_branch} → {pr.target_branch}
        
        Description:
        {pr.description}
        
        Please review the changes at your earliest convenience.
        
        View the PR here:
        {self.config.get('vcs_url', '')}/pull/{pr.id}
        
        Best regards,
        Development Team
        """
        
        for reviewer_id in pr.reviewers:
            await self.communication.send_notification(
                user_id=reviewer_id,
                subject=subject,
                message=body.strip()
            )
    
    # Deployment Management
    async def deploy_to_environment(self, deployment_data: Dict[str, Any]) -> AgentResponse:
        """
        Deploy code to an environment.
        
        Args:
            deployment_data: Dictionary containing deployment details
                - environment: Target environment (e.g., 'staging', 'production')
                - commit_hash: Commit hash to deploy
                - deployed_by: ID of the user initiating the deployment
                - metadata: Optional deployment metadata
                
        Returns:
            AgentResponse with deployment status or error
        """
        try:
            deployment = Deployment(**deployment_data)
            self.deployments[deployment.id] = deployment
            
            # Trigger deployment in CI/CD system
            deployment_result = await self.ci_cd.trigger_deployment(
                environment=deployment.environment,
                commit_hash=deployment.commit_hash,
                metadata=deployment.metadata
            )
            
            # Update deployment status based on result
            deployment.status = DeploymentStatus.IN_PROGRESS
            deployment.logs = deployment_result.get('logs')
            
            # Simulate deployment completion (in real app, this would be async)
            if deployment_result.get('status') == 'success':
                deployment.status = DeploymentStatus.SUCCESS
            else:
                deployment.status = DeploymentStatus.FAILED
                
            deployment.completed_at = datetime.utcnow()
            
            # Notify team about deployment status
            await self._notify_deployment_status(deployment)
            
            logger.info(f"Deployment {deployment.id} to {deployment.environment} {deployment.status}")
            
            return AgentResponse(
                success=deployment.status == DeploymentStatus.SUCCESS,
                output={"deployment": deployment.dict()},
                message=f"Deployment to {deployment.environment} {deployment.status}"
            )
            
        except Exception as e:
            error_msg = f"Deployment failed: {str(e)}"
            logger.error(error_msg)
            
            # Update deployment status if it was created
            if 'deployment' in locals():
                deployment.status = DeploymentStatus.FAILED
                deployment.completed_at = datetime.utcnow()
                deployment.logs = error_msg
            
            return AgentResponse(
                success=False,
                error=error_msg,
                output={"deployment": deployment.dict()} if 'deployment' in locals() else None
            )
    
    async def _notify_deployment_status(self, deployment: Deployment) -> None:
        """Notify team about deployment status."""
        # In a real implementation, this would fetch team members and send notifications
        subject = f"Deployment to {deployment.environment} {deployment.status}"
        
        body = f"""
        Deployment Details:
        
        Environment: {deployment.environment}
        Status: {deployment.status.upper()}
        Commit: {deployment.commit_hash}
        Deployed by: {deployment.deployed_by}
        """
        
        if deployment.completed_at:
            body += f"\nCompleted at: {deployment.completed_at.isoformat()}"
            
        if deployment.logs:
            body += f"\n\nLogs:\n{deployment.logs[:500]}..."  # Truncate long logs
        
        # In a real app, this would be sent to the appropriate team channel
        await self.communication.send_team_notification(
            team_id="dev-team",  # Would be dynamic in a real app
            subject=subject,
            message=body.strip()
        )

# Mock integration functions
def get_version_control_integration():
    class MockVCSIntegration:
        async def create_pull_request(self, pr_data):
            logger.info(f"[MockVCS] Creating PR: {pr_data['title']}")
            return {"status": "success", "pr_url": f"https://vcs.example.com/pr/123"}
            
        async def get_commit_details(self, commit_hash):
            return {
                "hash": commit_hash,
                "message": "Update README.md",
                "author": "dev@example.com",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    return MockVCSIntegration()

def get_ci_cd_integration():
    class MockCICDIntegration:
        async def trigger_deployment(self, environment, commit_hash, metadata=None):
            logger.info(f"[MockCI/CD] Deploying {commit_hash} to {environment}")
            # Simulate deployment
            return {
                "status": "success",
                "logs": "Deployment completed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    return MockCICDIntegration()

# Update the __init__.py to expose the new DevAgent
__all__ = [
    'DevAgent',
    'Task',
    'PullRequest',
    'Deployment',
    'Project',
    'TaskStatus',
    'Priority',
    'TaskType',
    'PullRequestStatus',
    'DeploymentStatus'
]
