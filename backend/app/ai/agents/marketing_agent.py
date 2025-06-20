from typing import Dict, Any, List, Optional, Union, Type, TypeVar, Callable, Tuple
from enum import Enum, auto
import json
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, validator, HttpUrl, conlist
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_agent import BaseAgent, AgentConfig, AgentResponse, AgentState
from ..integrations.google_ads import GoogleAdsIntegration
from ..integrations.facebook_ads import FacebookAdsIntegration
from ..integrations.hubspot_integration import HubspotIntegration
from ..integrations.mailchimp_integration import MailchimpIntegration
from ..integrations.google_analytics import GoogleAnalyticsIntegration
from ..integrations.slack_integration import SlackIntegration
from ..tools.analytics_tools import (
    calculate_roi,
    analyze_campaign_performance,
    segment_audience,
    generate_lead_scoring_model,
    predict_campaign_success
)

logger = logging.getLogger(__name__)

class CampaignType(str, Enum):
    """Types of marketing campaigns."""
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    SEARCH_ADS = "search_ads"
    DISPLAY_ADS = "display_ads"
    CONTENT_MARKETING = "content_marketing"
    INFLUENCER = "influencer"
    AFFILIATE = "affiliate"
    EVENT = "event"
    WEBINAR = "webinar"
    RETARGETING = "retargeting"

class CampaignStatus(str, Enum):
    """Status of a marketing campaign."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MarketingChannel(str, Enum):
    """Marketing channels for campaign distribution."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    GOOGLE = "google"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    DIRECT_MAIL = "direct_mail"

