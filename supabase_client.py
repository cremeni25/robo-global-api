import os
from functools import lru_cache
from typing import Dict
from supabase import create_client, Client


REQUIRED_ENV_VARS = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
]


OPTIONAL_ENV_VARS = [
    "SUPABASE_TABLE_PRODUTOS",
    "SUPABASE_VIEW_RANKING",
    "SUPABASE_VIEW_PONTUACAO",
    "SUPABASE_ORDER_PRODUTOS",
    "SUPABASE_ORDER_RANKING",
    "SUPABASE_ORDER_PONTUACAO",
    "SUPABASE_FUNCTION_ATUALIZAR",
]


@lru_cache()
def get_config() -> Dict[str, str]:
    """Lê e guarda em cache as variáveis de ambiente da aplicação."""
    cfg = {}
    for key in REQUIRED_ENV_VARS + OPTIONAL_ENV_VARS:
        cfg[key] = os.getenv(key, "").strip()
    return cfg


@lru_cache()
def get_supabase() -> Client:
    """Cria e retorna um cliente Supabase usando variáveis de ambiente."""
    cfg = get_config()

    missing = [k for k in REQUIRED_ENV_VARS if not cfg.get(k)]
    if missing:
        raise RuntimeError(
            f"As seguintes variáveis de ambiente obrigatórias não estão definidas: {', '.join(missing)}"
        )

    url = cfg["SUPABASE_URL"]
    key = cfg["SUPABASE_KEY"]
    client: Client = create_client(url, key)
    return client
