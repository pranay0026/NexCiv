from typing import Optional
from supabase import create_client, Client
from config import settings

_CLIENT = None

def get_supabase() -> Optional[Client]:
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None
    try:
        _CLIENT = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return _CLIENT
    except Exception as e:
        print(f"Warning: Failed to initialize Supabase client: {e}")
        return None