class CampaignObjective(str, Enum):
    """Marketing campaign objectives."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES = "sales"
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    APP_INSTALLS = "app_installs"
    VIDEO_VIEWS = "video_views"

class CampaignAudience(BaseModel):
    """Target audience for marketing campaigns."""
    name: str
    description: Optional[str] = None
    demographics: Dict[str, Any] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    behaviors: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    custom_audience: bool = False
    lookalike_audience: bool = False
    size_estimate: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CampaignBudget(BaseModel):
    """Budget allocation for marketing campaigns."""
    total_amount: float
    currency: str = "USD"
    daily_budget: Optional[float] = None
    lifetime_budget: bool = False
    optimization_goal: str = "conversions"
    bid_strategy: str = "lowest_cost"
    start_date: datetime
    end_date: Optional[datetime] = None

class CampaignContent(BaseModel):
    """Content assets for marketing campaigns."""
    headline: str
    primary_text: str
    description: Optional[str] = None
    call_to_action: str
    landing_page_url: HttpUrl
    image_urls: List[HttpUrl] = Field(default_factory=list)
    video_url: Optional[HttpUrl] = None
    ad_copy_variations: List[Dict[str, str]] = Field(default_factory=list)
    utm_parameters: Dict[str, str] = Field(default_factory=dict)

class MarketingCampaign(BaseModel):
    """Comprehensive marketing campaign model."""
    id: str
    name: str
    description: str
    campaign_type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    objective: CampaignObjective
    channels: List[MarketingChannel]
    audience: CampaignAudience
    budget: CampaignBudget
    content: CampaignContent
    kpis: Dict[str, Any] = Field(default_factory=dict)
    tracking_parameters: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    team_members: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class MarketingAgent(BaseAgent):
    """
    Advanced Marketing Agent specialized in digital marketing, campaign management, and analytics.
    
    This agent provides comprehensive marketing capabilities including:
    - Multi-channel campaign management
    - Audience segmentation and targeting
    - Marketing automation
    - Performance analytics and ROI tracking
    - A/B testing and optimization
    - Budget management
    - Marketing technology integration
    - Content strategy and distribution
    - Lead generation and nurturing
    - Marketing performance reporting
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.campaigns: Dict[str, MarketingCampaign] = {}
        self.active_campaigns: Dict[str, List[str]] = {}
        self.audiences: Dict[str, CampaignAudience] = {}
        self._init_marketing_integrations()
    
    def _init_marketing_integrations(self) -> None:
        """Initialize marketing platform integrations."""
        try:
            self.google_ads = GoogleAdsIntegration(
                client_id=settings.GOOGLE_ADS_CLIENT_ID,
                client_secret=settings.GOOGLE_ADS_CLIENT_SECRET,
                developer_token=settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                refresh_token=settings.GOOGLE_ADS_REFRESH_TOKEN
            )
            
            self.facebook_ads = FacebookAdsIntegration(
                app_id=settings.FACEBOOK_APP_ID,
                app_secret=settings.FACEBOOK_APP_SECRET,
                access_token=settings.FACEBOOK_ACCESS_TOKEN,
                ad_account_id=settings.FACEBOOK_AD_ACCOUNT_ID
            )
            
            self.hubspot = HubspotIntegration(
                api_key=settings.HUBSPOT_API_KEY,
                portal_id=settings.HUBSPOT_PORTAL_ID
            )
            
            self.mailchimp = MailchimpIntegration(
                api_key=settings.MAILCHIMP_API_KEY,
                server_prefix=settings.MAILCHIMP_SERVER_PREFIX
            )
            
            self.analytics = GoogleAnalyticsIntegration(
                property_id=settings.GA_PROPERTY_ID,
                credentials_path=settings.GA_CREDENTIALS_PATH
            )
            
            self.slack = SlackIntegration(api_token=settings.SLACK_BOT_TOKEN)
            
            logger.info("Marketing platform integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize marketing integrations: {str(e)}")
            raise
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a comprehensive marketing campaign across multiple channels.
        
        Args:
            campaign_data: Dictionary containing campaign details including:
                - name: Campaign name
                - description: Campaign description
                - campaign_type: Type of campaign (from CampaignType enum)
                - objective: Campaign objective (from CampaignObjective enum)
                - channels: List of marketing channels (from MarketingChannel enum)
                - audience: Audience definition
                - budget: Budget details
                - content: Content assets
                - start_date: Campaign start date (ISO format)
                - end_date: Campaign end date (ISO format, optional)
        
        Returns:
            AgentResponse with campaign details or error message
        """
        try:
            # Generate a unique campaign ID
            campaign_id = f"camp_{len(self.campaigns) + 1}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Create campaign objects
            audience = CampaignAudience(**campaign_data['audience'])
            budget = CampaignBudget(**campaign_data['budget'])
            content = CampaignContent(**campaign_data['content'])
            
            # Create the marketing campaign
            campaign = MarketingCampaign(
                id=campaign_id,
                name=campaign_data['name'],
                description=campaign_data['description'],
                campaign_type=CampaignType(campaign_data['campaign_type']),
                objective=CampaignObjective(campaign_data['objective']),
                channels=[MarketingChannel(ch) for ch in campaign_data['channels']],
                audience=audience,
                budget=budget,
                content=content,
                start_date=datetime.fromisoformat(campaign_data['start_date']),
                end_date=datetime.fromisoformat(campaign_data['end_date']) if 'end_date' in campaign_data else None,
                status=CampaignStatus.DRAFT
            )
            
            # Store the campaign
            self.campaigns[campaign_id] = campaign
            
            # Add to active campaigns if not in draft
            if campaign.status != CampaignStatus.DRAFT:
                for channel in campaign.channels:
                    if channel.value not in self.active_campaigns:
                        self.active_campaigns[channel.value] = []
                    self.active_campaigns[channel.value].append(campaign_id)
            
            # Generate tracking parameters
            self._generate_tracking_parameters(campaign)
            
            return AgentResponse(
                success=True,
                output={
                    "campaign_id": campaign_id,
                    "status": campaign.status,
                    "tracking_parameters": campaign.tracking_parameters,
                    "next_steps": ["Set up tracking", "Create ad sets", "Launch campaign"]
                },
                metadata={
                    "campaign_type": campaign.campaign_type,
                    "channels": [ch.value for ch in campaign.channels],
                    "created_at": campaign.created_at.isoformat(),
                    "budget_currency": campaign.budget.currency
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Campaign creation failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"campaign_name": campaign_data.get('name', 'unknown')}
            )
    
    async def launch_campaign(self, campaign_id: str) -> AgentResponse:
        """Launch a marketing campaign across all configured channels."""
        try:
            if campaign_id not in self.campaigns:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            campaign = self.campaigns[campaign_id]
            
            # Update campaign status
            campaign.status = CampaignStatus.ACTIVE
            campaign.updated_at = datetime.utcnow()
            
            # Initialize results dictionary
            launch_results = {}
            
            # Launch on each channel
            for channel in campaign.channels:
                try:
                    if channel == MarketingChannel.GOOGLE:
                        result = await self._launch_google_ads_campaign(campaign)
                    elif channel in [MarketingChannel.FACEBOOK, MarketingChannel.INSTAGRAM]:
                        result = await self._launch_facebook_ads_campaign(campaign, channel)
                    elif channel == MarketingChannel.EMAIL:
                        result = await self._launch_email_campaign(campaign)
                    else:
                        result = {"status": "skipped", "message": f"Channel {channel} launch not implemented"}
                    
                    launch_results[channel.value] = result
                    
                except Exception as e:
                    logger.error(f"Failed to launch on {channel}: {str(e)}", exc_info=True)
                    launch_results[channel.value] = {
                        "status": "failed",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
            
            # Update campaign status based on results
            all_success = all(r.get("status") == "success" for r in launch_results.values())
            campaign.status = CampaignStatus.ACTIVE if all_success else CampaignStatus.PAUSED
            
            return AgentResponse(
                success=all_success,
                output={
                    "campaign_id": campaign_id,
                    "status": campaign.status,
                    "launch_results": launch_results
                },
                metadata={
                    "campaign_name": campaign.name,
                    "launched_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to launch campaign {campaign_id}: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Campaign launch failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"campaign_id": campaign_id}
            )
    
    async def analyze_campaign_performance(self, campaign_id: str) -> AgentResponse:
        """
        Analyze the performance of a marketing campaign.
        
        Args:
            campaign_id: ID of the campaign to analyze
            
        Returns:
            AgentResponse with performance analysis and recommendations
        """
        try:
            if campaign_id not in self.campaigns:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            campaign = self.campaigns[campaign_id]
            
            # Collect performance data from all channels
            performance_data = {}
            
            for channel in campaign.channels:
                try:
                    if channel == MarketingChannel.GOOGLE:
                        data = await self.google_ads.get_campaign_metrics(campaign_id)
                    elif channel in [MarketingChannel.FACEBOOK, MarketingChannel.INSTAGRAM]:
                        data = await self.facebook_ads.get_campaign_insights(campaign_id)
                    elif channel == MarketingChannel.EMAIL:
                        data = await self.mailchimp.get_campaign_report(campaign_id)
                    else:
                        data = {"status": "skipped", "message": f"Channel {channel} analysis not implemented"}
                    
                    performance_data[channel.value] = data
                    
                except Exception as e:
                    logger.error(f"Failed to get performance data for {channel}: {str(e)}", exc_info=True)
                    performance_data[channel.value] = {
                        "status": "error",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
            
            # Generate insights and recommendations
            insights = await self._generate_performance_insights(campaign, performance_data)
            
            return AgentResponse(
                success=True,
                output={
                    "campaign_id": campaign_id,
                    "campaign_name": campaign.name,
                    "status": campaign.status,
                    "performance_summary": {
                        "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
                        "total_spend": sum(
                            data.get("spend", 0) 
                            for data in performance_data.values() 
                            if isinstance(data, dict) and "spend" in data
                        ),
                        "total_impressions": sum(
                            data.get("impressions", 0) 
                            for data in performance_data.values() 
                            if isinstance(data, dict) and "impressions" in data
                        ),
                        "total_clicks": sum(
                            data.get("clicks", 0) 
                            for data in performance_data.values() 
                            if isinstance(data, dict) and "clicks" in data
                        ),
                        "total_conversions": sum(
                            data.get("conversions", 0) 
                            for data in performance_data.values() 
                            if isinstance(data, dict) and "conversions" in data
                        )
                    },
                    "channel_performance": performance_data,
                    "insights": insights.get("insights", []),
                    "recommendations": insights.get("recommendations", []),
                    "next_steps": insights.get("next_steps", [])
                },
                metadata={
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "campaign_type": campaign.campaign_type,
                    "channels": [ch.value for ch in campaign.channels]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze campaign {campaign_id}: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Campaign analysis failed: {str(e)}",
                error_type=type(e).__name__,
                metadata={"campaign_id": campaign_id}
            )
    
    # Additional specialized methods
    async def segment_audience(
        self, 
        audience_criteria: Dict[str, Any], 
        source: str = "customer_database"
    ) -> AgentResponse:
        """Segment audience based on criteria and data source."""
        # Implementation for audience segmentation
        pass
    
    async def create_lead_scoring_model(
        self, 
        historical_data: List[Dict[str, Any]],
        target_variable: str,
        model_type: str = "xgboost"
    ) -> AgentResponse:
        """Create a lead scoring model using historical data."""
        # Implementation for lead scoring model
        pass
    
    async def generate_content_ideas(
        self, 
        topic: str, 
        target_audience: str,
        count: int = 5,
        content_type: str = "blog_post"
    ) -> AgentResponse:
        """Generate content ideas based on topic and audience."""
        # Implementation for content idea generation
        pass
    
    async def optimize_ad_copy(
        self,
        current_copy: str,
        target_metrics: Dict[str, float],
        platform: str = "facebook"
    ) -> AgentResponse:
        """Optimize ad copy based on target metrics."""
        # Implementation for ad copy optimization
        pass
    
    # Helper methods
    def _generate_tracking_parameters(self, campaign: MarketingCampaign) -> None:
        """Generate UTM parameters and other tracking codes for a campaign."""
        base_params = {
            "utm_source": "marketing_automation",
            "utm_medium": "cpc",  # Default, can be overridden
            "utm_campaign": campaign.id,
            "utm_content": "",  # Will be populated per ad/variation
            "utm_term": ""  # For paid search keywords
        }
        
        # Add platform-specific parameters
        if MarketingChannel.FACEBOOK in campaign.channels:
            base_params["fbclid"] = f"{campaign.id}_fb"
        if MarketingChannel.GOOGLE in campaign.channels:
            base_params["gclid"] = f"{campaign.id}_google"
        
        campaign.tracking_parameters = base_params
    
    async def _launch_google_ads_campaign(self, campaign: MarketingCampaign) -> Dict[str, Any]:
        """Launch campaign on Google Ads."""
        # Implementation for Google Ads launch
        return {"status": "success", "message": "Google Ads campaign created"}
    
    async def _launch_facebook_ads_campaign(
        self, 
        campaign: MarketingCampaign, 
        channel: MarketingChannel
    ) -> Dict[str, Any]:
        """Launch campaign on Facebook/Instagram Ads."""
        # Implementation for Facebook/Instagram Ads launch
        return {"status": "success", "message": f"{channel.value} campaign created"}
    
    async def _launch_email_campaign(self, campaign: MarketingCampaign) -> Dict[str, Any]:
        """Launch email campaign."""
        # Implementation for email campaign launch
        return {"status": "success", "message": "Email campaign created"}
    
    async def _generate_performance_insights(
        self, 
        campaign: MarketingCampaign, 
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights and recommendations from performance data."""
        # Implementation for performance analysis
        return {
            "insights": ["Campaign is performing above average", "Mobile traffic converts better"],
            "recommendations": ["Increase budget for top performers", "Test new ad creatives"],
            "next_steps": ["Optimize underperforming ads", "Expand successful segments"]
        }

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    async def main():
        # Example configuration
        config = AgentConfig(
            id="marketing_agent_1",
            name="Digital Marketing Specialist",
            role="Senior Marketing Strategist",
            goal="Drive customer acquisition and engagement through data-driven marketing",
            backstory="""
            You are an experienced marketing professional with 8+ years in digital marketing.
            You specialize in multi-channel campaign management, marketing automation,
            and performance optimization. Your analytical skills help you make data-driven
            decisions that maximize ROI.
            """,
            verbose=True,
            allow_delegation=True,
            tools=["google_ads", "facebook_ads", "hubspot", "mailchimp", "google_analytics"],
            llm_config={
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )
        
        # Create agent instance
        agent = MarketingAgent(config)
        
        # Example campaign data
        campaign_data = {
            "name": "Summer Sale 2024",
            "description": "Summer promotion for new product line",
            "campaign_type": "social_media",
            "objective": "sales",
            "channels": ["facebook", "google", "email"],
            "audience": {
                "name": "Summer Shoppers",
                "description": "Customers interested in summer products",
                "demographics": {
                    "age_range": ["25-54"],
                    "gender": ["male", "female"],
                    "locations": ["United States", "Canada"],
                    "languages": ["en"]
                },
                "interests": ["fashion", "summer", "travel"],
                "behaviors": ["frequent_shopper", "mobile_user"],
                "custom_audience": True,
                "size_estimate": 1500000
            },
            "budget": {
                "total_amount": 10000,
                "daily_budget": 500,
                "start_date": "2024-06-15T00:00:00",
                "end_date": "2024-07-15T23:59:59",
                "optimization_goal": "conversions",
                "bid_strategy": "target_cpa"
            },
            "content": {
                "headline": "Summer Sale - Up to 50% Off!",
                "primary_text": "Don't miss our biggest sale of the season. Shop now for amazing deals!",
                "call_to_action": "Shop Now",
                "landing_page_url": "https://example.com/summer-sale",
                "image_urls": [
                    "https://example.com/images/summer-sale-1.jpg",
                    "https://example.com/images/summer-sale-2.jpg"
                ],
                "utm_parameters": {
                    "utm_source": "summer_sale_2024",
                    "utm_medium": "cpc"
                }
            },
            "start_date": "2024-06-15T00:00:00",
            "end_date": "2024-07-15T23:59:59"
        }
        
        # Create campaign
        result = await agent.create_campaign(campaign_data)
        
        if result.success:
            print("Campaign created successfully!")
            print(f"Campaign ID: {result.output['campaign_id']}")
            print(f"Status: {result.output['status']}")
            print("\nNext steps:")
            for step in result.output['next_steps']:
                print(f"- {step}")
        else:
            print(f"Error: {result.error}")
    
    asyncio.run(main())
