import os
from functools import lru_cache
from typing import Any

from supabase import create_client, Client


class SupabaseConfigError(Exception):
    """Erro de configuração do Supabase."""


@lru_cache
def get_supabase() -> Client:
    """
    Retorna uma instância única do cliente Supabase.
    Certifique-se de definir SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise SupabaseConfigError(
            "SUPABASE_URL e/ou SUPABASE_KEY não configurados nas variáveis de ambiente."
        )

    return create_client(url, key)


def fetch_one(table: str, **filters: Any) -> dict | None:
    """
    Busca um único registro em uma tabela usando filtros de igualdade.
    Retorna None se não encontrar.
    """
    client = get_supabase()
    query = client.table(table).select("*")

    for col, value in filters.items():
        query = query.eq(col, value)

    resp = query.limit(1).execute()
    data = resp.data or []

    if not data:
        return None
    return data[0]


def fetch_all(table: str, **filters: Any) -> list[dict]:
    """
    Busca múltiplos registros em uma tabela usando filtros de igualdade.
    """
    client = get_supabase()
    query = client.table(table).select("*")

    for col, value in filters.items():
        query = query.eq(col, value)

    resp = query.execute()
    return resp.data or []


def insert_row(table: str, row: dict) -> dict:
    """
    Insere uma linha em uma tabela e retorna o registro criado.
    """
    client = get_supabase()
    resp = client.table(table).insert(row).execute()
    data = resp.data or []
    return data[0] if data else {}
