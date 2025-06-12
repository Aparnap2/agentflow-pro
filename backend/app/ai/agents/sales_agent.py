from typing import Dict, Any, List, Optional, Union, Type, TypeVar, Callable, Tuple
from enum import Enum, auto
import json
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import aiohttp
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, validator, HttpUrl, conlist, condecimal, conint
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_agent import BaseAgent, AgentConfig, AgentResponse, AgentState
from ..integrations.crm_integration import CRMIntegration
from ..integrations.email_integration import EmailIntegration
from ..integrations.calendar_integration import CalendarIntegration
from ..integrations.document_integration import DocumentIntegration
from ..integrations.payment_processor import PaymentProcessorIntegration
from ..tools.sales_tools import (
    calculate_roi,
    analyze_sales_performance,
    generate_forecast,
    create_commission_structure,
    analyze_competitors
)

logger = logging.getLogger(__name__)

# Type aliases
T = TypeVar('T')
Percentage = conint(ge=0, le=100)

class Contact(BaseModel):
    """Contact information for leads and customers."""
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = None
    company: str
    linkedin_url: Optional[HttpUrl] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Opportunity(BaseModel):
    """Sales opportunity with associated details."""
    id: str
    name: str
    description: str
    amount: condecimal(gt=0)
    currency: str = "USD"
    probability: int = Field(ge=0, le=100)
    stage: OpportunityStage = OpportunityStage.DISCOVERY
    close_date: Optional[datetime] = None
    account_id: str
    owner_id: str
    contacts: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    last_contact: Optional[datetime] = None
    next_steps: List[Dict[str, Any]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Account(BaseModel):
    """Company or organization being sold to."""
    id: str
    name: str
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    billing_address: Optional[Dict[str, str]] = None
    shipping_address: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    contacts: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityType(str, Enum):
    """Types of sales activities."""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    DEMO = "demo"
    PROPOSAL = "proposal"
    FOLLOW_UP = "follow_up"
    TASK = "task"
    OTHER = "other"

class Activity(BaseModel):
    """Record of a sales activity."""
    id: str
    type: ActivityType
    subject: str
    description: Optional[str] = None
    due_date: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    related_to: Optional[Dict[str, str]] = None  # e.g., {"type": "opportunity", "id": "123"}
    participants: List[Dict[str, str]] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LeadStatus(str, Enum):
    """Status of a sales lead in the pipeline."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NURTURING = "nurturing"

class OpportunityStage(str, Enum):
    """Stages of a sales opportunity."""
    DISCOVERY = "discovery"
    DEMONSTRATION = "demonstration"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class CommunicationChannel(str, Enum):
    """Channels for sales communication."""
    EMAIL = "email"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    SOCIAL_MEDIA = "social_media"
    CHAT = "chat"

class LeadSource(str, Enum):
    """Sources of sales leads."""
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    NETWORKING = "networking"
    SOCIAL_MEDIA = "social_media"
    PAID_ADS = "paid_ads"
    EVENTS = "events"
    PARTNERSHIPS = "partnerships"
    INBOUND_CALL = "inbound_call"
    OTHER = "other"

class LeadScore(BaseModel):
    """Scoring model for lead qualification."""
    budget: int = Field(ge=0, le=10, description="Budget availability score")
    authority: int = Field(ge=0, le=10, description="Decision-making authority score")
    need: int = Field(ge=0, le=10, description="Need/pain point score")
    timeline: int = Field(ge=0, le=10, description="Purchase timeline score")
    fit: int = Field(ge=0, le=10, description="Product/service fit score")
    engagement: int = Field(ge=0, le=10, description="Engagement level score")
    
    @property
    def total_score(self) -> int:
        """Calculate total lead score."""
        return sum([
            self.budget,
            self.authority,
            self.need,
            self.timeline,
            self.fit,
            self.engagement
        ])
    
    @property
    def qualification_status(self) -> str:
        """Determine qualification status based on score."""
        score = self.total_score
        if score >= 45:
            return "Hot Lead"
        elif score >= 30:
            return "Warm Lead"
        else:
            return "Cold Lead"

class SalesAgent(BaseAgent):
    """
    Advanced Sales Agent specialized in B2B and B2C sales processes.
    
    This agent provides comprehensive sales capabilities including:
    - Lead generation and qualification
    - Opportunity management
    - Sales pipeline management
    - Customer relationship management
    - Sales forecasting
    - Proposal generation
    - Contract management
    - Sales performance analytics
    - Customer success management
    - Cross-selling and upselling
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.accounts: Dict[str, Account] = {}
        self.contacts: Dict[str, Contact] = {}
        self.opportunities: Dict[str, Opportunity] = {}
        self.activities: Dict[str, Activity] = {}
        self._init_sales_integrations()
    
    def _init_sales_integrations(self) -> None:
        """Initialize sales-related integrations."""
        try:
            self.crm = CRMIntegration(
                api_key=settings.CRM_API_KEY,
                base_url=settings.CRM_BASE_URL
            )
            
            self.email = EmailIntegration(
                smtp_server=settings.EMAIL_SMTP_SERVER,
                smtp_port=settings.EMAIL_SMTP_PORT,
                username=settings.EMAIL_USERNAME,
                password=settings.EMAIL_PASSWORD
            )
            
            self.calendar = CalendarIntegration(
                provider=settings.CALENDAR_PROVIDER,
                credentials=settings.CALENDAR_CREDENTIALS
            )
            
            self.document = DocumentIntegration(
                provider=settings.DOCUMENT_PROVIDER,
                api_key=settings.DOCUMENT_API_KEY
            )
            
            self.payment = PaymentProcessorIntegration(
                provider=settings.PAYMENT_PROVIDER,
                api_key=settings.PAYMENT_API_KEY
            )
            
            logger.info("Sales integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize sales integrations: {str(e)}")
            raise
    
    async def qualify_lead(self, lead_data: Dict[str, Any]) -> AgentResponse:
        """
        Qualify a sales lead using a comprehensive scoring model.
        
        Args:
            lead_data: Dictionary containing lead information including:
                - contact: Contact information
                - company: Company information
                - budget: Budget details
                - needs: List of needs/pain points
                - timeline: Purchase timeline
                - engagement: Previous engagement history
        
        Returns:
            AgentResponse with lead qualification details
        """
        try:
            # Generate lead score using AI
            score_prompt = f"""
            Analyze the following lead information and provide a qualification score (1-10) for each category:
            
            Lead Information:
            {json.dumps(lead_data, indent=2, default=str)}
            
            Categories to score (1-10):
            1. Budget: Does the lead have budget for our solution?
            2. Authority: Is the lead a decision maker or influencer?
            3. Need: How strong is their need/pain point?
            4. Timeline: How soon are they looking to make a decision?
            5. Fit: How well does our solution match their needs?
            6. Engagement: How engaged has the lead been in conversations?
            
            Respond with a JSON object containing the scores and a brief explanation for each.
            """
            
            score_response = await self.llm.generate(score_prompt)
            scores = json.loads(score_response)
            
            # Create LeadScore object
            lead_score = LeadScore(
                budget=scores.get('budget_score', 0),
                authority=scores.get('authority_score', 0),
                need=scores.get('need_score', 0),
                timeline=scores.get('timeline_score', 0),
                fit=scores.get('fit_score', 0),
                engagement=scores.get('engagement_score', 0)
            )
            
            # Generate qualification summary
            summary_prompt = f"""
            Based on the following lead information and scores, provide a qualification summary:
            
            Lead Information:
            {json.dumps(lead_data, indent=2, default=str)}
            
            Scores:
            {json.dumps(lead_score.dict(), indent=2)}
            
            Total Score: {lead_score.total_score}/60
            Qualification: {lead_score.qualification_status}
            
            Provide a detailed summary of why this lead is qualified or not, 
            key opportunities, potential challenges, and recommended next steps.
            """
            
            summary = await self.llm.generate(summary_prompt)
            
            return AgentResponse(
                success=True,
                output={
                    "qualification_summary": summary,
                    "scores": lead_score.dict(),
                    "total_score": lead_score.total_score,
                    "qualification_status": lead_score.qualification_status,
                    "recommendations": [
                        "Schedule discovery call" if lead_score.total_score >= 30 else "Add to nurturing sequence",
                        "Assess competitor presence",
                        "Identify key stakeholders"
                    ]
                },
                metadata={
                    "lead_source": lead_data.get('source', 'unknown'),
                    "company": lead_data.get('company', {}).get('name', 'unknown'),
                    "scored_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Lead qualification failed: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Lead qualification failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"lead_email": lead_data.get('contact', {}).get('email', 'unknown')}
            )
    
    async def create_opportunity(self, opportunity_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new sales opportunity.
        
        Args:
            opportunity_data: Dictionary containing opportunity details including:
                - name: Opportunity name
                - description: Detailed description
                - amount: Expected deal value
                - account_id: Related account ID
                - owner_id: Sales rep ID
                - stage: Current stage (defaults to Discovery)
                - close_date: Expected close date
                - probability: Win probability (0-100)
        
        Returns:
            AgentResponse with created opportunity details
        """
        try:
            # Generate a unique opportunity ID
            opp_id = f"opp_{len(self.opportunities) + 1}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Create the opportunity
            opportunity = Opportunity(
                id=opp_id,
                name=opportunity_data['name'],
                description=opportunity_data.get('description', ''),
                amount=opportunity_data['amount'],
                account_id=opportunity_data['account_id'],
                owner_id=opportunity_data['owner_id'],
                stage=OpportunityStage(opportunity_data.get('stage', 'discovery')),
                close_date=datetime.fromisoformat(opportunity_data['close_date']) if 'close_date' in opportunity_data else None,
                probability=opportunity_data.get('probability', 0)
            )
            
            # Store the opportunity
            self.opportunities[opp_id] = opportunity
            
            # Link to account if it exists
            if opportunity.account_id in self.accounts:
                self.accounts[opportunity.account_id].opportunities.append(opp_id)
            
            # Create initial activities
            discovery_activity = Activity(
                id=f"act_{len(self.activities) + 1}",
                type=ActivityType.MEETING,
                subject=f"Discovery Call: {opportunity.name}",
                description=f"Initial discovery call to understand {opportunity.name} requirements.",
                due_date=datetime.utcnow() + timedelta(days=1),
                related_to={"type": "opportunity", "id": opp_id}
            )
            self.activities[discovery_activity.id] = discovery_activity
            
            return AgentResponse(
                success=True,
                output={
                    "opportunity_id": opp_id,
                    "status": "created",
                    "next_steps": [
                        f"Schedule discovery call: {discovery_activity.id}",
                        "Identify key stakeholders",
                        "Research account background"
                    ]
                },
                metadata={
                    "opportunity_name": opportunity.name,
                    "amount": float(opportunity.amount),
                    "stage": opportunity.stage.value,
                    "created_at": opportunity.created_at.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create opportunity: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Opportunity creation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"opportunity_name": opportunity_data.get('name', 'unknown')}
            )
    
    async def generate_proposal(self, opportunity_id: str, template_id: Optional[str] = None) -> AgentResponse:
        """
        Generate a sales proposal for an opportunity.
        
        Args:
            opportunity_id: ID of the opportunity
            template_id: Optional ID of a proposal template to use
            
        Returns:
            AgentResponse with generated proposal
        """
        try:
            if opportunity_id not in self.opportunities:
                raise ValueError(f"Opportunity {opportunity_id} not found")
            
            opportunity = self.opportunities[opportunity_id]
            
            # Get account information
            account = None
            if opportunity.account_id in self.accounts:
                account = self.accounts[opportunity.account_id]
            
            # Generate proposal content using AI
            prompt = f"""
            Create a comprehensive sales proposal with the following details:
            
            Opportunity:
            - Name: {opportunity.name}
            - Description: {opportunity.description}
            - Amount: {opportunity.amount} {opportunity.currency}
            
            Account: {account.name if account else 'N/A'}
            Industry: {account.industry if account and account.industry else 'N/A'}
            
            Create a professional proposal that includes:
            1. Executive Summary
            2. Understanding of Client Needs
            3. Proposed Solution
            4. Implementation Plan
            5. Pricing and Payment Terms
            6. Terms and Conditions
            7. Next Steps
            
            Make the proposal compelling and tailored to the client's industry and needs.
            """
            
            proposal_content = await self.llm.generate(prompt)
            
            # Format as a document
            proposal_doc = {
                "title": f"Proposal: {opportunity.name}",
                "content": proposal_content,
                "sections": [
                    "Executive Summary",
                    "Understanding Your Needs",
                    "Proposed Solution",
                    "Implementation Plan",
                    "Pricing and Payment Terms",
                    "Terms and Conditions",
                    "Next Steps"
                ],
                "metadata": {
                    "opportunity_id": opportunity_id,
                    "account_id": opportunity.account_id,
                    "amount": float(opportunity.amount),
                    "currency": opportunity.currency,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
            # Save the proposal
            proposal_id = f"prop_{len(self.opportunities)}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Create a document in the document management system
            doc_response = await self.document.create_document(
                title=proposal_doc["title"],
                content=proposal_doc,
                folder_id="proposals"
            )
            
            # Log the proposal generation
            proposal_activity = Activity(
                id=f"act_{len(self.activities) + 1}",
                type=ActivityType.PROPOSAL,
                subject=f"Proposal Generated: {opportunity.name}",
                description=f"Generated proposal for opportunity {opportunity_id}",
                due_date=datetime.utcnow(),
                completed=True,
                completed_at=datetime.utcnow(),
                related_to={"type": "opportunity", "id": opportunity_id},
                custom_fields={"proposal_id": proposal_id, "document_id": doc_response.get('id')}
            )
            self.activities[proposal_activity.id] = proposal_activity
            
            return AgentResponse(
                success=True,
                output={
                    "proposal_id": proposal_id,
                    "document_id": doc_response.get('id'),
                    "title": proposal_doc["title"],
                    "preview": proposal_content[:500] + "..." if len(proposal_content) > 500 else proposal_content,
                    "next_steps": [
                        "Review proposal",
                        "Schedule proposal presentation",
                        "Prepare for Q&A session"
                    ]
                },
                metadata={
                    "opportunity_name": opportunity.name,
                    "account_name": account.name if account else "",
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate proposal: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Proposal generation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"opportunity_id": opportunity_id}
            )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_external_api(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Helper method to make API calls with retry logic."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    headers={"Authorization": f"Bearer {self.config.api_key}"}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"API call to {endpoint} failed: {str(e)}")
            raise
    
    async def analyze_sales_performance(self, time_period: str = "last_quarter") -> AgentResponse:
        """
        Analyze sales performance metrics.
        
        Args:
            time_period: Time period to analyze (e.g., 'last_week', 'last_quarter')
            
        Returns:
            AgentResponse with performance analysis
        """
        try:
            # Get opportunities for the time period
            opportunities = [
                opp for opp in self.opportunities.values()
                if self._is_in_time_period(opp.created_at, time_period)
            ]
            
            # Calculate metrics
            total_value = sum(float(opp.amount) for opp in opportunities)
            won_opps = [opp for opp in opportunities if opp.stage == OpportunityStage.CLOSED_WON]
            win_rate = (len(won_opps) / len(opportunities)) * 100 if opportunities else 0
            
            # Generate insights using AI
            analysis_prompt = f"""
            Analyze the following sales performance metrics and provide key insights:
            
            Time Period: {time_period}
            Total Opportunities: {len(opportunities)}
            Total Pipeline Value: ${total_value:,.2f}
            Win Rate: {win_rate:.1f}%
            
            Provide analysis of what's working well, areas for improvement, and recommendations
            to improve sales performance in the next period.
            """
            
            insights = await self.llm.generate(analysis_prompt)
            
            return AgentResponse(
                success=True,
                output={
                    "time_period": time_period,
                    "total_opportunities": len(opportunities),
                    "pipeline_value": total_value,
                    "win_rate": win_rate,
                    "insights": insights,
                    "recommendations": [
                        "Focus on opportunities with higher win probability",
                        "Improve lead qualification process",
                        "Enhance sales training on objection handling"
                    ]
                },
                metadata={
                    "analysis_date": datetime.utcnow().isoformat(),
                    "opportunities_analyzed": len(opportunities)
                }
            )
            
        except Exception as e:
            logger.error(f"Sales performance analysis failed: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Sales performance analysis failed: {str(e)}",
                error_type=type(e).__name__
            )
    
    def _is_in_time_period(self, date: datetime, period: str) -> bool:
        """Check if a date falls within the specified time period."""
        now = datetime.utcnow()
        if period == "last_week":
            return date >= now - timedelta(weeks=1)
        elif period == "last_month":
            return date >= now - timedelta(days=30)
        elif period == "last_quarter":
            return date >= now - timedelta(days=90)
        elif period == "last_year":
            return date >= now - timedelta(days=365)
        return True
    
    async def create_account(self, account_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new account in the sales system.
        
        Args:
            account_data: Dictionary containing account details
            
        Returns:
            AgentResponse with created account details
        """
        try:
            # Generate a unique account ID
            account_id = f"acc_{len(self.accounts) + 1}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Create the account
            account = Account(
                id=account_id,
                name=account_data['name'],
                website=account_data.get('website'),
                industry=account_data.get('industry'),
                annual_revenue=account_data.get('annual_revenue'),
                employee_count=account_data.get('employee_count'),
                billing_address=account_data.get('billing_address'),
                shipping_address=account_data.get('shipping_address'),
                description=account_data.get('description'),
                tags=account_data.get('tags', [])
            )
            
            # Store the account
            self.accounts[account_id] = account
            
            return AgentResponse(
                success=True,
                output={
                    "account_id": account_id,
                    "account_name": account.name,
                    "status": "created",
                    "next_steps": [
                        "Add key contacts",
                        "Schedule account review",
                        "Research account background"
                    ]
                },
                metadata={
                    "created_at": account.created_at.isoformat(),
                    "industry": account.industry or "Not specified"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create account: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Account creation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"account_name": account_data.get('name', 'unknown')}
            )
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new contact in the sales system.
        
        Args:
            contact_data: Dictionary containing contact details
            
        Returns:
            AgentResponse with created contact details
        """
        try:
            # Generate a unique contact ID
            contact_id = f"con_{len(self.contacts) + 1}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Create the contact
            contact = Contact(
                id=contact_id,
                first_name=contact_data['first_name'],
                last_name=contact_data['last_name'],
                email=contact_data['email'],
                phone=contact_data.get('phone'),
                title=contact_data.get('title'),
                company=contact_data.get('company', ''),
                linkedin_url=contact_data.get('linkedin_url'),
                notes=contact_data.get('notes')
            )
            
            # Store the contact
            self.contacts[contact_id] = contact
            
            # Link to account if specified
            if 'account_id' in contact_data and contact_data['account_id'] in self.accounts:
                account_id = contact_data['account_id']
                self.accounts[account_id].contacts.append(contact_id)
                contact.company = self.accounts[account_id].name
            
            return AgentResponse(
                success=True,
                output={
                    "contact_id": contact_id,
                    "contact_name": f"{contact.first_name} {contact.last_name}",
                    "email": contact.email,
                    "company": contact.company,
                    "status": "created",
                    "next_steps": [
                        "Send welcome email",
                        "Schedule introduction call",
                        "Add to relevant email lists"
                    ]
                },
                metadata={
                    "created_at": contact.created_at.isoformat(),
                    "account_linked": 'account_id' in contact_data
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create contact: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Contact creation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"contact_email": contact_data.get('email', 'unknown')}
            )
    
    async def create_activity(self, activity_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new sales activity.
        
        Args:
            activity_data: Dictionary containing activity details
            
        Returns:
            AgentResponse with created activity details
        """
        try:
            # Generate a unique activity ID
            activity_id = f"act_{len(self.activities) + 1}_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            
            # Create the activity
            activity = Activity(
                id=activity_id,
                type=ActivityType(activity_data['type']),
                subject=activity_data['subject'],
                description=activity_data.get('description'),
                due_date=datetime.fromisoformat(activity_data['due_date']),
                related_to=activity_data.get('related_to'),
                participants=activity_data.get('participants', []),
                notes=activity_data.get('notes')
            )
            
            # Store the activity
            self.activities[activity_id] = activity
            
            # Schedule calendar event if needed
            if activity.type in [ActivityType.MEETING, ActivityType.CALL, ActivityType.DEMO]:
                calendar_event = {
                    'title': activity.subject,
                    'description': activity.description or "",
                    'start_time': activity.due_date.isoformat(),
                    'end_time': (activity.due_date + timedelta(hours=1)).isoformat(),
                    'attendees': [p.get('email') for p in activity.participants if 'email' in p]
                }
                await self.calendar.create_event(calendar_event)
            
            return AgentResponse(
                success=True,
                output={
                    "activity_id": activity_id,
                    "type": activity.type.value,
                    "subject": activity.subject,
                    "due_date": activity.due_date.isoformat(),
                    "status": "scheduled",
                    "next_steps": [
                        f"Prepare for {activity.type.value}",
                        "Send calendar invite" if activity.type in [ActivityType.MEETING, ActivityType.CALL] else "Prepare materials"
                    ]
                },
                metadata={
                    "created_at": activity.created_at.isoformat(),
                    "related_to": activity.related_to
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create activity: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Activity creation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"activity_type": activity_data.get('type', 'unknown')}
            )
    
    async def move_opportunity_stage(
        self, 
        opportunity_id: str, 
        new_stage: str,
        notes: Optional[str] = None
    ) -> AgentResponse:
        """
        Move an opportunity to a new stage in the sales pipeline.
        
        Args:
            opportunity_id: ID of the opportunity to update
            new_stage: New stage to move to (from OpportunityStage)
            notes: Optional notes about the stage change
            
        Returns:
            AgentResponse with update status
        """
        try:
            if opportunity_id not in self.opportunities:
                raise ValueError(f"Opportunity {opportunity_id} not found")
            
            opportunity = self.opportunities[opportunity_id]
            old_stage = opportunity.stage
            opportunity.stage = OpportunityStage(new_stage)
            opportunity.updated_at = datetime.utcnow()
            
            # Log the stage change
            stage_change_activity = Activity(
                id=f"act_{len(self.activities) + 1}",
                type=ActivityType.OTHER,
                subject=f"Stage Change: {old_stage.value} → {new_stage}",
                description=notes or f"Opportunity moved from {old_stage.value} to {new_stage}",
                due_date=datetime.utcnow(),
                completed=True,
                completed_at=datetime.utcnow(),
                related_to={"type": "opportunity", "id": opportunity_id}
            )
            self.activities[stage_change_activity.id] = stage_change_activity
            
            # Add next steps based on the new stage
            next_steps = []
            if new_stage == OpportunityStage.DEMONSTRATION:
                next_steps = [
                    "Schedule product demo",
                    "Prepare customized demo script",
                    "Identify technical stakeholders"
                ]
            elif new_stage == OpportunityStage.PROPOSAL:
                next_steps = [
                    "Draft proposal document",
                    "Review pricing options",
                    "Schedule proposal review meeting"
                ]
            elif new_stage == OpportunityStage.NEGOTIATION:
                next_steps = [
                    "Identify negotiation points",
                    "Prepare fallback options",
                    "Review contract terms"
                ]
            
            return AgentResponse(
                success=True,
                output={
                    "opportunity_id": opportunity_id,
                    "old_stage": old_stage.value,
                    "new_stage": new_stage,
                    "next_steps": next_steps,
                    "activity_id": stage_change_activity.id
                },
                metadata={
                    "updated_at": opportunity.updated_at.isoformat(),
                    "opportunity_name": opportunity.name
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update opportunity stage: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Failed to update opportunity stage: {str(e)}",
                error_type=type(e).__name__,
                metadata={"opportunity_id": opportunity_id, "new_stage": new_stage}
            )
    
    async def get_sales_metrics(self, time_period: str = "last_quarter") -> AgentResponse:
        """
        Get key sales metrics and KPIs.
        
        Args:
            time_period: Time period to analyze
            
        Returns:
            AgentResponse with sales metrics
        """
        try:
            # Get relevant opportunities
            opportunities = [
                opp for opp in self.opportunities.values()
                if self._is_in_time_period(opp.updated_at, time_period)
            ]
            
            # Calculate metrics
            total_opps = len(opportunities)
            won_opps = [o for o in opportunities if o.stage == OpportunityStage.CLOSED_WON]
            lost_opps = [o for o in opportunities if o.stage == OpportunityStage.CLOSED_LOST]
            open_opps = [o for o in opportunities if o.stage not in [
                OpportunityStage.CLOSED_WON, 
                OpportunityStage.CLOSED_LOST
            ]]
            
            total_value = sum(float(opp.amount) for opp in opportunities)
            won_value = sum(float(opp.amount) for opp in won_opps)
            open_value = sum(float(opp.amount) * (opp.probability / 100) for opp in open_opps)
            
            win_rate = (len(won_opps) / (len(won_opps) + len(lost_opps))) * 100 if (won_opps or lost_opps) else 0
            average_deal_size = won_value / len(won_opps) if won_opps else 0
            sales_cycle_days = self._calculate_average_sales_cycle(won_opps)
            
            # Generate insights
            insights_prompt = f"""
            Based on the following sales metrics, provide actionable insights:
            
            Time Period: {time_period}
            Total Opportunities: {total_opps}
            Win Rate: {win_rate:.1f}%
            Average Deal Size: ${average_deal_size:,.2f}
            Average Sales Cycle: {sales_cycle_days:.1f} days
            
            What are the key trends? What's working well? What needs improvement?
            Provide 3-5 specific, actionable recommendations.
            """
            
            insights = await self.llm.generate(insights_prompt)
            
            return AgentResponse(
                success=True,
                output={
                    "time_period": time_period,
                    "total_opportunities": total_opps,
                    "win_rate": win_rate,
                    "average_deal_size": average_deal_size,
                    "average_sales_cycle_days": sales_cycle_days,
                    "pipeline_value": total_value,
                    "won_value": won_value,
                    "open_opportunities_value": open_value,
                    "insights": insights,
                    "recommendations": [
                        "Focus on opportunities with higher win probability",
                        "Reduce sales cycle length by improving qualification",
                        "Increase average deal size through upselling"
                    ]
                },
                metadata={
                    "analysis_date": datetime.utcnow().isoformat(),
                    "opportunities_analyzed": total_opps
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get sales metrics: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Failed to get sales metrics: {str(e)}",
                error_type=type(e).__name__
            )
    
    def _calculate_average_sales_cycle(self, opportunities: List[Opportunity]) -> float:
        """Calculate the average sales cycle length in days from a list of won opportunities."""
        if not opportunities:
            return 0.0
            
        total_days = 0
        valid_opps = 0
        
        for opp in opportunities:
            if opp.created_at and opp.updated_at and opp.stage == OpportunityStage.CLOSED_WON:
                cycle_days = (opp.updated_at - opp.created_at).days
                if cycle_days > 0:  # Ignore same-day closes which might be test data
                    total_days += cycle_days
                    valid_opps += 1
        
        return total_days / valid_opps if valid_opps > 0 else 0.0
