import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import settings
from ..models import auth

security = HTTPBearer()

class AuthService:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    def create_access_token(self, user_data: auth.TokenData) -> str:
        """Create JWT access token"""
        to_encode = {
            "user_id": user_data.user_id,
            "tenant_id": user_data.tenant_id,
            "email": user_data.email,
            "role": user_data.role.value,
            "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
        }
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def verify_token(self, token: str) -> auth.TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return auth.TokenData(
                user_id=payload["user_id"],
                tenant_id=payload["tenant_id"],
                email=payload["email"],
                role=auth.UserRole(payload["role"])
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.JWTError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def register_user(self, request: auth.RegisterRequest) -> auth.AuthResponse:
        """Register new user and tenant"""
        # Check if user already exists
        existing_user = await self.db.fetchrow(
            "SELECT * FROM users WHERE email = $1", 
            request.email
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Start transaction
        async with self.db.transaction():
            # Create tenant
            tenant = auth.TenantInfo(
                name=request.tenant_name,
                plan=request.plan,
                api_calls_quota=settings.STARTER_PLAN_API_CALLS,
                llm_tokens_quota=settings.STARTER_PLAN_LLM_TOKENS
            )
            
            await self.db.execute(
                """
                INSERT INTO tenants (
                    tenant_id, name, plan, api_calls_quota, llm_tokens_quota
                ) VALUES ($1, $2, $3, $4, $5)
                """,
                tenant.tenant_id, tenant.name, tenant.plan.value,
                tenant.api_calls_quota, tenant.llm_tokens_quota
            )

            # Create user
            hashed_password = self.hash_password(request.password)
            user = auth.UserInfo(
                tenant_id=tenant.tenant_id,
                email=request.email,
                role=auth.UserRole.OWNER
            )
            
            await self.db.execute(
                """
                INSERT INTO users (
                    user_id, tenant_id, email, password_hash, role
                ) VALUES ($1, $2, $3, $4, $5)
                """,
                user.user_id, user.tenant_id, user.email, 
                hashed_password, user.role.value
            )

            # Create auth token
            token_data = auth.TokenData(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                role=user.role
            )
            access_token = self.create_access_token(token_data)

            return auth.AuthResponse(
                access_token=access_token,
                user=user.dict(),
                tenant=tenant.dict()
            )

    async def login_user(self, request: auth.LoginRequest) -> auth.AuthResponse:
        """Authenticate user and return JWT token"""
        # Get user from database
        user = await self.db.fetchrow(
            """
            SELECT u.*, t.*, u.user_id as user_id
            FROM users u
            JOIN tenants t ON u.tenant_id = t.tenant_id
            WHERE u.email = $1
            """,
            request.email
        )
        
        if not user or not self.verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user['is_active'] or not user['tenant_is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        # Create token
        token_data = auth.TokenData(
            user_id=user['user_id'],
            tenant_id=user['tenant_id'],
            email=user['email'],
            role=auth.UserRole(user['role'])
        )
        access_token = self.create_access_token(token_data)

        # Convert user and tenant to dict for response
        user_info = {
            'user_id': user['user_id'],
            'email': user['email'],
            'role': user['role'],
            'is_active': user['is_active'],
            'created_at': user['created_at']
        }
        
        tenant_info = {
            'tenant_id': user['tenant_id'],
            'name': user['name'],
            'plan': user['plan'],
            'is_active': user['tenant_is_active'],
            'created_at': user['tenant_created_at']
        }

        return auth.AuthResponse(
            access_token=access_token,
            user=user_info,
            tenant=tenant_info
        )

    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> auth.TokenData:
        """Dependency to get current user from JWT token"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        return self.verify_token(token)

    async def get_current_tenant_info(
        self, 
        current_user: auth.TokenData = Depends(get_current_user)
    ) -> Tuple[auth.TokenData, auth.TenantInfo]:
        """Dependency to get current user and tenant info"""
        # Get tenant info from database
        tenant = await self.db.fetchrow(
            "SELECT * FROM tenants WHERE tenant_id = $1", 
            current_user.tenant_id
        )
        
        if not tenant or not tenant['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not found or inactive"
            )
            
        tenant_info = auth.TenantInfo(
            tenant_id=tenant['tenant_id'],
            name=tenant['name'],
            plan=auth.PlanType(tenant['plan']),
            stripe_customer_id=tenant.get('stripe_customer_id'),
            api_calls_quota=tenant['api_calls_quota'],
            llm_tokens_quota=tenant['llm_tokens_quota'],
            is_active=tenant['is_active'],
            created_at=tenant['created_at']
        )
        
        return current_user, tenant_info
