from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import stripe
import json

from ..core.config import settings
from ..models import auth
from ..services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_auth_service() -> AuthService:
    return AuthService()

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,
    success_url: str,
    cancel_url: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create a Stripe checkout session"""
    try:
        # Authenticate user
        current_user = await auth_service.verify_token(credentials.credentials)
        
        # Get or create customer in Stripe
        customer = await stripe.Customer.create(
            email=current_user.email,
            metadata={
                "user_id": current_user.user_id,
                "tenant_id": current_user.tenant_id
            }
        )
        
        # Define prices based on plan (simplified example)
        prices = {
            "starter": "price_...",  # Replace with actual price ID
            "pro": "price_...",     # Replace with actual price ID
            "enterprise": "price_..."  # Replace with actual price ID
        }
        
        if plan not in prices:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan"
            )
        
        # Create checkout session
        session = await stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price': prices[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": current_user.user_id,
                "tenant_id": current_user.tenant_id,
                "plan": plan
            }
        )
        
        return {"url": session.url}
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )

@router.post("/webhook")
async def webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Update your database to reflect the subscription
            await handle_checkout_session_completed(session)
        # Add more event types as needed
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

async def handle_checkout_session_completed(session):
    """Handle successful checkout session"""
    # In a real implementation, update your database to reflect the subscription
    # This is a placeholder function
    print(f"Checkout session completed: {session.id}")
    print(f"Customer: {session.customer}")
    print(f"Metadata: {session.metadata}")
    
    # Example: Update user's subscription in your database
    # await db.execute(
    #     """
    #     UPDATE tenants 
    #     SET plan = $1, stripe_customer_id = $2
    #     WHERE tenant_id = $3
    #     """,
    #     session.metadata.get('plan'),
    #     session.customer,
    #     session.metadata.get('tenant_id')
    # )

@router.get("/subscription")
async def get_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current subscription information"""
    try:
        # Authenticate user and get tenant info
        user, tenant = await auth_service.get_current_tenant_info(credentials)
        
        if not tenant.stripe_customer_id:
            return {"status": "no_subscription"}
        
        # Get customer from Stripe
        customer = await stripe.Customer.retrieve(tenant.stripe_customer_id)
        
        # Get subscriptions
        subscriptions = await stripe.Subscription.list(
            customer=tenant.stripe_customer_id,
            limit=1
        )
        
        if not subscriptions.data:
            return {
                "status": "active",
                "plan": tenant.plan,
                "payment_method": None,
                "next_payment": None
            }
        
        subscription = subscriptions.data[0]
        
        # Get default payment method
        payment_method = None
        if customer.invoice_settings and customer.invoice_settings.default_payment_method:
            payment_method = await stripe.PaymentMethod.retrieve(
                customer.invoice_settings.default_payment_method
            )
        
        return {
            "status": subscription.status,
            "plan": tenant.plan,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "payment_method": payment_method,
            "next_payment": subscription.current_period_end
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subscription: {str(e)}"
        )
