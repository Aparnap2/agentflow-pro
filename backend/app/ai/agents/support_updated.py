"""
Updated SupportAgent with comprehensive customer support capabilities.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date, timedelta
from enum import Enum
import logging
from pydantic import BaseModel, Field, validator, HttpUrl

from .base_agent import BaseAgent, AgentConfig, AgentResponse

logger = logging.getLogger(__name__)

class TicketStatus(str, Enum):
    """Status of a support ticket."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_TEAM = "waiting_team"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class TicketPriority(str, Enum):
    """Priority levels for support tickets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketType(str, Enum):
    """Types of support tickets."""
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    HOW_TO = "how_to"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"

class ChannelType(str, Enum):
    """Channels through which support tickets can be created."""
    EMAIL = "email"
    CHAT = "chat"
    PHONE = "phone"
    SELF_SERVICE = "self_service"
    SOCIAL = "social"
    API = "api"

class SatisfactionRating(int, Enum):
    """Customer satisfaction rating scale."""
    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5

class Ticket(BaseModel):
    """Support ticket model."""
    id: str
    subject: str
    description: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    type: TicketType = TicketType.GENERAL
    channel: ChannelType
    customer_id: str
    customer_name: str
    customer_email: str
    assigned_agent_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    first_response_time: Optional[timedelta] = None
    resolution_time: Optional[timedelta] = None
    satisfaction_rating: Optional[SatisfactionRating] = None
    metadata: Dict[str, Any] = {}

class Comment(BaseModel):
    """Ticket comment/update model."""
    id: str
    ticket_id: str
    author_id: str
    author_type: str  # 'agent', 'customer', 'system'
    content: str
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class KnowledgeBaseArticle(BaseModel):
    """Knowledge base article model."""
    id: str
    title: str
    content: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    status: str = "draft"  # draft, published, archived
    author_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    views: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    metadata: Dict[str, Any] = {}

class SupportAgent(BaseAgent):
    """
    Comprehensive Support Agent with customer support capabilities.
    
    This agent provides a complete suite of support functions including:
    - Ticket management and tracking
    - Customer communication
    - Knowledge base management
    - Customer satisfaction tracking
    - Support analytics
    - Self-service portal integration
    - Multi-channel support
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.tickets: Dict[str, Ticket] = {}
        self.comments: Dict[str, List[Comment]] = {}
        self.knowledge_base: Dict[str, KnowledgeBaseArticle] = {}
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.crm = get_crm_integration()
            self.communication = get_communication_integration()
            self.knowledge_base_system = get_knowledge_base_integration()
            self.analytics = get_analytics_integration()
            logger.info("Support Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Support Agent integrations: {str(e)}")
            raise
    
    # Ticket Management
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new support ticket.
        
        Args:
            ticket_data: Dictionary containing ticket details
                - subject: Ticket subject
                - description: Detailed description of the issue
                - customer_id: ID of the customer
                - customer_name: Name of the customer
                - customer_email: Email of the customer
                - channel: Channel through which ticket was created (from ChannelType enum)
                - priority: Priority level (from TicketPriority enum)
                - type: Type of ticket (from TicketType enum)
                - tags: List of tags
                - custom_fields: Any custom fields
                
        Returns:
            AgentResponse with created ticket or error
        """
        try:
            ticket = Ticket(**ticket_data)
            self.tickets[ticket.id] = ticket
            self.comments[ticket.id] = []
            
            # Create ticket in CRM
            await self.crm.create_ticket(ticket.dict())
            
            # Send acknowledgment to customer
            await self._send_acknowledgment(ticket)
            
            # Auto-assign if possible
            await self._auto_assign_ticket(ticket)
            
            logger.info(f"Created ticket: {ticket.subject} ({ticket.id})")
            
            return AgentResponse(
                success=True,
                output={"ticket": ticket.dict()},
                message=f"Created ticket: {ticket.subject}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create ticket: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _send_acknowledgment(self, ticket: Ticket) -> None:
        """Send acknowledgment to the customer that their ticket was received."""
        subject = f"Ticket #{ticket.id}: {ticket.subject}"
        
        body = f"""
        Dear {ticket.customer_name},
        
        Thank you for contacting {self.config.get('company_name', 'our support team')}.
        We have received your request and a ticket has been created for you.
        
        Ticket ID: {ticket.id}
        Subject: {ticket.subject}
        Status: {ticket.status.value.replace('_', ' ').title()}
        Priority: {ticket.priority.value.title()}
        
        A support agent will review your request and respond as soon as possible.
        
        You can view the status of your ticket or add comments at any time by visiting:
        {self.config.get('support_portal_url', '')}/tickets/{ticket.id}
        
        Best regards,
        {self.config.get('support_team_name', 'Customer Support Team')}
        """
        
        await self.communication.send_email(
            to=ticket.customer_email,
            subject=subject,
            body=body.strip()
        )
    
    async def _auto_assign_ticket(self, ticket: Ticket) -> None:
        """Automatically assign ticket based on rules and availability."""
        # In a real implementation, this would use assignment rules
        # and check agent availability/workload
        
        # For now, just log that we would assign it
        logger.info(f"Would auto-assign ticket {ticket.id} based on rules")
    
    async def add_comment(self, ticket_id: str, comment_data: Dict[str, Any]) -> AgentResponse:
        """
        Add a comment to a ticket.
        
        Args:
            ticket_id: ID of the ticket
            comment_data: Dictionary containing comment details
                - author_id: ID of the comment author
                - author_type: Type of author ('agent', 'customer', 'system')
                - content: Comment content
                - is_public: Whether the comment is visible to the customer
                
        Returns:
            AgentResponse with added comment or error
        """
        try:
            if ticket_id not in self.tickets:
                raise ValueError(f"Ticket {ticket_id} not found")
                
            comment = Comment(ticket_id=ticket_id, **comment_data)
            
            if ticket_id not in self.comments:
                self.comments[ticket_id] = []
            self.comments[ticket_id].append(comment)
            
            # Update ticket's updated_at timestamp
            ticket = self.tickets[ticket_id]
            ticket.updated_at = datetime.utcnow()
            
            # If this is the first agent response, record first response time
            if (comment.author_type == 'agent' and 
                not ticket.first_response_time and 
                ticket.status != TicketStatus.RESOLVED):
                ticket.first_response_time = comment.created_at - ticket.created_at
                
                # Update status if it was just opened
                if ticket.status == TicketStatus.OPEN:
                    ticket.status = TicketStatus.IN_PROGRESS
            
            # Notify relevant parties about the new comment
            await self._notify_new_comment(ticket, comment)
            
            logger.info(f"Added comment to ticket {ticket_id}")
            
            return AgentResponse(
                success=True,
                output={"comment": comment.dict()},
                message="Comment added successfully"
            )
            
        except Exception as e:
            error_msg = f"Failed to add comment: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_new_comment(self, ticket: Ticket, comment: Comment) -> None:
        """Notify relevant parties about a new comment on a ticket."""
        # Don't notify about system comments or private notes
        if comment.author_type == 'system' or not comment.is_public:
            return
            
        # Determine who to notify
        recipients = set()
        
        # Always notify the customer if the comment is from an agent
        if comment.author_type == 'agent':
            recipients.add((ticket.customer_email, ticket.customer_name))
        
        # Notify assigned agent if the comment is from the customer
        elif comment.author_type == 'customer' and ticket.assigned_agent_id:
            # In a real app, we'd look up the agent's email
            agent_email = f"agent-{ticket.assigned_agent_id}@example.com"
            recipients.add((agent_email, f"Agent {ticket.assigned_agent_id}"))
        
        # Prepare notification
        subject = f"New update on ticket #{ticket.id}: {ticket.subject}"
        
        for email, name in recipients:
            greeting = f"Hi {name}," if name else "Hello,"
            
            body = f"""
            {greeting}
            
            There's a new update on ticket #{ticket.id}:
            
            {comment.content}
            
            You can view and respond to this ticket by visiting:
            {self.config.get('support_portal_url', '')}/tickets/{ticket.id}
            
            Best regards,
            {self.config.get('support_team_name', 'Customer Support Team')}
            """
            
            await self.communication.send_email(
                to=email,
                subject=subject,
                body=body.strip()
            )
    
    async def update_ticket_status(self, ticket_id: str, status: TicketStatus, 
                                 comment: Optional[str] = None, agent_id: Optional[str] = None) -> AgentResponse:
        """
        Update the status of a ticket.
        
        Args:
            ticket_id: ID of the ticket
            status: New status (from TicketStatus enum)
            comment: Optional comment about the status change
            agent_id: ID of the agent making the change
            
        Returns:
            AgentResponse with update status or error
        """
        try:
            if ticket_id not in self.tickets:
                raise ValueError(f"Ticket {ticket_id} not found")
                
            ticket = self.tickets[ticket_id]
            previous_status = ticket.status
            ticket.status = status
            ticket.updated_at = datetime.utcnow()
            
            # Update timestamps for resolution/closure
            if status == TicketStatus.RESOLVED and not ticket.resolved_at:
                ticket.resolved_at = datetime.utcnow()
                ticket.resolution_time = ticket.resolved_at - ticket.created_at
            elif status == TicketStatus.CLOSED and not ticket.closed_at:
                ticket.closed_at = datetime.utcnow()
                if not ticket.resolved_at:
                    ticket.resolved_at = ticket.closed_at
                    ticket.resolution_time = ticket.resolved_at - ticket.created_at
            
            # Add a system comment about the status change
            if agent_id:
                status_comment = f"Status changed from {previous_status} to {status}"
                if comment:
                    status_comment += f": {comment}"
                    
                await self.add_comment(
                    ticket_id=ticket_id,
                    comment_data={
                        "author_id": agent_id,
                        "author_type": "agent",
                        "content": status_comment,
                        "is_public": True
                    }
                )
            
            # Notify customer if ticket is resolved/closed
            if status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
                await self._notify_ticket_resolution(ticket, comment)
            
            logger.info(f"Updated ticket {ticket_id} status from {previous_status} to {status}")
            
            return AgentResponse(
                success=True,
                output={"ticket": ticket.dict()},
                message=f"Updated ticket status to {status}"
            )
            
        except Exception as e:
            error_msg = f"Failed to update ticket status: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_ticket_resolution(self, ticket: Ticket, resolution_notes: Optional[str] = None) -> None:
        """Notify customer that their ticket has been resolved/closed."""
        subject = f"Ticket #{ticket.id} has been {ticket.status}"
        
        body = f"""
        Dear {ticket.customer_name},
        
        We're writing to inform you that your ticket has been marked as {ticket.status}.
        
        Ticket ID: {ticket.id}
        Subject: {ticket.subject}
        Status: {ticket.status}
        """
        
        if resolution_notes:
            body += f"\nResolution Notes:\n{resolution_notes}\n"
        
        body += f"""
        If you have any further questions or if your issue hasn't been fully resolved, 
        please don't hesitate to reply to this email or update the ticket at:
        {self.config.get('support_portal_url', '')}/tickets/{ticket.id}
        
        We value your feedback! Please take a moment to rate your support experience:
        {self.config.get('feedback_url', '')}/ticket/{ticket.id}
        
        Best regards,
        {self.config.get('support_team_name', 'Customer Support Team')}
        """
        
        await self.communication.send_email(
            to=ticket.customer_email,
            subject=subject,
            body=body.strip()
        )
    
    # Knowledge Base Management
    async def create_knowledge_base_article(self, article_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new knowledge base article.
        
        Args:
            article_data: Dictionary containing article details
                - title: Article title
                - content: Article content (HTML or Markdown)
                - category: Article category
                - subcategory: Optional subcategory
                - tags: List of tags
                - author_id: ID of the author
                - status: Article status ('draft' or 'published')
                
        Returns:
            AgentResponse with created article or error
        """
        try:
            article = KnowledgeBaseArticle(**article_data)
            self.knowledge_base[article.id] = article
            
            # Index in search system
            await self.knowledge_base_system.index_article(article.dict())
            
            logger.info(f"Created knowledge base article: {article.title} ({article.id})")
            
            return AgentResponse(
                success=True,
                output={"article": article.dict()},
                message=f"Created article: {article.title}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create knowledge base article: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def search_knowledge_base(self, query: str, filters: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Search the knowledge base for articles.
        
        Args:
            query: Search query string
            filters: Optional filters (category, tags, status, etc.)
            
        Returns:
            AgentResponse with search results or error
        """
        try:
            # In a real implementation, this would use a search engine
            # This is a simplified version that just filters on title/content
            results = []
            query = query.lower()
            
            for article in self.knowledge_base.values():
                # Skip if status filter is provided and doesn't match
                if filters and 'status' in filters and article.status != filters['status']:
                    continue
                    
                # Skip if category filter is provided and doesn't match
                if filters and 'category' in filters and article.category != filters['category']:
                    continue
                    
                # Skip if tags filter is provided and no matching tags
                if filters and 'tags' in filters and not any(tag in article.tags for tag in filters['tags']):
                    continue
                    
                # Simple text search in title and content
                if (query in article.title.lower() or 
                    query in article.content.lower()):
                    results.append(article.dict())
            
            return AgentResponse(
                success=True,
                output={
                    "query": query,
                    "filters": filters or {},
                    "results": results,
                    "count": len(results)
                },
                message=f"Found {len(results)} articles matching your search"
            )
            
        except Exception as e:
            error_msg = f"Failed to search knowledge base: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    # Customer Satisfaction
    async def record_customer_satisfaction(self, ticket_id: str, rating: SatisfactionRating, 
                                         comment: Optional[str] = None) -> AgentResponse:
        """
        Record customer satisfaction for a ticket.
        
        Args:
            ticket_id: ID of the ticket
            rating: Satisfaction rating (1-5)
            comment: Optional comment from the customer
            
        Returns:
            AgentResponse with recorded satisfaction data or error
        """
        try:
            if ticket_id not in self.tickets:
                raise ValueError(f"Ticket {ticket_id} not found")
                
            ticket = self.tickets[ticket_id]
            ticket.satisfaction_rating = rating
            
            # Add a comment with the rating
            if comment:
                await self.add_comment(
                    ticket_id=ticket_id,
                    comment_data={
                        "author_id": ticket.customer_id,
                        "author_type": "customer",
                        "content": f"Customer satisfaction rating: {rating}/5\n\n{comment}",
                        "is_public": False  # Keep internal by default
                    }
                )
            
            # Log the satisfaction data
            logger.info(f"Recorded satisfaction rating {rating} for ticket {ticket_id}")
            
            # In a real implementation, you might want to trigger alerts for low ratings
            if rating <= SatisfactionRating.DISSATISFIED:
                await self._handle_low_satisfaction(ticket, rating, comment)
            
            return AgentResponse(
                success=True,
                output={
                    "ticket_id": ticket_id,
                    "rating": rating,
                    "comment": comment
                },
                message="Thank you for your feedback!"
            )
            
        except Exception as e:
            error_msg = f"Failed to record customer satisfaction: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _handle_low_satisfaction(self, ticket: Ticket, rating: SatisfactionRating, 
                                     comment: Optional[str] = None) -> None:
        """Handle low satisfaction ratings by notifying supervisors."""
        # In a real implementation, this would notify supervisors or managers
        # about the low satisfaction rating for follow-up
        
        subject = f"Low Satisfaction Rating for Ticket #{ticket.id}"
        
        body = f"""
        A customer has provided a low satisfaction rating for a support ticket.
        
        Ticket Details:
        - ID: {ticket.id}
        - Subject: {ticket.subject}
        - Assigned Agent: {ticket.assigned_agent_id or 'Unassigned'}
        - Rating: {rating}/5
        - Comment: {comment or 'No comment provided'}
        
        Ticket URL: {self.config.get('admin_portal_url', '')}/tickets/{ticket.id}
        
        Please follow up with the customer and take appropriate action.
        """
        
        # In a real app, this would be sent to the appropriate manager/supervisor
        await self.communication.send_email(
            to=f"support-manager@{self.config.get('company_domain', 'example.com')}",
            subject=subject,
            body=body.strip()
        )

# Mock integration functions
def get_crm_integration():
    class MockCRMIntegration:
        async def create_ticket(self, ticket_data):
            logger.info(f"[MockCRM] Creating ticket: {ticket_data['subject']}")
            return {"status": "success", "ticket_id": ticket_data['id']}
            
        async def update_ticket(self, ticket_id, updates):
            logger.info(f"[MockCRM] Updating ticket {ticket_id}: {updates}")
            return {"status": "success"}
            
    return MockCRMIntegration()

def get_knowledge_base_integration():
    class MockKBIntegration:
        async def index_article(self, article_data):
            logger.info(f"[MockKB] Indexing article: {article_data['title']}")
            return {"status": "success"}
            
        async def search_articles(self, query, filters=None):
            logger.info(f"[MockKB] Searching for: {query}")
            return {"status": "success", "results": []}
            
    return MockKBIntegration()

# Update the __init__.py to expose the new SupportAgent
__all__ = [
    'SupportAgent',
    'Ticket',
    'Comment',
    'KnowledgeBaseArticle',
    'TicketStatus',
    'TicketPriority',
    'TicketType',
    'ChannelType',
    'SatisfactionRating'
]
