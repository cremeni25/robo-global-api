from supabase import create_client
import os

# Conexão
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Função genérica para buscar dados
async def fetch_all(tabela: str, order: str = None, desc: bool = False, limit: int = None):
    try:
        query = supabase.table(tabela).select("*")

        if order:
            query = query.order(order, desc=desc)

        if limit:
            query = query.limit(limit)

        # A nova versão retorna um objeto com ".data"
        response = query.execute()

        return {
            "erro": False,
            "dados": response.data
        }

    except Exception as e:
        return {
            "erro": True,
            "mensagem": str(e)
        }
