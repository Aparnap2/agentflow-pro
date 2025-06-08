"""
Mailchimp Integration

Provides functionality to interact with Mailchimp API for email marketing,
audience management, and campaign automation.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel, Field, validator, HttpUrl, EmailStr
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class MailchimpAuthConfig(BaseModel):
    """Configuration for Mailchimp API authentication."""
    api_key: str
    server_prefix: Optional[str] = None  # e.g., 'us1', 'us2', etc.
    access_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    oauth2_access_token: Optional[str] = None
    oauth2_refresh_token: Optional[str] = None
    oauth2_expires_at: Optional[datetime] = None
    user_agent: Optional[str] = "AI Marketing Agent/1.0"
    timeout: int = 30

class MailchimpListVisibility(str, Enum):
    """Visibility options for Mailchimp lists."""
    PUB = "pub"
    PRIV = "prv"

class MailchimpCampaignType(str, Enum):
    """Mailchimp campaign types."""
    REGULAR = "regular"
    PLAINTEXT = "plaintext"
    ABSPLIT = "absplit"
    RSS = "rss"
    AUTOMATION = "automation"
    VARIATE = "variate"

class MailchimpCampaignStatus(str, Enum):
    """Mailchimp campaign statuses."""
    SAVE = "save"
    PAUSED = "paused"
    SCHEDULE = "schedule"
    SENDING = "sending"
    SENT = "sent"

class MailchimpEmailType(str, Enum):
    """Mailchimp email types."""
    HTML = "html"
    PLAINTEXT = "plaintext"

class MailchimpTargetingType(str, Enum):
    """Mailchimp campaign targeting types."""
    SAVED = "saved"
    INTERESTS = "interests"
    GEO = "geo"

class MailchimpMemberStatus(str, Enum):
    """Mailchimp list member statuses."""
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    CLEANED = "cleaned"
    PENDING = "pending"
    TRANSACTIONAL = "transactional"

class MailchimpEmailTypePreference(str, Enum):
    """Mailchimp email type preferences."""
    HTML = "html"
    TEXT = "text"
    MOBILE = "mobile"

class MailchimpMergeFieldType(str, Enum):
    """Mailchimp merge field types."""
    TEXT = "text"
    NUMBER = "number"
    ADDRESS = "address"
    PHONE = "phone"
    DATE = "date"
    URL = "url"
    IMAGEURL = "imageurl"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    BIRTHDAY = "birthday"
    ZIP = "zip"

class MailchimpListContact(BaseModel):
    """Contact information for a Mailchimp list."""
    company: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip: str
    country: str
    phone: Optional[str] = None

class MailchimpCampaignRecipients(BaseModel):
    """Recipient settings for a Mailchimp campaign."""
    list_id: str
    list_name: Optional[str] = None
    segment_opts: Optional[Dict[str, Any]] = None
    segment_text: Optional[str] = None

class MailchimpCampaignSettings(BaseModel):
    """Settings for a Mailchimp campaign."""
    subject_line: str
    title: Optional[str] = None
    from_name: str
    reply_to: str
    use_conversation: Optional[bool] = False
    to_name: Optional[str] = None
    folder_id: Optional[str] = None
    authenticate: Optional[bool] = True
    auto_footer: Optional[bool] = False
    inline_css: Optional[bool] = True
    auto_tweet: Optional[bool] = False
    auto_fb_post: Optional[List[str]] = Field(default_factory=list)
    fb_comments: Optional[bool] = True
    template_id: Optional[int] = None
    drag_and_drop: Optional[bool] = True

class MailchimpCampaignTracking(BaseModel):
    """Tracking settings for a Mailchimp campaign."""
    opens: bool = True
    html_clicks: bool = True
    text_clicks: bool = True
    goal_tracking: bool = False
    ecomm360: bool = False
    google_analytics: Optional[str] = None
    clicktale: Optional[str] = None

class MailchimpCampaignRssOpts(BaseModel):
    """RSS feed options for a Mailchimp campaign."""
    feed_url: HttpUrl
    frequency: str = "daily"  # daily, weekly, monthly
    schedule: Optional[Dict[str, Any]] = None
    constrain_rss_img: Optional[bool] = True
    last_sent: Optional[datetime] = None

class MailchimpCampaignSocialCard(BaseModel):
    """Social card settings for a Mailchimp campaign."""
    image_url: Optional[HttpUrl] = None
    description: str
    title: str

class MailchimpCampaignReportSummary(BaseModel):
    """Summary report for a Mailchimp campaign."""
    opens: int = 0
    unique_opens: int = 0
    open_rate: float = 0.0
    clicks: int = 0
    subscriber_clicks: int = 0
    click_rate: float = 0.0
    ecommerce: Dict[str, Any] = Field(default_factory=dict)

class MailchimpCampaignDeliveryStatus(BaseModel):
    """Delivery status for a Mailchimp campaign."""
    enabled: bool = False
    can_cancel: bool = False
    status: Optional[str] = None
    emails_sent: int = 0
    emails_canceled: int = 0

class MailchimpListMemberLocation(BaseModel):
    """Location data for a Mailchimp list member."""
    latitude: float
    longitude: float
    gmtoff: int
    dstoff: int
    country_code: str
    timezone: str
    region: Optional[str] = None

class MailchimpListMemberStats(BaseModel):
    """Statistics for a Mailchimp list member."""
    avg_open_rate: float = 0.0
    avg_click_rate: float = 0.0
    ecommerce_data: Optional[Dict[str, Any]] = None
    last_sale: Optional[Dict[str, Any]] = None

class MailchimpMergeFieldOptions(BaseModel):
    """Options for a Mailchimp merge field."""
    default_country: Optional[str] = None
    phone_format: Optional[str] = None
    date_format: Optional[str] = None
    choices: Optional[List[str]] = None
    size: Optional[int] = None

class MailchimpMergeField(BaseModel):
    """A merge field for a Mailchimp list."""
    merge_id: Optional[int] = None
    tag: str
    name: str
    type: MailchimpMergeFieldType
    required: bool = False
    default_value: Optional[str] = None
    public: bool = True
    display_order: int = 0
    options: Optional[MailchimpMergeFieldOptions] = None
    help_text: Optional[str] = None
    list_id: Optional[str] = None

class MailchimpListMember(BaseModel):
    """A member of a Mailchimp list."""
    email_address: EmailStr
    email_type: MailchimpEmailTypePreference = MailchimpEmailTypePreference.HTML
    status: MailchimpMemberStatus = MailchimpMemberStatus.SUBSCRIBED
    merge_fields: Optional[Dict[str, Any]] = None
    interests: Optional[Dict[str, bool]] = None
    language: Optional[str] = None
    vip: bool = False
    location: Optional[MailchimpListMemberLocation] = None
    ip_signup: Optional[str] = None
    timestamp_signup: Optional[datetime] = None
    ip_opt: Optional[str] = None
    timestamp_opt: Optional[datetime] = None
    email_client: Optional[str] = None
    last_changed: Optional[datetime] = None
    list_id: Optional[str] = None
    member_rating: int = 2
    stats: Optional[MailchimpListMemberStats] = None

class MailchimpCampaignContent(BaseModel):
    """Content settings for a Mailchimp campaign."""
    html: Optional[str] = None
    text: Optional[str] = None
    url: Optional[HttpUrl] = None
    archive: Optional[Dict[str, Any]] = None
    archive_html: Optional[Dict[str, Any]] = None
    archive_type: Optional[str] = None
    archive_url: Optional[HttpUrl] = None
    template: Optional[Dict[str, Any]] = None

class MailchimpCampaignVariateSettings(BaseModel):
    """Variate settings for a Mailchimp campaign."""
    winning_combination_id: Optional[str] = None
    winning_campaign_id: Optional[str] = None
    winner_criteria: Optional[str] = None
    wait_time: Optional[int] = None
    test_size: Optional[int] = None
    subject_lines: Optional[List[str]] = None
    send_times: Optional[List[datetime]] = None
    from_names: Optional[List[str]] = None
    reply_to_addresses: Optional[List[str]] = None
    contents: Optional[List[str]] = None
    combinations: Optional[List[Dict[str, Any]]] = None

class MailchimpCampaignTrackingOptions(BaseModel):
    """Tracking options for a Mailchimp campaign."""
    opens: bool = True
    html_clicks: bool = True
    text_clicks: bool = True
    goal_tracking: bool = False
    ecomm360: bool = False
    google_analytics: Optional[str] = None
    clicktale: Optional[str] = None

class MailchimpCampaignRssOpts(BaseModel):
    """RSS feed options for a Mailchimp campaign."""
    feed_url: HttpUrl
    frequency: str = "daily"  # daily, weekly, monthly
    schedule: Optional[Dict[str, Any]] = None
    constrain_rss_img: Optional[bool] = True
    last_sent: Optional[datetime] = None

class MailchimpCampaignSocialCard(BaseModel):
    """Social card settings for a Mailchimp campaign."""
    image_url: Optional[HttpUrl] = None
    description: str
    title: str

class MailchimpCampaignReportSummary(BaseModel):
    """Summary report for a Mailchimp campaign."""
    opens: int = 0
    unique_opens: int = 0
    open_rate: float = 0.0
    clicks: int = 0
    subscriber_clicks: int = 0
    click_rate: float = 0.0
    ecommerce: Dict[str, Any] = Field(default_factory=dict)

class MailchimpCampaignDeliveryStatus(BaseModel):
    """Delivery status for a Mailchimp campaign."""
    enabled: bool = False
    can_cancel: bool = False
    status: Optional[str] = None
    emails_sent: int = 0
    emails_canceled: int = 0

class MailchimpIntegration:
    """
    Integration with Mailchimp API for email marketing and automation.
    
    This class provides methods to interact with Mailchimp API, including:
    - List management (create, update, delete)
    - Member management (subscribe, update, unsubscribe)
    - Campaign creation and scheduling
    - Template management
    - Automation workflows
    - Reporting and analytics
    """
    
    def __init__(self, config: Union[Dict[str, Any], MailchimpAuthConfig]):
        """
        Initialize the Mailchimp integration.
        
        Args:
            config: Configuration for Mailchimp API authentication
        """
        if isinstance(config, dict):
            self.config = MailchimpAuthConfig(**config)
        else:
            self.config = config
            
        self._client = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Mailchimp API client."""
        try:
            # Initialize the Mailchimp client
            self._client = MailchimpMarketing.Client()
            
            # Configure the client
            if self.config.api_key:
                # Extract server prefix from API key if not provided
                if not self.config.server_prefix and '_' in self.config.api_key:
                    self.config.server_prefix = self.config.api_key.split('-')[-1]
                
                self._client.set_config({
                    "api_key": self.config.api_key,
                    "server": self.config.server_prefix or "us1"
                })
            elif self.config.access_token:
                self._client.set_config({
                    "access_token": self.config.access_token,
                    "server": self.config.server_prefix or "us1"
                })
            elif self.config.oauth2_access_token:
                self._client.set_config({
                    "oauth2_access_token": self.config.oauth2_access_token,
                    "oauth2_refresh_token": self.config.oauth2_refresh_token,
                    "oauth2_expires_at": self.config.oauth2_expires_at.isoformat() if self.config.oauth2_expires_at else None,
                    "server": self.config.server_prefix or "us1"
                })
            else:
                raise ValueError("No valid authentication method provided. Need either api_key, access_token, or OAuth2 credentials.")
            
            # Test the connection
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.ping.get()
            )
            
            self._initialized = True
            logger.info("Mailchimp integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Mailchimp client: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiClientError, Exception)),
        reraise=True
    )
    async def get_lists(self, count: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        Get all lists in the Mailchimp account.
        
        Args:
            count: Number of lists to return (max 1000)
            offset: Number of lists to skip for pagination
            
        Returns:
            Dictionary with list of lists and total items
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Get lists from Mailchimp
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.lists.get_all_lists(
                    count=min(count, 1000),
                    offset=offset
                )
            )
            
            return {
                'success': True,
                'lists': response.get('lists', []),
                'total_items': response.get('total_items', 0),
                'operation': 'lists_retrieved'
            }
            
        except ApiClientError as e:
            logger.error(f"Mailchimp API error: {e.text}")
            return {
                'success': False,
                'error': e.text,
                'error_type': 'mailchimp_api_error',
                'status_code': e.status_code,
                'operation': 'lists_retrieval'
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve lists: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'lists_retrieval'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiClientError, Exception)),
        reraise=True
    )
    async def create_list(
        self,
        name: str,
        contact: MailchimpListContact,
        permission_reminder: str,
        email_type_option: bool,
        campaign_defaults: Dict[str, str],
        visibility: MailchimpListVisibility = MailchimpListVisibility.PUB
        use_archive_bar: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new list in Mailchimp.
        
        Args:
            name: Name of the list
            contact: Contact information for the list
            permission_reminder: Permission reminder text
            email_type_option: Whether to enable email type selection
            campaign_defaults: Default settings for campaigns
            visibility: List visibility (public or private)
            use_archive_bar: Whether to use the archive bar in campaigns
            
        Returns:
            Dictionary with the created list details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Prepare list data
            list_data = {
                "name": name,
                "contact": contact.dict(exclude_none=True),
                "permission_reminder": permission_reminder,
                "email_type_option": email_type_option,
                "campaign_defaults": campaign_defaults,
                "visibility": visibility.value,
                "use_archive_bar": use_archive_bar
            }
            
            # Create the list
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.lists.create_list(list_data)
            )
            
            logger.info(f"Created list {response['id']}: {name}")
            
            return {
                'success': True,
                'list_id': response['id'],
                'list_name': response['name'],
                'operation': 'list_created',
                'data': response
            }
            
        except ApiClientError as e:
            logger.error(f"Mailchimp API error: {e.text}")
            return {
                'success': False,
                'error': e.text,
                'error_type': 'mailchimp_api_error',
                'status_code': e.status_code,
                'operation': 'list_creation'
            }
            
        except Exception as e:
            logger.error(f"Failed to create list: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'list_creation'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiClientError, Exception)),
        reraise=True
    )
    async def add_list_member(
        self,
        list_id: str,
        member: Union[Dict[str, Any], MailchimpListMember]
    ) -> Dict[str, Any]:
        """
        Add or update a member in a Mailchimp list.
        
        Args:
            list_id: ID of the list
            member: Member data to add or update
            
        Returns:
            Dictionary with the member details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Convert MailchimpListMember to dict if needed
            if isinstance(member, MailchimpListMember):
                member_data = member.dict(exclude_none=True, exclude={"list_id"})
            else:
                member_data = member
            
            # Add or update the member (upsert)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.lists.set_list_member(
                    list_id,
                    member_data['email_address'],
                    member_data
                )
            )
            
            logger.info(f"Added/updated member {response['email_address']} in list {list_id}")
            
            return {
                'success': True,
                'member_id': response['id'],
                'email_address': response['email_address'],
                'status': response['status'],
                'operation': 'member_added',
                'data': response
            }
            
        except ApiClientError as e:
            logger.error(f"Mailchimp API error: {e.text}")
            return {
                'success': False,
                'error': e.text,
                'error_type': 'mailchimp_api_error',
                'status_code': e.status_code,
                'operation': 'member_addition'
            }
            
        except Exception as e:
            logger.error(f"Failed to add member to list: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'member_addition'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiClientError, Exception)),
        reraise=True
    )
    async def create_campaign(
        self,
        type: MailchimpCampaignType,
        recipients: Union[Dict[str, Any], MailchimpCampaignRecipients],
        settings: Union[Dict[str, Any], MailchimpCampaignSettings],
        tracking: Optional[Union[Dict[str, Any], MailchimpCampaignTracking]] = None,
        rss_opts: Optional[Union[Dict[str, Any], MailchimpCampaignRssOpts]] = None,
        social_card: Optional[Union[Dict[str, Any], MailchimpCampaignSocialCard]] = None,
        content: Optional[Union[Dict[str, Any], MailchimpCampaignContent]] = None
    ) -> Dict[str, Any]:
        """
        Create a new campaign in Mailchimp.
        
        Args:
            type: Type of campaign
            recipients: Recipient settings
            settings: Campaign settings
            tracking: Tracking settings
            rss_opts: RSS feed options
            social_card: Social card settings
            content: Campaign content
            
        Returns:
            Dictionary with the created campaign details
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Prepare campaign data
            campaign_data = {
                'type': type.value,
                'recipients': recipients.dict(exclude_none=True) if isinstance(recipients, MailchimpCampaignRecipients) else recipients,
                'settings': settings.dict(exclude_none=True) if isinstance(settings, MailchimpCampaignSettings) else settings,
            }
            
            # Add optional fields
            if tracking is not None:
                campaign_data['tracking'] = tracking.dict(exclude_none=True) if isinstance(tracking, MailchimpCampaignTracking) else tracking
                
            if rss_opts is not None:
                campaign_data['rss_opts'] = rss_opts.dict(exclude_none=True) if isinstance(rss_opts, MailchimpCampaignRssOpts) else rss_opts
                
            if social_card is not None:
                campaign_data['social_card'] = social_card.dict(exclude_none=True) if isinstance(social_card, MailchimpCampaignSocialCard) else social_card
                
            if content is not None:
                campaign_data['content'] = content.dict(exclude_none=True) if isinstance(content, MailchimpCampaignContent) else content
            
            # Create the campaign
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.campaigns.create(campaign_data)
            )
            
            logger.info(f"Created campaign {response['id']}: {response['settings']['title']}")
            
            return {
                'success': True,
                'campaign_id': response['id'],
                'web_id': response['web_id'],
                'type': response['type'],
                'status': response['status'],
                'operation': 'campaign_created',
                'data': response
            }
            
        except ApiClientError as e:
            logger.error(f"Mailchimp API error: {e.text}")
            return {
                'success': False,
                'error': e.text,
                'error_type': 'mailchimp_api_error',
                'status_code': e.status_code,
                'operation': 'campaign_creation'
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'campaign_creation'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiClientError, Exception)),
        reraise=True
    )
    async def send_campaign(
        self,
        campaign_id: str,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Send a campaign immediately or schedule it for later.
        
        Args:
            campaign_id: ID of the campaign to send
            schedule_time: When to send the campaign (None for immediate)
            
        Returns:
            Dictionary with the send status
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            if schedule_time:
                # Schedule the campaign
                schedule_data = {
                    'schedule_time': schedule_time.isoformat(),
                    'timewarp': False,
                    'batch_delivery': {
                        'batch_delay': 0,
                        'batch_count': 1
                    }
                }
                
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._client.campaigns.schedule(
                        campaign_id,
                        schedule_data
                    )
                )
                
                logger.info(f"Scheduled campaign {campaign_id} for {schedule_time}")
                operation = 'campaign_scheduled'
            else:
                # Send immediately
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._client.campaigns.send(campaign_id)
                )
                
                logger.info(f"Sent campaign {campaign_id} immediately")
                operation = 'campaign_sent'
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'operation': operation,
                'data': response
            }
            
        except ApiClientError as e:
            logger.error(f"Mailchimp API error: {e.text}")
            return {
                'success': False,
                'error': e.text,
                'error_type': 'mailchimp_api_error',
                'status_code': e.status_code,
                'operation': 'campaign_send'
            }
            
        except Exception as e:
            logger.error(f"Failed to send campaign: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'campaign_send'
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ApiClientError, Exception)),
        reraise=True
    )
    async def get_campaign_report(
        self,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Get the report for a sent campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary with the campaign report
        """
        if not self._initialized:
            await self.initialize()
            
        try:
            # Get the campaign report
            report = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.reports.get_campaign_report(campaign_id)
            )
            
            logger.info(f"Retrieved report for campaign {campaign_id}")
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'emails_sent': report.get('emails_sent', 0),
                'opens': report.get('opens', {}).get('unique_opens', 0),
                'clicks': report.get('clicks', {}).get('unique_clicks', 0),
                'bounces': report.get('bounces', {}).get('hard_bounces', 0) + report.get('bounces', {}).get('soft_bounces', 0),
                'unsubscribes': report.get('unsubscribed', 0),
                'operation': 'report_retrieved',
                'data': report
            }
            
        except ApiClientError as e:
            logger.error(f"Mailchimp API error: {e.text}")
            return {
                'success': False,
                'error': e.text,
                'error_type': 'mailchimp_api_error',
                'status_code': e.status_code,
                'operation': 'report_retrieval'
            }
            
        except Exception as e:
            logger.error(f"Failed to get campaign report: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general_error',
                'operation': 'report_retrieval'
            }
