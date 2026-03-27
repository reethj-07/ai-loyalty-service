"""
Supabase Client Configuration
Manages connection to Supabase database
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

load_dotenv()


class SupabaseClient:
    _instance: Optional[Client] = None
    _admin_instance: Optional[Client] = None

    @classmethod
    def get_client(cls, use_service_key: bool = False) -> Client:
        """
        Get or create Supabase client instance (singleton pattern)

        Args:
            use_service_key: If True, uses service_role key (bypasses RLS)
                           If False, uses anon key (respects RLS)
        """
        if use_service_key:
            # Use admin client with service key for write operations
            if cls._admin_instance is None:
                url = os.environ.get("SUPABASE_URL")
                key = os.environ.get("SUPABASE_SERVICE_KEY")

                if not url or not key:
                    raise ValueError(
                        "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
                    )

                cls._admin_instance = create_client(url, key)

            return cls._admin_instance
        else:
            # Use regular client with anon key for read operations
            if cls._instance is None:
                url = os.environ.get("SUPABASE_URL")
                key = os.environ.get("SUPABASE_ANON_KEY")

                if not url or not key:
                    raise ValueError(
                        "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
                    )

                cls._instance = create_client(url, key)

            return cls._instance

    @classmethod
    def reset(cls):
        """Reset client instance (useful for testing)"""
        cls._instance = None
        cls._admin_instance = None


# Export singleton getter
def get_supabase(use_service_key: bool = False) -> Client:
    """
    Get Supabase client instance

    Args:
        use_service_key: If True, uses service_role key (bypasses RLS) for admin operations
                       If False, uses anon key (respects RLS) for regular operations
    """
    return SupabaseClient.get_client(use_service_key=use_service_key)

# Create a lazy supabase object that initializes on first access
class _SupabaseProxy:
    """Lazy proxy for Supabase client"""
    def __getattr__(self, name):
        client = get_supabase()
        return getattr(client, name)

supabase = _SupabaseProxy()
