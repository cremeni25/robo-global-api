from supabase import create_client
import os

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Variáveis SUPABASE_URL e SUPABASE_KEY não configuradas.")

    return create_client(url, key)
