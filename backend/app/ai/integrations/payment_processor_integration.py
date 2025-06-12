"""
Payment Processor Integration Module for Sales Agent.

This module provides functionality to process payments through various payment processors.
Currently supports Stripe with a base interface for other providers.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, condecimal
from decimal import Decimal
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class PaymentStatus(str, Enum):
    """Payment status values."""
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"

class PaymentMethodType(str, Enum):
    """Supported payment method types."""
    CARD = "card"
    BANK_ACCOUNT = "bank_account"
    PAYPAL = "paypal"
    SEPA_DEBIT = "sepa_debit"
    SOFORT = "sofort"
    ALIPAY = "alipay"
    KLARNA = "klarna"
    AFTERPAY_CLEARPAY = "afterpay_clearpay"
    BANCONTACT = "bancontact"
    GIROPAY = "giropay"
    IDEAL = "ideal"
    PRZELEWY = "p24"
    OTHER = "other"

class Currency(str, Enum):
    """Supported currencies."""
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    CAD = "cad"
    AUD = "aud"
    JPY = "jpy"
    CNY = "cny"
    INR = "inr"
    SGD = "sgd"
    AED = "aed"
    CHF = "chf"
    SEK = "sek"
    NOK = "nok"
    DKK = "dkk"

class Address(BaseModel):
    """Billing/Shipping address."""
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class Customer(BaseModel):
    """Customer information for payments."""
    id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

class PaymentMethod(BaseModel):
    """Payment method details."""
    id: str
    type: PaymentMethodType
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    billing_details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class PaymentIntent(BaseModel):
    """Payment intent information."""
    id: str
    amount: condecimal(ge=0, decimal_places=2)
    currency: Currency
    status: PaymentStatus
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    payment_method_types: List[PaymentMethodType] = Field(default_factory=list)
    receipt_email: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_payment_error: Optional[Dict[str, Any]] = None
    client_secret: Optional[str] = None
    next_action: Optional[Dict[str, Any]] = None

class Refund(BaseModel):
    """Refund information."""
    id: str
    amount: condecimal(ge=0, decimal_places=2)
    currency: Currency
    payment_intent_id: str
    reason: Optional[str] = None
    status: str
    created_at: datetime
    metadata: Dict[str, str] = Field(default_factory=dict)

class PaymentProcessorIntegration:
    """Base class for payment processor integrations."""
    
    def __init__(self, **kwargs):
        """Initialize the payment processor integration."""
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Customer:
        """Create a new customer."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def retrieve_customer(self, customer_id: str, **kwargs) -> Optional[Customer]:
        """Retrieve a customer by ID."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: Union[str, Currency],
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        off_session: bool = False,
        confirm: bool = True,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> PaymentIntent:
        """Create a new payment intent."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def retrieve_payment_intent(
        self,
        payment_intent_id: str,
        **kwargs
    ) -> Optional[PaymentIntent]:
        """Retrieve a payment intent by ID."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
        **kwargs
    ) -> PaymentIntent:
        """Confirm a payment intent."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def capture_payment_intent(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        **kwargs
    ) -> PaymentIntent:
        """Capture a payment intent."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def cancel_payment_intent(
        self,
        payment_intent_id: str,
        **kwargs
    ) -> PaymentIntent:
        """Cancel a payment intent."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Refund:
        """Create a refund for a payment intent."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def retrieve_refund(
        self,
        refund_id: str,
        **kwargs
    ) -> Optional[Refund]:
        """Retrieve a refund by ID."""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def list_refunds(
        self,
        payment_intent_id: Optional[str] = None,
        limit: int = 10,
        **kwargs
    ) -> List[Refund]:
        """List refunds, optionally filtered by payment intent."""
        raise NotImplementedError("Subclasses must implement this method")
