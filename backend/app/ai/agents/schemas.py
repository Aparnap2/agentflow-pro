"""
Pydantic models for agent configuration, state management, and data structures.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator, HttpUrl, EmailStr, conint, confloat

# Core Enums
class AgentRole(str, Enum):
    """Defines the role of an agent in the system."""
    STRATEGIC_PLANNER = "strategic_planner"
    MARKETING_SPECIALIST = "marketing_specialist"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    SALES_AGENT = "sales_agent"
    HR_SPECIALIST = "hr_specialist"
    FINANCE_SPECIALIST = "finance_specialist"
    SUPPORT_AGENT = "support_agent"
    ANALYTICS_ENGINEER = "analytics_engineer"


# Base Models
class AgentResponse(BaseModel):
    """Standard response format for agent operations."""
    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentConfig(BaseModel):
    """Configuration for creating an agent."""
    id: str = Field(..., description="Unique identifier for the agent")
    role: str = Field(..., description="The agent's specialized function")
    goal: str = Field(..., description="The agent's primary objective")
    backstory: str = Field(..., description="The agent's background and expertise")
    tools: List[str] = Field(default_factory=list, description="List of tool names the agent can use")
    verbose: bool = Field(False, description="Enable verbose output")
    allow_delegation: bool = Field(True, description="Allow agent to delegate tasks")
    max_iter: int = Field(15, description="Maximum number of iterations for task execution")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    integrations: Dict[str, Any] = Field(default_factory=dict, description="Integration configurations")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "market_researcher_1",
                "role": "Market Research Analyst",
                "goal": "Conduct thorough market research to identify trends and opportunities",
                "backstory": "You are an experienced market researcher with expertise in analyzing industry trends and consumer behavior.",
                "tools": ["web_search", "data_analysis"],
                "verbose": True,
                "allow_delegation": True,
                "max_iter": 10,
                "integrations": {
                    "database": {"type": "postgres", "connection_string": "..."},
                    "email": {"provider": "sendgrid", "api_key": "..."}
                }
            }
        }


# State Management
class AgentState(BaseModel):
    """Represents the state of an agent during execution."""
    agent_id: str
    current_task: Optional[str] = None
    memory: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["idle", "processing", "error", "completed"] = "idle"
    error: Optional[str] = None
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress of current task (0.0 to 1.0)")

class AgentMemory(BaseModel):
    """Structured memory for agent context and history."""
    facts: Dict[str, Any] = Field(default_factory=dict)
    conversations: List[Dict[str, Any]] = Field(default_factory=list)
    tasks_completed: List[Dict[str, Any]] = Field(default_factory=list)
    knowledge: Dict[str, Any] = Field(default_factory=dict)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)


# Agent Collaboration
class CrewConfig(BaseModel):
    """Configuration for creating a crew of agents."""
    id: str = Field(..., description="Unique identifier for the crew")
    name: str = Field(..., description="Display name of the crew")
    description: str = Field(..., description="Purpose and responsibilities of the crew")
    agent_ids: List[str] = Field(..., description="List of agent IDs in this crew")
    process: Literal["hierarchical", "sequential", "parallel"] = "hierarchical"
    verbose: bool = Field(False, description="Enable verbose logging for the crew")
    memory: bool = Field(True, description="Enable shared memory for the crew")
    cache: bool = Field(True, description="Enable caching for the crew's operations")
    max_rounds: int = Field(5, ge=1, description="Maximum number of interaction rounds")
    manager_llm_config: Optional[Dict[str, Any]] = Field(
        None,
        description="LLM configuration for the crew manager"
    )
    communication_protocol: str = Field(
        "round_robin",
        description="Protocol for agent communication (round_robin, broadcast, direct)"
    )
    conflict_resolution: str = Field(
        "consensus",
        description="Conflict resolution strategy (consensus, manager_decision, vote)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")

class CrewState(BaseModel):
    """State of a crew during execution."""
    crew_id: str
    current_round: int = 0
    active_agent_id: Optional[str] = None
    state: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["idle", "active", "completed", "error"] = "idle"


# Workflow Management
class WorkflowStep(BaseModel):
    """Represents a step in a workflow."""
    id: str = Field(..., description="Unique identifier for the step")
    name: str = Field(..., description="Display name of the step")
    description: str = Field(..., description="Detailed description of the step's purpose")
    agent_id: str = Field(..., description="ID of the agent responsible for this step")
    expected_output: str = Field(..., description="Description of the expected output")
    tools: List[str] = Field(default_factory=list, description="Tools required for this step")
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of step IDs that must complete before this step starts"
    )
    timeout_seconds: Optional[int] = Field(
        None,
        description="Maximum time allowed for this step in seconds"
    )
    retry_attempts: int = Field(0, description="Number of retry attempts on failure")
    is_critical: bool = Field(True, description="Whether workflow fails if this step fails")
    config: Dict[str, Any] = Field(default_factory=dict, description="Step-specific configuration")

class WorkflowConfig(BaseModel):
    """Configuration for a workflow."""
    id: str = Field(..., description="Unique identifier for the workflow")
    name: str = Field(..., description="Display name of the workflow")
    description: str = Field(..., description="Purpose and functionality of the workflow")
    version: str = Field("1.0.0", description="Version of the workflow definition")
    steps: List[WorkflowStep] = Field(..., description="Ordered list of workflow steps")
    max_iterations: int = Field(10, ge=1, description="Maximum number of iterations allowed")
    verbose: bool = Field(True, description="Enable verbose logging")
    enable_observability: bool = Field(
        True,
        description="Enable monitoring and observability for the workflow"
    )
    error_handling: Dict[str, Any] = Field(
        default_factory=lambda: {"strategy": "stop_on_error", "notify": True},
        description="Error handling configuration"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Execution Models
class ExecutionContext(BaseModel):
    """Context for workflow execution."""
    workflow_id: str = Field(..., description="ID of the workflow being executed")
    execution_id: str = Field(..., description="Unique identifier for this execution")
    input_data: Dict[str, Any] = Field(..., description="Input data for the workflow")
    state: Dict[str, Any] = Field(default_factory=dict, description="Execution state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When execution started")
    completed_at: Optional[datetime] = Field(None, description="When execution completed")
    status: Literal["pending", "running", "completed", "failed", "cancelled"] = "pending"
    created_by: Optional[str] = Field(None, description="User or system that initiated execution")
    priority: int = Field(0, description="Execution priority (higher = more urgent)")

class ExecutionResult(BaseModel):
    """Result of a workflow execution."""
    execution_id: str
    workflow_id: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    steps_completed: int
    total_steps: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Domain-Specific Schemas
# ======================

# HR Agent Schemas
class EmployeeStatus(str, Enum):
    """Employee status enumeration."""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"
    INACTIVE = "inactive"
    TERMINATED = "terminated"

class Employee(BaseModel):
    """Employee information model."""
    id: str = Field(..., description="Unique employee identifier")
    first_name: str
    last_name: str
    email: EmailStr
    department: str
    position: str
    manager_id: Optional[str] = None
    hire_date: date
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    skills: List[str] = Field(default_factory=list)
    performance_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LeaveRequest(BaseModel):
    """Employee leave request model."""
    id: str
    employee_id: str
    start_date: date
    end_date: date
    leave_type: str  # vacation, sick, personal, etc.
    status: Literal["pending", "approved", "rejected", "cancelled"] = "pending"
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Finance Agent Schemas
class TransactionType(str, Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class TransactionStatus(str, Enum):
    """Status of a financial transaction."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"

