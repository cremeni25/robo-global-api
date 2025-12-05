import os
from supabase import create_client, Client


class SupabaseConfigError(Exception):
    """Erro de configuração do Supabase."""
    pass


_supabase_client: Client | None = None


def get_supabase() -> Client:
    """
    Retorna uma instância global do cliente Supabase.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise SupabaseConfigError("Variáveis SUPABASE_URL ou SUPABASE_KEY não configuradas.")

    _supabase_client = create_client(url, key)
    return _supabase_client


def fetch_one(table: str, **filters):
    """
    Busca a primeira linha que corresponder aos filtros.
    """
    client = get_supabase()
    query = client.table(table).select("*")

    for k, v in filters.items():
        query = query.eq(k, v)

    data = query.limit(1).execute().data
    return data[0] if data else None


def fetch_all(table: str, **filters):
    """
    Busca todas as linhas que corresponderem aos filtros.
    """
    client = get_supabase()
    query = client.table(table).select("*")

    for k, v in filters.items():
        query = query.eq(k, v)

    return query.execute().data or []


def insert_row(table: str, row: dict):
    """
    Insere uma linha na tabela especificada.
    """
    client = get_supabase()
    result = client.table(table).insert(row).execute()
    return result.data
