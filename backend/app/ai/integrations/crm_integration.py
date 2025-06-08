"""
CRM Integration Module for Sales Agent.

This module provides an interface to interact with various CRM systems.
Currently supports HubSpot as the primary CRM with a base interface for others.
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

class HubSpotCRM(CRMIntegration):
    """HubSpot CRM integration."""
    
    def __init__(self, api_key: str):
        """Initialize HubSpot integration.
        
        Args:
            api_key: HubSpot API key (HAPI key or OAuth access token)
        """
        super().__init__(api_key, "https://api.hubapi.com/crm/v3/objects")
    
    async def create_contact(self, contact: CRMContact) -> Dict:
        """Create a new contact in HubSpot."""
        properties = {
            "email": contact.email,
            "firstname": contact.first_name,
            "lastname": contact.last_name,
            "phone": contact.phone,
            "company": contact.company,
            "jobtitle": contact.title
        }
        properties.update(contact.custom_fields)
        
        data = {
            "properties": {k: v for k, v in properties.items() if v is not None}
        }
        
        response = await self._make_request("POST", "contacts", data=data)
        return response
    
    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Get a contact by ID from HubSpot."""
        try:
            response = await self._make_request("GET", f"contacts/{contact_id}")
            props = response.get("properties", {})
            
            return CRMContact(
                id=response.get("id"),
                first_name=props.get("firstname", ""),
                last_name=props.get("lastname", ""),
                email=props.get("email", ""),
                phone=props.get("phone"),
                company=props.get("company"),
                title=props.get("jobtitle"),
                created_at=datetime.fromisoformat(props.get("createdate", "")),
                updated_at=datetime.fromisoformat(props.get("lastmodifieddate", "")),
                custom_fields={
                    k: v for k, v in props.items() 
                    if k not in ["firstname", "lastname", "email", "phone", "company", "jobtitle"]
                }
            )
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return None
            raise
    
    async def create_account(self, account: CRMAccount) -> Dict:
        """Create a new company in HubSpot."""
        properties = {
            "name": account.name,
            "website": str(account.website) if account.website else None,
            "industry": account.industry,
            "annualrevenue": account.annual_revenue,
            "numberofemployees": account.employee_count
        }
        properties.update(account.custom_fields)
        
        data = {
            "properties": {k: v for k, v in properties.items() if v is not None}
        }
        
        response = await self._make_request("POST", "companies", data=data)
        return response
    
    async def create_opportunity(self, opportunity: CRMOpportunity) -> Dict:
        """Create a new deal in HubSpot."""
        properties = {
            "dealname": opportunity.name,
            "amount": str(opportunity.amount),
            "dealstage": self._map_stage_to_hubspot(opportunity.stage),
            "pipeline": "default",
            "closedate": opportunity.close_date.isoformat() if opportunity.close_date else None,
            "hubspot_owner_id": opportunity.owner_id,
            "description": opportunity.description
        }
        
        if opportunity.probability is not None:
            properties["hs_probability"] = str(opportunity.probability)
        
        properties.update(opportunity.custom_fields)
        
        data = {
            "properties": {k: v for k, v in properties.items() if v is not None}
        }
        
        response = await self._make_request("POST", "deals", data=data)
        
        # Associate with company if provided
        if opportunity.account_id:
            await self._associate_deal_with_company(
                deal_id=response["id"],
                company_id=opportunity.account_id
            )
        
        return response
    
    async def _associate_deal_with_company(self, deal_id: str, company_id: str):
        """Associate a deal with a company in HubSpot."""
        await self._make_request(
            "PUT",
            f"deals/{deal_id}/associations/companies/{company_id}/deal_to_company",
            data={}
        )
    
    def _map_stage_to_hubspot(self, stage: str) -> str:
        """Map standard stage names to HubSpot stage IDs."""
        stage_mapping = {
            "discovery": "appointmentscheduled",
            "demonstration": "qualifiedtobuy",
            "proposal": "presentationscheduled",
            "negotiation": "decisionmakerboughtin",
            "closing": "contractsent",
            "closed_won": "closedwon",
            "closed_lost": "closedlost"
        }
        return stage_mapping.get(stage.lower(), "appointmentscheduled")

# Factory function for creating the appropriate CRM integration
def create_crm_integration(provider: str, api_key: str, **kwargs) -> CRMIntegration:
    """Create a CRM integration instance based on the provider.
    
    Args:
        provider: CRM provider name (e.g., 'hubspot')
        api_key: API key for the CRM
        **kwargs: Additional provider-specific arguments
        
    Returns:
        An instance of the appropriate CRM integration class
    """
    provider = provider.lower()
    
    if provider == 'hubspot':
        return HubSpotCRM(api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unsupported CRM provider: {provider}")