class Transaction(BaseModel):
    """Financial transaction model."""
    id: str
    type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    amount: float = Field(..., gt=0, description="Positive amount")
    currency: str = "USD"
    description: str
    category: str
    account_id: str
    reference_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Budget(BaseModel):
    """Budget allocation model."""
    id: str
    name: str
    description: str
    amount: float = Field(..., gt=0)
    spent: float = Field(0.0, ge=0)
    remaining: float = Field(0.0, ge=0)
    category: str
    start_date: date
    end_date: date
    owner_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Support Agent Schemas
class TicketPriority(str, Enum):
    """Support ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(str, Enum):
    """Support ticket statuses."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class TicketType(str, Enum):
    """Types of support tickets."""
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    QUESTION = "question"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"

class SupportTicket(BaseModel):
    """Customer support ticket model."""
    id: str
    subject: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    type: TicketType = TicketType.GENERAL
    customer_id: str
    assigned_agent_id: Optional[str] = None
    source: str = "web"  # web, email, chat, api
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SupportMessage(BaseModel):
    """Support conversation message model."""
    id: str
    ticket_id: str
    content: str
    sender_type: Literal["agent", "customer", "system"]
    sender_id: str
    is_internal: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Analytics Agent Schemas
class MetricType(str, Enum):
    """Types of analytics metrics."""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    UNIQUE = "unique"

