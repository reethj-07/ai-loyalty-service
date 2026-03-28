"""
Authentication API Endpoints
Handles user registration, login, logout, and token refresh
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
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
    refresh_token: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class AuthResponse(BaseModel):
    user: dict
    session: dict


AUTH_ACCESS_COOKIE = "access_token"
AUTH_REFRESH_COOKIE = "refresh_token"


def _cookie_settings() -> dict:
    secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    samesite = os.getenv("COOKIE_SAMESITE", "lax")
    domain = os.getenv("COOKIE_DOMAIN", "").strip() or None
    return {
        "secure": secure,
        "httponly": True,
        "samesite": samesite,
        "domain": domain,
        "path": "/",
    }


def _set_auth_cookies(response: JSONResponse, session: dict):
    settings = _cookie_settings()
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    expires_in = int(session.get("expires_in") or 0)

    if access_token:
        response.set_cookie(
            key=AUTH_ACCESS_COOKIE,
            value=access_token,
            max_age=expires_in if expires_in > 0 else None,
            **settings,
        )

    if refresh_token:
        response.set_cookie(
            key=AUTH_REFRESH_COOKIE,
            value=refresh_token,
            max_age=60 * 60 * 24 * 14,
            **settings,
        )


def _clear_auth_cookies(response: JSONResponse):
    settings = _cookie_settings()
    response.delete_cookie(key=AUTH_ACCESS_COOKIE, path=settings["path"], domain=settings["domain"])
    response.delete_cookie(key=AUTH_REFRESH_COOKIE, path=settings["path"], domain=settings["domain"])


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

    response = JSONResponse(content=result)
    if result.get("session"):
        _set_auth_cookies(response, result["session"])
    return response


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

    response = JSONResponse(content=result)
    if result.get("session"):
        _set_auth_cookies(response, result["session"])
    return response


@router.post("/signout")
async def sign_out(request: Request):
    """
    Sign out current user

    Invalidates the current session.
    Requires authentication.
    """
    bearer_token = ""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header.replace("Bearer ", "", 1).strip()

    cookie_token = request.cookies.get(AUTH_ACCESS_COOKIE, "")
    token = bearer_token or cookie_token

    if token:
        try:
            await auth_service.sign_out(token)
        except Exception:
            pass

    response = JSONResponse(content={"message": "Signed out successfully"})
    _clear_auth_cookies(response)
    return response


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, http_request: Request):
    """
    Refresh access token

    Use refresh token to get a new access token when it expires.
    """
    refresh_token_value = (request.refresh_token or "").strip() or http_request.cookies.get(AUTH_REFRESH_COOKIE, "")
    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    result = await auth_service.refresh_session(refresh_token_value)
    response = JSONResponse(content=result)
    if result.get("session"):
        _set_auth_cookies(response, result["session"])
    return response


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset link.

    Always returns a generic success message to prevent account enumeration.
    """
    return await auth_service.request_password_reset(request.email)


@router.get("/me")
async def get_me(request: Request):
    """
    Get current authenticated user

    Returns information about the currently authenticated user.
    Requires authentication.
    """
    auth_header = request.headers.get("Authorization", "")
    bearer_token = auth_header.replace("Bearer ", "", 1).strip() if auth_header.startswith("Bearer ") else ""
    cookie_token = request.cookies.get(AUTH_ACCESS_COOKIE, "").strip()
    token = bearer_token or cookie_token

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await auth_service.get_current_user(token)


@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    return {
        "status": "ok",
        "service": "authentication",
        "provider": "supabase"
    }
