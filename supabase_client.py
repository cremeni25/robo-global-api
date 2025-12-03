import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client


class SupabaseConfigError(Exception):
    pass


_supabase_client: Optional[Client] = None


def get_config() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise SupabaseConfigError(
            "Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas."
        )
    return url, key


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url, key = get_config()
        _supabase_client = create_client(url, key)
    return _supabase_client


def fetch_one(table: str, **filters: Any) -> Optional[Dict[str, Any]]:
    client = get_supabase()
    query = client.table(table).select("*")
    for col, val in filters.items():
        query = query.eq(col, val)
    data = query.limit(1).execute().data or []
    return data[0] if data else None


def fetch_all(table: str, **filters: Any) -> List[Dict[str, Any]]:
    client = get_supabase()
    query = client.table(table).select("*")
    for col, val in filters.items():
        query = query.eq(col, val)
    return query.execute().data or []


def insert_row(table: str, row: Dict[str, Any]) -> Dict[str, Any]:
    client = get_supabase()
    res = client.table(table).insert(row).execute()
    if not res.data:
        raise RuntimeError(f"Falha ao inserir em {table}.")
    return res.data[0]
