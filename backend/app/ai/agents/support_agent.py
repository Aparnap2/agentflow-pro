"""
Customer Support Agent Module

This module implements an AI-powered Customer Support Agent capable of handling
a wide range of customer service tasks including ticket management, live chat support,
knowledge base management, and customer satisfaction analysis.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
from datetime import datetime, timedelta
import logging
import json
import asyncio
from pydantic import BaseModel, Field, validator, HttpUrl
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_agent import BaseAgent, AgentConfig, AgentResponse
from ..integrations.crm_integration import CRMIntegration
from ..integrations.chat_integration import ChatIntegration
from ..integrations.knowledge_base import KnowledgeBaseIntegration
from ..integrations.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

class TicketPriority(str, Enum):
    """Priority levels for support tickets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(str, Enum):
    """Status of a support ticket."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"

class TicketSource(str, Enum):
    """Source of the support ticket."""
    EMAIL = "email"
    PHONE = "phone"
    CHAT = "chat"
    SELF_SERVICE = "self_service"
    SOCIAL_MEDIA = "social_media"
    API = "api"

class SupportChannel(str, Enum):
    """Available support channels."""
    EMAIL = "email"
    LIVE_CHAT = "live_chat"
    PHONE = "phone"
    SOCIAL_MEDIA = "social_media"
    SELF_SERVICE = "self_service"
    IN_PERSON = "in_person"

class CustomerFeedback(BaseModel):
    """Customer feedback model."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comments: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SupportTicket(BaseModel):
    """Support ticket model."""
    id: str
    subject: str
    description: str
    customer_id: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    source: TicketSource
    assigned_agent_id: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    first_response_time: Optional[timedelta] = None
    resolution_time: Optional[timedelta] = None
    customer_satisfaction: Optional[CustomerFeedback] = None
    internal_notes: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_note(self, note: str, agent_id: str, is_internal: bool = True) -> None:
        """Add a note to the ticket."""
        self.internal_notes.append({
            'note': note,
            'agent_id': agent_id,
            'timestamp': datetime.utcnow(),
            'is_internal': is_internal
        })
        self.updated_at = datetime.utcnow()

