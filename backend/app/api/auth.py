from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..models import auth
from ..services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()

def get_auth_service():
    return AuthService()

@router.post("/register", response_model=auth.AuthResponse)
async def register(
    request: auth.RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user and tenant"""
    try:
        return await auth_service.register_user(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=auth.AuthResponse)
async def login(
    request: auth.LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and get access token"""
    try:
        return await auth_service.login_user(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=dict)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user information"""
    try:
        user = await auth_service.get_current_user(credentials)
        return {"user_id": user.user_id, "email": user.email, "role": user.role}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user information"
        )

@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    try:
        # In a real implementation, validate the refresh token here
        # and issue a new access token
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Token refresh not implemented"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user (invalidate token)"""
    # In a real implementation, you'd add the token to a blacklist
    return {"message": "Successfully logged out"}
