import os
from supabase_py import create_client

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Variáveis de ambiente não configuradas.")

    return create_client(url, key)
