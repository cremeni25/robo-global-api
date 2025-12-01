from supabase import create_client
import os


def get_supabase():
    """
    Cria e retorna um client do Supabase usando as variáveis de ambiente.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY não estão configuradas no ambiente.")

    return create_client(url, key)


def get_config():
    """
    Retorna um dicionário com todas as variáveis de configuração usadas pela API.
    """
    return {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),

        "SUPABASE_TABLE_PRODUTOS": os.getenv("SUPABASE_TABLE_PRODUTOS"),
        "SUPABASE_VIEW_RANKING": os.getenv("SUPABASE_VIEW_RANKING"),
        "SUPABASE_VIEW_PONTUACAO": os.getenv("SUPABASE_VIEW_PONTUACAO"),

        "SUPABASE_ORDER_PRODUTOS": os.getenv("SUPABASE_ORDER_PRODUTOS"),
        "SUPABASE_ORDER_RANKING": os.getenv("SUPABASE_ORDER_RANKING"),
        "SUPABASE_ORDER_PONTUACAO": os.getenv("SUPABASE_ORDER_PONTUACAO"),

        "SUPABASE_FUNCTION_ATUALIZAR": os.getenv("SUPABASE_FUNCTION_ATUALIZAR"),
    }
