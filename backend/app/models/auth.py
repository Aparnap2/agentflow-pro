from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from uuid import uuid4
from .base import UserRole, AgentRole, Department, MessageType
from ..core.config import PlanType

class TokenData(BaseModel):
    user_id: str
    tenant_id: str
    email: str
    role: UserRole

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    tenant_name: str
    plan: PlanType = PlanType.STARTER

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    tenant: dict

class UserInfo(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    email: str
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class TenantInfo(BaseModel):
    tenant_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    plan: PlanType
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    api_calls_quota: int
    llm_tokens_quota: int
    is_active: bool = True

class RateLimitInfo(BaseModel):
    tenant_id: str
    window_start: datetime
    api_calls: int
    llm_tokens: int
    api_calls_limit: int
    llm_tokens_limit: int
