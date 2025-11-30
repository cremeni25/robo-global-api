from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from supabase_client import get_supabase, get_config


app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos de afiliados usando Supabase.",
    version="1.0.0",
)


class AtualizarPayload(BaseModel):
    """Corpo opcional para o endpoint /atualizar."""
    limite_produtos: Optional[int] = None
    forcar_recalculo: Optional[bool] = True


def _fetch_all(table_or_view: str, order: Optional[str] = None, desc: bool = False, limit: Optional[int] = None):
    """Função utilitária genérica para buscar dados no Supabase."""
    supabase = get_supabase()
    query = supabase.table(table_or_view).select("*")

    if order:
        query = query.order(order, desc=desc)
    if limit:
        query = query.limit(limit)

    response = query.execute()
    if response.error:
        raise HTTPException(status_code=500, detail=response.error.message)
    return response.data


@app.get("/status")
def status() -> Dict[str, Any]:
    """Verifica se a API está no ar e se as variáveis mínimas estão configuradas."""
    cfg = get_config()
    return {
        "status": "ok",
        "servico": "robo-global-afiliados",
        "supabase_url_definida": bool(cfg.get("SUPABASE_URL")),
        "supabase_table_produtos": cfg.get("SUPABASE_TABLE_PRODUTOS"),
        "supabase_view_ranking": cfg.get("SUPABASE_VIEW_RANKING"),
        "supabase_view_pontuacao": cfg.get("SUPABASE_VIEW_PONTUACAO"),
    }


@app.get("/produtos")
def listar_produtos(limit: Optional[int] = None):
    """Retorna a lista de produtos brutos da tabela principal."""
    cfg = get_config()
    tabela = cfg.get("SUPABASE_TABLE_PRODUTOS")
    if not tabela:
        raise HTTPException(status_code=500, detail="Variável SUPABASE_TABLE_PRODUTOS não configurada.")

    return _fetch_all(tabela, order=cfg.get("SUPABASE_ORDER_PRODUTOS") or None, desc=True, limit=limit)


@app.get("/ranking")
def ranking_global(limit: Optional[int] = 20):
    """Retorna o ranking global de produtos (já calculado em view do Supabase)."""
    cfg = get_config()
    view = cfg.get("SUPABASE_VIEW_RANKING")
    if not view:
        raise HTTPException(status_code=500, detail="Variável SUPABASE_VIEW_RANKING não configurada.")

    # assumindo que a view já está ordenada por score, mas se tiver coluna, use SUPABASE_ORDER_RANKING
    order_col = cfg.get("SUPABASE_ORDER_RANKING")
    return _fetch_all(view, order=order_col, desc=True if order_col else False, limit=limit)


@app.get("/pontuacao")
def pontuacao_detalhada(limit: Optional[int] = 50):
    """Retorna detalhes de pontuação de cada produto (view ou tabela específica)."""
    cfg = get_config()
    view = cfg.get("SUPABASE_VIEW_PONTUACAO")
    if not view:
        raise HTTPException(status_code=500, detail="Variável SUPABASE_VIEW_PONTUACAO não configurada.")

    order_col = cfg.get("SUPABASE_ORDER_PONTUACAO")
    return _fetch_all(view, order=order_col, desc=True if order_col else False, limit=limit)


@app.post("/atualizar")
def atualizar_scores(payload: AtualizarPayload):
    """Dispara uma função RPC do Supabase para recalcular scores/ranking."""
    cfg = get_config()
    fn = cfg.get("SUPABASE_FUNCTION_ATUALIZAR")
    if not fn:
        raise HTTPException(status_code=500, detail="Variável SUPABASE_FUNCTION_ATUALIZAR não configurada.")

    supabase = get_supabase()
    params = {}
    if payload.limite_produtos is not None:
        params["limite_produtos"] = payload.limite_produtos
    if payload.forcar_recalculo is not None:
        params["forcar_recalculo"] = payload.forcar_recalculo

    response = supabase.rpc(fn, params=params).execute()
    if response.error:
        raise HTTPException(status_code=500, detail=response.error.message)

    return {
        "status": "ok",
        "mensagem": "Processo de atualização disparado com sucesso.",
        "retorno_supabase": response.data,
    }


# Endpoint raiz opcional, só para mostrar algo amigável ao acessar a URL base.
@app.get("/")
def raiz():
    return {
        "mensagem": "API Robô Global de Afiliados ativa. Veja /docs para documentação interativa.",
        "endpoints": ["/status", "/produtos", "/ranking", "/pontuacao", "/atualizar"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