class TimeGranularity(str, Enum):
    """Time granularity for time series data."""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class FilterOperator(str, Enum):
    """Operators for filtering analytics data."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN_OR_EQUAL = "lte"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"

class AnalyticsQuery(BaseModel):
    """Analytics query model."""
    metrics: List[str]
    dimensions: List[str] = Field(default_factory=list)
    filters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    time_range: Optional[Dict[str, Union[str, datetime]]] = None
    granularity: TimeGranularity = TimeGranularity.DAY
    limit: int = 1000
    offset: int = 0
    order_by: List[Dict[str, str]] = Field(default_factory=list)

class AnalyticsResult(BaseModel):
    """Analytics query result model."""
    data: List[Dict[str, Any]]
    metrics: List[str]
    dimensions: List[str]
    total: int
    limit: int
    offset: int
    query: Dict[str, Any]
    executed_at: datetime = Field(default_factory=datetime.utcnow)


# Integration Models
# =================

class IntegrationType(str, Enum):
    """Types of system integrations."""
    DATABASE = "database"
    MESSAGING = "messaging"
    STORAGE = "storage"
    AUTH = "authentication"
    PAYMENT = "payment"
    EMAIL = "email"
    CRM = "crm"
    ANALYTICS = "analytics"
    DOCUMENT = "document"
    API = "api"

class IntegrationStatus(str, Enum):
    """Integration connection status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    DISABLED = "disabled"

class IntegrationConfig(BaseModel):
    """Configuration for a system integration."""
    id: str
    name: str
    type: IntegrationType
    status: IntegrationStatus = IntegrationStatus.PENDING
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced_at: Optional[datetime] = None
    error: Optional[str] = None


# Event Schemas
# ============

class EventType(str, Enum):
    """Types of system events."""
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_updated"
    TRANSACTION_PROCESSED = "transaction_processed"
    BUDGET_ALERT = "budget_alert"
    EMPLOYEE_ONBOARDED = "employee_onboarded"
    LEAVE_REQUESTED = "leave_requested"
    REPORT_GENERATED = "report_generated"
    SYSTEM_ALERT = "system_alert"
    INTEGRATION_ERROR = "integration_error"
    WORKFLOW_COMPLETED = "workflow_completed"

class EventSeverity(str, Enum):
    """Severity levels for events."""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"

class Event(BaseModel):
    """System event model."""
    id: str
    type: EventType
    severity: EventSeverity = EventSeverity.INFO
    source: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# API Request/Response Models
# ==========================
class PaginationParams(BaseModel):
    """Pagination parameters for API requests."""
    page: int = Field(1, ge=1, description="Page number, 1-based")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Literal["asc", "desc"] = "desc"

class PaginatedResponse(BaseModel):
    """Standard paginated response format."""
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class ValidationErrorItem(BaseModel):
    """Validation error item details."""
    loc: List[Union[str, int]]
    msg: str
    type: str

class ValidationErrorResponse(ErrorResponse):
    """Validation error response format."""
    errors: List[ValidationErrorItem]


# Notification Models
# ==================
class NotificationType(str, Enum):
    """Types of notifications."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SLACK = "slack"
    WEBHOOK = "webhook"

class NotificationStatus(str, Enum):
    """Status of a notification."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    BOUNCED = "bounced"

class NotificationPriority(str, Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Notification(BaseModel):
    """Notification model."""
    id: str
    type: NotificationType
    status: NotificationStatus = NotificationStatus.PENDING
    priority: NotificationPriority = NotificationPriority.NORMAL
    subject: str
    message: str
    recipient: str
    sender: Optional[str] = None
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
