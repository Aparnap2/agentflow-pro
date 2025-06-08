"""
HubSpot Integration

Provides functionality to interact with HubSpot CRM API for contact management,
deal tracking, and marketing automation.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel, Field, validator, HttpUrl, EmailStr
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException
from hubspot.crm.deals import SimplePublicObjectInput as DealInput
from hubspot.crm.companies import SimplePublicObjectInput as CompanyInput
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class HubSpotAuthConfig(BaseModel):
    """Configuration for HubSpot API authentication."""
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    token: Optional[Dict[str, Any]] = None

class HubSpotObjectType(str, Enum):
    """HubSpot object types."""
    CONTACT = "contacts"
    COMPANY = "companies"
    DEAL = "deals"
    TICKET = "tickets"
    FEEDBACK_SUBMISSION = "feedback_submissions"
    LINE_ITEM = "line_items"
    PRODUCT = "products"
    QUOTE = "quotes"
    TASK = "tasks"
    CALL = "calls"
    EMAIL = "emails"
    MEETING = "meetings"
    NOTE = "notes"
    POSTAL_MAIL = "postal_mail"
    TASK = "tasks"

class HubSpotAssociationType(str, Enum):
    """HubSpot association types."""
    CONTACT_TO_COMPANY = "contact_to_company"
    COMPANY_TO_CONTACT = "company_to_contact"
    DEAL_TO_CONTACT = "deal_to_contact"
    CONTACT_TO_DEAL = "contact_to_deal"
    DEAL_TO_COMPANY = "deal_to_company"
    COMPANY_TO_DEAL = "company_to_deal"
    DEAL_TO_LINE_ITEM = "deal_to_line_item"
    LINE_ITEM_TO_DEAL = "line_item_to_deal"
    COMPANY_TO_TICKET = "company_to_ticket"
    TICKET_TO_COMPANY = "ticket_to_company"
    CONTACT_TO_TICKET = "contact_to_ticket"
    TICKET_TO_CONTACT = "ticket_to_contact"

class HubSpotContactProperties(BaseModel):
    """HubSpot contact properties."""
    email: Optional[EmailStr] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    website: Optional[HttpUrl] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    hubspot_owner_id: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    lead_source: Optional[str] = None
    hs_lead_status: Optional[str] = None
    jobtitle: Optional[str] = None
    mobilephone: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    twitterhandle: Optional[str] = None
    facebook_username: Optional[str] = None
    linkedin_username: Optional[str] = None
    twitterusername: Optional[str] = None
    github_username: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    annualrevenue: Optional[float] = None
    numberofemployees: Optional[int] = None
    hubspot_team_id: Optional[str] = None
    hs_analytics_source: Optional[str] = None
    hs_analytics_source_data_1: Optional[str] = None
    hs_analytics_source_data_2: Optional[str] = None
    hs_analytics_first_timestamp: Optional[datetime] = None
    hs_analytics_last_timestamp: Optional[datetime] = None
    hs_analytics_num_visits: Optional[int] = None
    hs_analytics_num_page_views: Optional[int] = None
    hs_analytics_num_event_completions: Optional[int] = None
    recent_conversion_date: Optional[datetime] = None
    recent_conversion_event_name: Optional[str] = None
    num_contacted_notes: Optional[int] = None
    num_notes: Optional[int] = None
    owner_assigned_date: Optional[datetime] = None
    hs_all_team_ids: Optional[List[str]] = None
    hs_all_accessible_team_ids: Optional[List[str]] = None
    hs_analytics_first_referrer: Optional[str] = None
    hs_analytics_last_referrer: Optional[str] = None
    hs_email_domain: Optional[str] = None
    hs_email_quarantined: Optional[bool] = None
    hs_email_recipient_fatigue_recovery_time: Optional[datetime] = None
    hs_email_sends_since_last_engagement: Optional[int] = None
    hs_is_contact: Optional[bool] = None
    hs_is_unworked: Optional[bool] = None
    hs_lifecyclestage_lead_date: Optional[datetime] = None
    hs_lifecyclestage_marketingqualifiedlead_date: Optional[datetime] = None
    hs_lifecyclestage_opportunity_date: Optional[datetime] = None
    hs_lifecyclestage_salesqualifiedlead_date: Optional[datetime] = None
    hs_lifecyclestage_subscriber_date: Optional[datetime] = None
    hs_predictivecontactscore_v2: Optional[float] = None
    hs_sa_first_engagement_object_id: Optional[str] = None
    hs_sales_email_last_clicked: Optional[datetime] = None
    hs_sales_email_last_opened: Optional[datetime] = None
    hs_sequences_actively_enrolled_count: Optional[int] = None
    hs_sequences_enrolled_count: Optional[int] = None
    hs_testpurge: Optional[str] = None
    hubspot_owner_assigneddate: Optional[datetime] = None
    notes_last_contacted: Optional[datetime] = None
    notes_last_updated: Optional[datetime] = None
    notes_next_activity_date: Optional[datetime] = None
    num_associated_deals: Optional[int] = None
    num_conversion_events: Optional[int] = None
    num_unique_conversion_events: Optional[int] = None
    recent_conversion_currency: Optional[str] = None
    recent_conversion_amount: Optional[float] = None
    recent_deal_amount: Optional[float] = None
    recent_deal_close_date: Optional[datetime] = None
    timezone: Optional[str] = None
    createdate: Optional[datetime] = None
    lastmodifieddate: Optional[datetime] = None
    hs_object_id: Optional[str] = None
    archived: Optional[bool] = None

class HubSpotCompanyProperties(BaseModel):
    """HubSpot company properties."""
    name: Optional[str] = None
    domain: Optional[str] = None
    phone: Optional[str] = None
    phone_service: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    numberofemployees: Optional[int] = None
    annualrevenue: Optional[float] = None
    website: Optional[HttpUrl] = None
    hubspot_owner_id: Optional[str] = None
    is_public: Optional[bool] = None
    lifecycle_stage: Optional[str] = None
    createdate: Optional[datetime] = None
    lastmodifieddate: Optional[datetime] = None
    closedate: Optional[datetime] = None
    first_contact_createdate: Optional[datetime] = None
    days_to_close: Optional[int] = None
    hs_all_team_ids: Optional[List[str]] = None
    hs_analytics_num_visits: Optional[int] = None
    hs_analytics_num_page_views: Optional[int] = None
    hs_analytics_first_timestamp: Optional[datetime] = None
    hs_analytics_last_timestamp: Optional[datetime] = None
    hs_analytics_source: Optional[str] = None
    hs_analytics_source_data_1: Optional[str] = None
    hs_analytics_source_data_2: Optional[str] = None
    hs_lead_status: Optional[str] = None
    hs_lifecyclestage_customer_date: Optional[datetime] = None
    hs_lifecyclestage_lead_date: Optional[datetime] = None
    hs_lifecyclestage_marketingqualifiedlead_date: Optional[datetime] = None
    hs_lifecyclestage_opportunity_date: Optional[datetime] = None
    hs_lifecyclestage_salesqualifiedlead_date: Optional[datetime] = None
    hs_lifecyclestage_subscriber_date: Optional[datetime] = None
    hs_object_id: Optional[str] = None
    archived: Optional[bool] = None

class HubSpotDealProperties(BaseModel):
    """HubSpot deal properties."""
    amount: Optional[float] = None
    closedate: Optional[datetime] = None
    createdate: Optional[datetime] = None
    dealname: str
    dealstage: str
    pipeline: str = "default"
    hubspot_owner_id: Optional[str] = None
    description: Optional[str] = None
    amount_in_home_currency: Optional[float] = None
    deal_currency_code: Optional[str] = None
    dealtype: Optional[str] = None
    hs_createdate: Optional[datetime] = None
    hs_is_closed: Optional[bool] = None
    hs_is_closed_won: Optional[bool] = None
    hs_lastmodifieddate: Optional[datetime] = None
    hs_object_id: Optional[str] = None
    hs_projected_amount: Optional[float] = None
    hs_projected_amount_in_home_currency: Optional[float] = None
    hs_tcv: Optional[float] = None
    hubspot_team_id: Optional[str] = None
    is_archived: Optional[bool] = None
    notes_last_contacted: Optional[datetime] = None
    notes_last_updated: Optional[datetime] = None
    notes_next_activity_date: Optional[datetime] = None
    num_associated_contacts: Optional[int] = None
    num_notes: Optional[int] = None
    num_contacted_notes: Optional[int] = None
    num_times_contacted: Optional[int] = None
    pipeline_stage: Optional[str] = None
    priority: Optional[str] = None
    source: Optional[str] = None
    hs_all_team_ids: Optional[List[str]] = None
    hs_created_by_user_id: Optional[str] = None
    hs_updated_by_user_id: Optional[str] = None
    hs_was_imported: Optional[bool] = None
    hubspot_owner_assigneddate: Optional[datetime] = None
    archived: Optional[bool] = None

class HubSpotIntegration:
    """
    Integration with HubSpot CRM API.
    
    This class provides methods to interact with HubSpot CRM, including:
    - Contact management (create, read, update, delete)
    - Company management
    - Deal tracking
    - Associations between objects
    - Custom objects
    - Email and marketing automation
    """
    
    def __init__(self, config: Union[Dict[str, Any], HubSpotAuthConfig]):
        """
        Initialize the HubSpot integration.
        
        Args:
            config: Configuration for HubSpot API authentication
        """
        if isinstance(config, dict):
            self.config = HubSpotAuthConfig(**config)
        else:
            self.config = config
            
        self._client = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the HubSpot API client."""
        try:
            # Configure the HubSpot client
            if self.config.access_token:
                self._client = HubSpot(access_token=self.config.access_token)
            elif self.config.api_key:
                self._client = HubSpot(api_key=self.config.api_key)
            elif self.config.client_id and self.config.client_secret and self.config.refresh_token:
                self._client = HubSpot(
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret,
                    refresh_token=self.config.refresh_token
                )
            else:
                raise ValueError("Insufficient credentials provided. Need either access_token, api_key, or OAuth credentials.")
            
            self._initialized = True
            logger.info("HubSpot integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HubSpot client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def create_contact(self, properties: Union[Dict[str, Any], HubSpotContactProperties]) -> Dict[str, Any]:
        """
        Create a new contact in HubSpot.
        
        Args:
            properties: Contact properties
            
        Returns:
            Dictionary with contact ID and other details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Convert to HubSpot SimplePublicObjectInput
            if isinstance(properties, HubSpotContactProperties):
                properties = properties.dict(exclude_none=True)
            
            contact_input = SimplePublicObjectInput(properties=properties)
            
            # Create the contact
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.contacts.basic_api.create(
                    simple_public_object_input=contact_input
                )
            )
            
            logger.info(f"Created contact {api_response.id}")
            
            return {
                'success': True,
                'id': api_response.id,
                'properties': api_response.properties,
                'created_at': api_response.created_at,
                'updated_at': api_response.updated_at,
                'archived': api_response.archived,
                'operation': 'contact_created'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'contact_creation'
            }
            
        except Exception as e:
            logger.error(f"Failed to create contact: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'contact_creation'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def update_contact(self, contact_id: str, properties: Union[Dict[str, Any], HubSpotContactProperties]) -> Dict[str, Any]:
        """
        Update an existing contact in HubSpot.
        
        Args:
            contact_id: ID of the contact to update
            properties: Contact properties to update
            
        Returns:
            Dictionary with updated contact details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Convert to HubSpot SimplePublicObjectInput
            if isinstance(properties, HubSpotContactProperties):
                properties = properties.dict(exclude_none=True)
            
            contact_input = SimplePublicObjectInput(properties=properties)
            
            # Update the contact
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.contacts.basic_api.update(
                    contact_id=contact_id,
                    simple_public_object_input=contact_input
                )
            )
            
            logger.info(f"Updated contact {contact_id}")
            
            return {
                'success': True,
                'id': api_response.id,
                'properties': api_response.properties,
                'updated_at': api_response.updated_at,
                'archived': api_response.archived,
                'operation': 'contact_updated'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'contact_update'
            }
            
        except Exception as e:
            logger.error(f"Failed to update contact: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'contact_update'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def get_contact(self, contact_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a contact from HubSpot by ID.
        
        Args:
            contact_id: ID of the contact to retrieve
            properties: List of properties to include in the response
            
        Returns:
            Dictionary with contact details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Get the contact
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.contacts.basic_api.get_by_id(
                    contact_id=contact_id,
                    properties=properties or None,
                    archived=False
                )
            )
            
            logger.info(f"Retrieved contact {contact_id}")
            
            return {
                'success': True,
                'id': api_response.id,
                'properties': api_response.properties,
                'created_at': api_response.created_at,
                'updated_at': api_response.updated_at,
                'archived': api_response.archived,
                'operation': 'contact_retrieved'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'contact_retrieval'
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve contact: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'contact_retrieval'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def search_contacts(self, query: str, limit: int = 10, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for contacts in HubSpot.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            properties: List of properties to include in the response
            
        Returns:
            Dictionary with search results
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Search for contacts
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.contacts.search_api.do_search(
                    public_object_search_request={
                        "query": query,
                        "limit": limit,
                        "properties": properties or [],
                        "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}]
                    }
                )
            )
            
            logger.info(f"Found {len(api_response.results)} contacts matching query: {query}")
            
            return {
                'success': True,
                'results': [
                    {
                        'id': contact.id,
                        'properties': contact.properties,
                        'created_at': contact.created_at,
                        'updated_at': contact.updated_at,
                        'archived': contact.archived
                    }
                    for contact in api_response.results
                ],
                'total': api_response.total,
                'operation': 'contacts_searched'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'contacts_search'
            }
            
        except Exception as e:
            logger.error(f"Failed to search contacts: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'contacts_search'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def create_company(self, properties: Union[Dict[str, Any], HubSpotCompanyProperties]) -> Dict[str, Any]:
        """
        Create a new company in HubSpot.
        
        Args:
            properties: Company properties
            
        Returns:
            Dictionary with company ID and other details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Convert to HubSpot SimplePublicObjectInput
            if isinstance(properties, HubSpotCompanyProperties):
                properties = properties.dict(exclude_none=True)
            
            company_input = CompanyInput(properties=properties)
            
            # Create the company
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.companies.basic_api.create(
                    simple_public_object_input=company_input
                )
            )
            
            logger.info(f"Created company {api_response.id}")
            
            return {
                'success': True,
                'id': api_response.id,
                'properties': api_response.properties,
                'created_at': api_response.created_at,
                'updated_at': api_response.updated_at,
                'archived': api_response.archived,
                'operation': 'company_created'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'company_creation'
            }
            
        except Exception as e:
            logger.error(f"Failed to create company: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'company_creation'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def create_deal(self, properties: Union[Dict[str, Any], HubSpotDealProperties]) -> Dict[str, Any]:
        """
        Create a new deal in HubSpot.
        
        Args:
            properties: Deal properties
            
        Returns:
            Dictionary with deal ID and other details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Convert to HubSpot SimplePublicObjectInput
            if isinstance(properties, HubSpotDealProperties):
                properties = properties.dict(exclude_none=True)
            
            deal_input = DealInput(properties=properties)
            
            # Create the deal
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.deals.basic_api.create(
                    simple_public_object_input=deal_input
                )
            )
            
            logger.info(f"Created deal {api_response.id}")
            
            return {
                'success': True,
                'id': api_response.id,
                'properties': api_response.properties,
                'created_at': api_response.created_at,
                'updated_at': api_response.updated_at,
                'archived': api_response.archived,
                'operation': 'deal_created'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'deal_creation'
            }
            
        except Exception as e:
            logger.error(f"Failed to create deal: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'deal_creation'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def create_association(
        self,
        from_object_type: str,
        from_object_id: str,
        to_object_type: str,
        to_object_id: str,
        association_type: str
    ) -> Dict[str, Any]:
        """
        Create an association between two objects in HubSpot.
        
        Args:
            from_object_type: Type of the source object (e.g., 'contacts', 'companies', 'deals')
            from_object_id: ID of the source object
            to_object_type: Type of the target object
            to_object_id: ID of the target object
            association_type: Type of association (e.g., 'contact_to_company')
            
        Returns:
            Dictionary with association details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Create the association
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.crm.associations.batch_api.create(
                    from_object_type=from_object_type,
                    to_object_type=to_object_type,
                    batch_input_public_association={
                        "inputs": [
                            {
                                "from": {"id": from_object_id},
                                "to": {"id": to_object_id},
                                "type": association_type
                            }
                        ]
                    }
                )
            )
            
            logger.info(f"Created association between {from_object_type}:{from_object_id} and {to_object_type}:{to_object_id}")
            
            return {
                'success': True,
                'from_object_type': from_object_type,
                'from_object_id': from_object_id,
                'to_object_type': to_object_type,
                'to_object_id': to_object_id,
                'association_type': association_type,
                'operation': 'association_created'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'association_creation'
            }
            
        except Exception as e:
            logger.error(f"Failed to create association: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'association_creation'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiException, Exception)),
        reraise=True
    )
    async def send_email(
        self,
        email_id: str,
        message: Dict[str, Any],
        contact_properties: Optional[List[Dict[str, str]]] = None,
        custom_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a marketing email through HubSpot.
        
        Args:
            email_id: ID of the email template to send
            message: Email message details
            contact_properties: List of contact properties to include
            custom_properties: Custom properties to include in the email
            
        Returns:
            Dictionary with email send details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Prepare the email request
            email_request = {
                "emailId": email_id,
                "message": message,
                "contactProperties": contact_properties or [],
                "customProperties": custom_properties or {}
            }
            
            # Send the email
            api_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.marketing.transactional.single_send_api.send(
                    public_single_send_request_egg=email_request
                )
            )
            
            logger.info(f"Sent email with ID: {api_response.id}")
            
            return {
                'success': True,
                'id': api_response.id,
                'status': api_response.status,
                'operation': 'email_sent'
            }
            
        except ApiException as e:
            logger.error(f"HubSpot API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'hubspot_api_error',
                'error_code': e.status,
                'error_body': e.body,
                'operation': 'email_send'
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'email_send'
            }
