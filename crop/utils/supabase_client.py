import os


def _get_client():
    try:
        from supabase import create_client
        from django.conf import settings
    except Exception:
        return None

    url = getattr(settings, 'SUPABASE_URL', None) or os.getenv('SUPABASE_URL')
    key = getattr(settings, 'SUPABASE_SERVICE_KEY', None) or os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


class _SupabaseProxy:
    def __getattr__(self, name):
        client = _get_client()
        if client is None:
            raise RuntimeError('Supabase client not configured')
        return getattr(client, name)


supabase = _SupabaseProxy()
