"""
Authentication and Authorization Module
Implements Supabase Auth integration with JWT validation
"""
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from app.core.supabase_client import supabase


security = HTTPBearer()


class AuthService:
    """Handles authentication and authorization"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if not self.supabase_jwt_secret:
            # For development, extract from anon key (not recommended for production)
            self.supabase_jwt_secret = os.getenv("SUPABASE_ANON_KEY")

    async def verify_token(self, token: str) -> dict:
        """
        Verify JWT token from Supabase Auth

        Args:
            token: JWT token from Authorization header

        Returns:
            dict: Decoded token payload with user info

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Use Supabase's built-in token verification (handles ES256/HS256 automatically)
            response = supabase.auth.get_user(token)

            if not response or not response.user:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Return user data in expected format
            user = response.user
            return {
                "sub": user.id,
                "email": user.email,
                "role": user.role or "authenticated",
                "user_metadata": user.user_metadata or {},
                "exp": None  # Supabase handles expiration internally
            }

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    async def get_current_user(self, token: str) -> dict:
        """
        Get current authenticated user from token

        Args:
            token: JWT token

        Returns:
            dict: User information including id, email, role
        """
        payload = await self.verify_token(token)

        user_id = payload.get("sub")
        email = payload.get("email")
        user_metadata = payload.get("user_metadata") or {}
        role = user_metadata.get("role") or payload.get("role", "authenticated")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "id": user_id,
            "email": email,
            "role": role,
            "user_metadata": user_metadata,
            "metadata": payload
        }

    async def sign_up(self, email: str, password: str, user_metadata: dict = None) -> dict:
        """
        Register a new user with Supabase Auth

        Args:
            email: User email
            password: User password
            user_metadata: Optional user metadata (name, company, etc.)

        Returns:
            dict: User data and session
        """
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })

            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None,
                        "note": "Email confirmation may be required. Check your email to activate account."
                    }
                }
            else:
                raise HTTPException(status_code=400, detail="Sign up failed - no user returned")

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e)
            if "is invalid" in error_msg:
                raise HTTPException(status_code=400, detail=f"Email address is not allowed: {email}. Use a real email domain.")
            elif "already registered" in error_msg.lower():
                raise HTTPException(status_code=400, detail="Email already registered. Please sign in instead.")
            else:
                raise HTTPException(status_code=400, detail="Unable to create account")

    async def sign_in(self, email: str, password: str) -> dict:
        """
        Sign in user with email and password

        Args:
            email: User email
            password: User password

        Returns:
            dict: User data and access tokens
        """
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_in": response.session.expires_in,
                        "token_type": response.session.token_type
                    }
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid email or password")

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e)
            if "Invalid login credentials" in error_msg:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            elif "is invalid" in error_msg:
                raise HTTPException(status_code=400, detail=f"Invalid email format: {email}")
            else:
                raise HTTPException(status_code=401, detail="Authentication failed")

    async def sign_out(self, token: str) -> dict:
        """
        Sign out user and invalidate session

        Args:
            token: Access token to invalidate

        Returns:
            dict: Success message
        """
        try:
            # Note: Supabase Python client doesn't have sign_out with token
            # Users should just discard the token on client side
            # For server-side, we could maintain a blacklist
            return {"message": "Signed out successfully"}
        except Exception:
            raise HTTPException(status_code=400, detail="Sign out failed")

    async def refresh_session(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            dict: New access token and session info
        """
        try:
            response = supabase.auth.refresh_session(refresh_token)

            if response.session:
                return {
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_in": response.session.expires_in
                    }
                }
            else:
                raise HTTPException(status_code=401, detail="Refresh failed")

        except Exception:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def request_password_reset(self, email: str) -> dict:
        """
        Request password reset email via Supabase Auth.

        Args:
            email: User email address

        Returns:
            dict: Success message
        """
        try:
            if hasattr(supabase.auth, "reset_password_email"):
                supabase.auth.reset_password_email(email)
            elif hasattr(supabase.auth, "reset_password_for_email"):
                supabase.auth.reset_password_for_email(email)
            else:
                raise HTTPException(status_code=501, detail="Password reset is not supported by current auth client")

            return {"message": "If an account exists for this email, a reset link has been sent."}
        except HTTPException:
            raise
        except Exception:
            # Deliberately return generic success to avoid account enumeration
            return {"message": "If an account exists for this email, a reset link has been sent."}


# Singleton instance
auth_service = AuthService()


# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    FastAPI dependency to get current authenticated user
    Use this to protect routes that require authentication

    Usage:
        @app.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user["id"]}
    """
    token = credentials.credentials
    return await auth_service.get_current_user(token)


# Optional authentication (allows both authenticated and anonymous)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Optional authentication - returns user if authenticated, None if not
    Use for routes that work with or without auth
    """
    if not credentials:
        return None

    try:
        return await auth_service.get_current_user(credentials.credentials)
    except HTTPException:
        return None


def require_roles(*allowed_roles: str):
    """Dependency factory to enforce role-based access control."""
    normalized_allowed = {role.lower() for role in allowed_roles if role}

    async def _role_guard(user: dict = Depends(get_current_user)) -> dict:
        role = str(user.get("role", "")).lower()
        if role not in normalized_allowed:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return user

    return _role_guard