class SupportAgent(BaseAgent):
    """
    Advanced Customer Support Agent specialized in providing exceptional customer service.
    
    This agent provides comprehensive support capabilities including:
    - Multi-channel ticket management
    - Live chat and email support
    - Knowledge base management
    - Customer satisfaction analysis
    - Automated responses and chatbots
    - Escalation management
    - Customer feedback collection and analysis
    - Support metrics and reporting
    - Self-service portal management
    - Customer success management
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.tickets: Dict[str, SupportTicket] = {}
        self.knowledge_base = KnowledgeBaseIntegration()
        self.sentiment_analyzer = SentimentAnalyzer()
        self._init_support_integrations()
    
    def _init_support_integrations(self) -> None:
        """Initialize support-related integrations."""
        try:
            self.crm = CRMIntegration(
                api_key=settings.CRM_API_KEY,
                base_url=settings.CRM_BASE_URL
            )
            
            self.chat = ChatIntegration(
                platform=settings.CHAT_PLATFORM,
                api_key=settings.CHAT_API_KEY
            )
            
            logger.info("Support integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize support integrations: {str(e)}")
            raise
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new support ticket.
        
        Args:
            ticket_data: Dictionary containing ticket details
                - subject: Ticket subject
                - description: Detailed description
                - customer_id: ID of the customer
                - source: Source of the ticket (email, chat, etc.)
                - priority: Priority level (low, medium, high, urgent)
                - category: Optional category
                - tags: Optional list of tags
                
        Returns:
            AgentResponse with created ticket details
        """
        try:
            # Generate a unique ticket ID
            ticket_id = f"TKT-{len(self.tickets) + 1:06d}"
            
            # Create the ticket
            ticket = SupportTicket(
                id=ticket_id,
                **ticket_data
            )
            
            # Store the ticket
            self.tickets[ticket_id] = ticket
            
            # Auto-assign if needed
            if not ticket.assigned_agent_id:
                ticket.assigned_agent_id = await self._auto_assign_agent(ticket)
            
            # Send acknowledgment if needed
            if ticket.source in [TicketSource.EMAIL, TicketSource.SELF_SERVICE]:
                await self._send_acknowledgment(ticket)
            
            return AgentResponse(
                success=True,
                output={
                    "ticket_id": ticket_id,
                    "status": ticket.status.value,
                    "assigned_agent_id": ticket.assigned_agent_id,
                    "next_steps": [
                        f"Review ticket details: {ticket_id}",
                        "Gather additional information if needed",
                        "Prepare initial response"
                    ]
                },
                metadata={
                    "created_at": ticket.created_at.isoformat(),
                    "customer_id": ticket.customer_id,
                    "priority": ticket.priority.value
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create ticket: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Ticket creation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"customer_id": ticket_data.get('customer_id', 'unknown')}
            )
    
    async def respond_to_ticket(self, ticket_id: str, response_data: Dict[str, Any]) -> AgentResponse:
        """
        Respond to a support ticket.
        
        Args:
            ticket_id: ID of the ticket to respond to
            response_data: Dictionary containing response details
                - message: Response content
                - agent_id: ID of the responding agent
                - is_internal: Whether the response is internal
                - close_ticket: Whether to close the ticket after response
                
        Returns:
            AgentResponse with response status
        """
        try:
            if ticket_id not in self.tickets:
                raise ValueError(f"Ticket {ticket_id} not found")
            
            ticket = self.tickets[ticket_id]
            agent_id = response_data['agent_id']
            
            # Add response to ticket
            ticket.add_note(
                note=response_data['message'],
                agent_id=agent_id,
                is_internal=response_data.get('is_internal', False)
            )
            
            # Update ticket status
            if response_data.get('close_ticket', False):
                ticket.status = TicketStatus.RESOLVED
                ticket.resolved_at = datetime.utcnow()
                if ticket.created_at:
                    ticket.resolution_time = ticket.resolved_at - ticket.created_at
            else:
                ticket.status = TicketStatus.IN_PROGRESS
            
            # Send response to customer if not internal
            if not response_data.get('is_internal', False):
                await self._send_response(ticket, response_data['message'])
            
            return AgentResponse(
                success=True,
                output={
                    "ticket_id": ticket_id,
                    "status": ticket.status.value,
                    "response_sent": not response_data.get('is_internal', False),
                    "next_steps": [
                        "Follow up if no response from customer" if not response_data.get('close_ticket') else "Complete any post-resolution tasks"
                    ]
                },
                metadata={
                    "updated_at": ticket.updated_at.isoformat(),
                    "agent_id": agent_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to respond to ticket {ticket_id}: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Failed to respond to ticket: {str(e)}",
                error_type=type(e).__name__,
                metadata={"ticket_id": ticket_id}
            )
    
    async def analyze_customer_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze customer sentiment from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        return await self.sentiment_analyzer.analyze(text)
    
    async def search_knowledge_base(self, query: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant articles.
        
        Args:
            query: Search query
            top_n: Number of results to return
            
        Returns:
            List of relevant knowledge base articles
        """
        return await self.knowledge_base.search(query, top_n=top_n)
    
    async def generate_response(self, ticket_id: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a response for a support ticket using AI.
        
        Args:
            ticket_id: ID of the ticket
            context: Additional context for response generation
            
        Returns:
            Generated response text
        """
        if ticket_id not in self.tickets:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        ticket = self.tickets[ticket_id]
        
        # Build prompt for the LLM
        prompt = f"""
        You are a customer support agent. Generate a helpful and professional response 
        to the following customer inquiry.
        
        Ticket ID: {ticket_id}
        Subject: {ticket.subject}
        Customer ID: {ticket.customer_id}
        Priority: {ticket.priority.value.upper()}
        
        Customer's message:
        {ticket.description}
        
        Additional context: {context or 'No additional context provided'}
        
        Generate a response that:
        1. Acknowledges the customer's issue
        2. Shows empathy and understanding
        3. Provides a clear solution or next steps
        4. Sets appropriate expectations
        5. Closes professionally
        """
        
        # Call the LLM to generate response
        response = await self.llm.generate(prompt)
        return response.strip()
    
    async def _auto_assign_agent(self, ticket: SupportTicket) -> str:
        """
        Automatically assign an agent to a ticket based on workload and skills.
        
        Args:
            ticket: Ticket to assign
            
        Returns:
            ID of the assigned agent
        """
        # In a real implementation, this would query the agent database
        # and use a more sophisticated assignment algorithm
        return "agent_1"  # Simplified for example
    
    async def _send_acknowledgment(self, ticket: SupportTicket) -> None:
        """
        Send an acknowledgment to the customer.
        
        Args:
            ticket: Ticket to acknowledge
        """
        # In a real implementation, this would send an email or notification
        logger.info(f"Sent acknowledgment for ticket {ticket.id} to customer {ticket.customer_id}")
    
    async def _send_response(self, ticket: SupportTicket, message: str) -> None:
        """
        Send a response to the customer.
        
        Args:
            ticket: Ticket being responded to
            message: Response message
        """
        # In a real implementation, this would send the response via the appropriate channel
        logger.info(f"Sent response for ticket {ticket.id} to customer {ticket.customer_id}")
        logger.debug(f"Response content: {message}")

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        # Initialize the support agent
        config = AgentConfig(
            name="SupportAgent",
            description="Handles customer support tickets and inquiries"
        )
        agent = SupportAgent(config)
        
        # Create a test ticket
        ticket_data = {
            "subject": "Login issues",
            "description": "I can't log into my account. It says invalid credentials but I'm sure my password is correct.",
            "customer_id": "cust_12345",
            "source": TicketSource.EMAIL,
            "priority": TicketPriority.HIGH,
            "category": "Account Access"
        }
        
        # Create the ticket
        result = await agent.create_ticket(ticket_data)
        print(f"Created ticket: {json.dumps(result.dict(), indent=2, default=str)}")
        
        # Generate a response
        if result.success:
            ticket_id = result.output["ticket_id"]
            response = await agent.generate_response(ticket_id)
            print(f"\nGenerated response:\n{response}")
            
            # Send the response
            response_result = await agent.respond_to_ticket(
                ticket_id=ticket_id,
                response_data={
                    "message": response,
                    "agent_id": "system_1",
                    "is_internal": False,
                    "close_ticket": False
                }
            )
            print(f"\nResponse sent: {response_result.success}")
    
    asyncio.run(main())
