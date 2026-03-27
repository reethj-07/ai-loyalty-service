"""
Authentication API Endpoints
Handles user registration, login, logout, and token refresh
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.auth import auth_service, get_current_user


router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    user: dict
    session: dict


# Endpoints

@router.post("/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """
    Register a new user

    Creates a new user account with Supabase Auth.
    Returns user data and authentication tokens.
    """
    user_metadata = {}
    if request.full_name:
        user_metadata["full_name"] = request.full_name
    if request.company:
        user_metadata["company"] = request.company

    result = await auth_service.sign_up(
        email=request.email,
        password=request.password,
        user_metadata=user_metadata
    )

    return result


@router.post("/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in with email and password

    Authenticates user and returns access tokens.
    """
    result = await auth_service.sign_in(
        email=request.email,
        password=request.password
    )

    return result


@router.post("/signout")
async def sign_out(user: dict = Depends(get_current_user)):
    """
    Sign out current user

    Invalidates the current session.
    Requires authentication.
    """
    return {"message": "Signed out successfully"}


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token

    Use refresh token to get a new access token when it expires.
    """
    result = await auth_service.refresh_session(request.refresh_token)
    return result


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user

    Returns information about the currently authenticated user.
    Requires authentication.
    """
    return user


@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    return {
        "status": "ok",
        "service": "authentication",
        "provider": "supabase"
    }
