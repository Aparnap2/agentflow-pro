"""
CRM Integration Module for Sales Agent.

This module provides a base interface for CRM systems.
For MVP, this is a simplified implementation without external dependencies.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from tenacity import retry, stop_after_attempt, wait_exponential
import aiohttp
import json

logger = logging.getLogger(__name__)

class CRMContact(BaseModel):
    """Contact information for CRM integration."""
    id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class CRMOpportunity(BaseModel):
    """Opportunity information for CRM integration."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    amount: float
    currency: str = "USD"
    stage: str
    close_date: Optional[datetime] = None
    probability: int = 0
    account_id: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class CRMAccount(BaseModel):
    """Account information for CRM integration."""
    id: Optional[str] = None
    name: str
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class CRMIntegration:
    """Base class for CRM integrations."""
    
    def __init__(self, api_key: str, base_url: str):
        """Initialize the CRM integration.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the CRM API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make an HTTP request to the CRM API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Dict containing the JSON response
        """
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response.raise_for_status()
                if response.status == 204:  # No content
                    return {}
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
    
    # Contact methods
    async def create_contact(self, contact: CRMContact) -> Dict:
        """Create a new contact in the CRM.
        
        Args:
            contact: Contact information
            
        Returns:
            Dict containing the created contact data
        """
        raise NotImplementedError
    
    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Get a contact by ID.
        
        Args:
            contact_id: ID of the contact to retrieve
            
        Returns:
            CRMContact if found, None otherwise
        """
        raise NotImplementedError
    
    async def update_contact(self, contact_id: str, update_data: Dict) -> Dict:
        """Update an existing contact.
        
        Args:
            contact_id: ID of the contact to update
            update_data: Fields to update
            
        Returns:
            Dict containing the updated contact data
        """
        raise NotImplementedError
    
    # Account methods
    async def create_account(self, account: CRMAccount) -> Dict:
        """Create a new account in the CRM.
        
        Args:
            account: Account information
            
        Returns:
            Dict containing the created account data
        """
        raise NotImplementedError
    
    async def get_account(self, account_id: str) -> Optional[CRMAccount]:
        """Get an account by ID.
        
        Args:
            account_id: ID of the account to retrieve
            
        Returns:
            CRMAccount if found, None otherwise
        """
        raise NotImplementedError
    
    # Opportunity methods
    async def create_opportunity(self, opportunity: CRMOpportunity) -> Dict:
        """Create a new opportunity in the CRM.
        
        Args:
            opportunity: Opportunity information
            
        Returns:
            Dict containing the created opportunity data
        """
        raise NotImplementedError
    
    async def update_opportunity_stage(
        self, 
        opportunity_id: str, 
        new_stage: str,
        **kwargs
    ) -> Dict:
        """Update the stage of an opportunity.
        
        Args:
            opportunity_id: ID of the opportunity to update
            new_stage: New stage for the opportunity
            
        Returns:
            Dict containing the updated opportunity data
        """
        raise NotImplementedError

class BasicCRM(CRMIntegration):
    """Basic CRM implementation for MVP."""
    
    def __init__(self):
        """Initialize the basic CRM."""
        super().__init__("", "")  # No API key or base URL needed for basic implementation
        self.contacts = {}
        self.accounts = {}
        self.opportunities = {}
    
    async def create_contact(self, contact: CRMContact) -> Dict:
        """Create a new contact."""
        contact_id = f"contact_{len(self.contacts) + 1}"
        contact.id = contact_id
        self.contacts[contact_id] = contact
        return {"id": contact_id, "status": "created"}
    
    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Get a contact by ID."""
        return self.contacts.get(contact_id)
    
    async def create_account(self, account: CRMAccount) -> Dict:
        """Create a new account."""
        account_id = f"account_{len(self.accounts) + 1}"
        account.id = account_id
        self.accounts[account_id] = account
        return {"id": account_id, "status": "created"}
    
    async def create_opportunity(self, opportunity: CRMOpportunity) -> Dict:
        """Create a new opportunity."""
        opportunity_id = f"opp_{len(self.opportunities) + 1}"
        opportunity.id = opportunity_id
        self.opportunities[opportunity_id] = opportunity
        return {"id": opportunity_id, "status": "created"}

# Factory function for creating the appropriate CRM integration
def create_crm_integration(provider: str = "basic", api_key: str = "", **kwargs) -> CRMIntegration:
    """Create a CRM integration instance.
    
    For MVP, only the basic CRM is supported.
    
    Args:
        provider: CRM provider name (only 'basic' is supported for MVP)
        api_key: Not used in basic implementation
        **kwargs: Additional arguments (ignored in basic implementation)
        
    Returns:
        An instance of the basic CRM integration
    """
    if provider != "basic":
        logger.warning(f"Only 'basic' CRM provider is supported in MVP. Using basic CRM instead of {provider}")
    return BasicCRM()
