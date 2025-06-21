"""Vertical agents module - Business function specialized agents."""

from .crm_agent import CRMAgent
from .email_marketing_agent import EmailMarketingAgent
from .invoice_agent import InvoiceAgent
from .scheduling_agent import SchedulingAgent
from .social_agent import SocialAgent
from .hr_agent import HRAgent
from .admin_agent import AdminAgent
from .review_agent import ReviewAgent

__all__ = [
    'CRMAgent',
    'EmailMarketingAgent', 
    'InvoiceAgent',
    'SchedulingAgent',
    'SocialAgent',
    'HRAgent',
    'AdminAgent',
    'ReviewAgent'
]