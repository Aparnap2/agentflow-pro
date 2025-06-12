"""
Basic Payment Processor Implementation for MVP.

This module provides a simple in-memory implementation of the PaymentProcessorIntegration
interface for MVP purposes. It does not process real payments but simulates the behavior.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from decimal import Decimal
import uuid

from .payment_processor_integration import (
    PaymentProcessorIntegration,
    Customer,
    PaymentIntent,
    Refund,
    PaymentStatus,
    PaymentMethodType,
    Currency,
    Address
)

logger = logging.getLogger(__name__)

class BasicPaymentProcessor(PaymentProcessorIntegration):
    """Basic in-memory payment processor for MVP."""
    
    def __init__(self, **kwargs):
        """Initialize the basic payment processor."""
        super().__init__(**kwargs)
        self._customers = {}
        self._payment_intents = {}
        self._refunds = {}
        self._payment_methods = {}
    
    def _generate_id(self, prefix: str = '') -> str:
        """Generate a unique ID with optional prefix."""
        return f"{prefix}{str(uuid.uuid4()).replace('-', '')}"
    
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Customer:
        """Create a new customer."""
        customer_id = self._generate_id('cus_')
        customer = Customer(
            id=customer_id,
            email=email,
            name=name,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        self._customers[customer_id] = customer
        
        if payment_method_id and payment_method_id in self._payment_methods:
            self._payment_methods[payment_method_id].customer_id = customer_id
            
        return customer
    
    async def retrieve_customer(self, customer_id: str, **kwargs) -> Optional[Customer]:
        """Retrieve a customer by ID."""
        return self._customers.get(customer_id)
    
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
        payment_intent_id = self._generate_id('pi_')
        now = datetime.utcnow()
        
        if customer_id and customer_id not in self._customers:
            raise ValueError(f"Customer {customer_id} not found")
        
        # For MVP, we'll just simulate a successful payment
        status = PaymentStatus.SUCCEEDED if confirm else PaymentStatus.REQUIRES_CONFIRMATION
        
        payment_intent = PaymentIntent(
            id=payment_intent_id,
            amount=amount,
            currency=Currency(currency) if isinstance(currency, str) else currency,
            status=status,
            customer_id=customer_id,
            payment_method_id=payment_method_id,
            payment_method_types=[PaymentMethodType.CARD],  # Default to card
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
            client_secret=f"mock_client_secret_{payment_intent_id}"
        )
        
        self._payment_intents[payment_intent_id] = payment_intent
        return payment_intent
    
    async def retrieve_payment_intent(
        self,
        payment_intent_id: str,
        **kwargs
    ) -> Optional[PaymentIntent]:
        """Retrieve a payment intent by ID."""
        return self._payment_intents.get(payment_intent_id)
    
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
        **kwargs
    ) -> PaymentIntent:
        """Confirm a payment intent."""
        payment_intent = await self.retrieve_payment_intent(payment_intent_id)
        if not payment_intent:
            raise ValueError(f"Payment intent {payment_intent_id} not found")
        
        # Update the payment intent
        payment_intent.status = PaymentStatus.SUCCEEDED
        payment_intent.updated_at = datetime.utcnow()
        if payment_method_id:
            payment_intent.payment_method_id = payment_method_id
        
        return payment_intent
    
    async def capture_payment_intent(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        **kwargs
    ) -> PaymentIntent:
        """Capture a payment intent."""
        payment_intent = await self.retrieve_payment_intent(payment_intent_id)
        if not payment_intent:
            raise ValueError(f"Payment intent {payment_intent_id} not found")
        
        if payment_intent.status != PaymentStatus.REQUIRES_CAPTURE:
            raise ValueError(f"Payment intent {payment_intent_id} is not in a capturable state")
        
        payment_intent.status = PaymentStatus.SUCCEEDED
        payment_intent.updated_at = datetime.utcnow()
        
        return payment_intent
    
    async def cancel_payment_intent(
        self,
        payment_intent_id: str,
        **kwargs
    ) -> PaymentIntent:
        """Cancel a payment intent."""
        payment_intent = await self.retrieve_payment_intent(payment_intent_id)
        if not payment_intent:
            raise ValueError(f"Payment intent {payment_intent_id} not found")
        
        if payment_intent.status not in [PaymentStatus.REQUIRES_PAYMENT_METHOD, 
                                       PaymentStatus.REQUIRES_CONFIRMATION, 
                                       PaymentStatus.REQUIRES_ACTION]:
            raise ValueError(f"Cannot cancel payment intent {payment_intent_id} in status {payment_intent.status}")
        
        payment_intent.status = PaymentStatus.CANCELED
        payment_intent.updated_at = datetime.utcnow()
        
        return payment_intent
    
    async def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Refund:
        """Create a refund for a payment intent."""
        payment_intent = await self.retrieve_payment_intent(payment_intent_id)
        if not payment_intent:
            raise ValueError(f"Payment intent {payment_intent_id} not found")
        
        if payment_intent.status != PaymentStatus.SUCCEEDED:
            raise ValueError(f"Cannot refund payment intent {payment_intent_id} with status {payment_intent.status}")
        
        refund_amount = amount if amount is not None else payment_intent.amount
        refund_id = self._generate_id('re_')
        now = datetime.utcnow()
        
        refund = Refund(
            id=refund_id,
            amount=refund_amount,
            currency=payment_intent.currency,
            payment_intent_id=payment_intent_id,
            reason=reason,
            status="succeeded",
            created_at=now,
            metadata=metadata or {}
        )
        
        self._refunds[refund_id] = refund
        
        # Update payment intent status if fully refunded
        if refund_amount == payment_intent.amount:
            payment_intent.status = PaymentStatus.REFUNDED
        else:
            payment_intent.status = PaymentStatus.PARTIALLY_REFUNDED
        
        payment_intent.updated_at = now
        
        return refund
    
    async def retrieve_refund(
        self,
        refund_id: str,
        **kwargs
    ) -> Optional[Refund]:
        """Retrieve a refund by ID."""
        return self._refunds.get(refund_id)
    
    async def list_refunds(
        self,
        payment_intent_id: Optional[str] = None,
        limit: int = 10,
        **kwargs
    ) -> List[Refund]:
        """List refunds, optionally filtered by payment intent."""
        refunds = list(self._refunds.values())
        
        if payment_intent_id is not None:
            refunds = [r for r in refunds if r.payment_intent_id == payment_intent_id]
        
        return refunds[:limit]
