from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from supabase_client_new import get_supabase

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos usando Supabase.",
    version="3.0.0"
)

# ------------------------------------------------------------
# MODELOS
# ------------------------------------------------------------

class AtualizarPayload(BaseModel):
    id_produto: str
    metrica: str
    valor: float

# ------------------------------------------------------------
# ENDPOINT: STATUS
# ------------------------------------------------------------
@app.get("/status")
def status():
    return {"status": "ok"}

# ------------------------------------------------------------
# ENDPOINT: LISTAR PRODUTOS
# ------------------------------------------------------------
@app.get("/produtos")
def listar_produtos():
    db = get_supabase()
    result = db.table("produtos").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhum produto encontrado")

    return result.data

# ------------------------------------------------------------
# ENDPOINT: ATUALIZAR MÉTRICA
# ------------------------------------------------------------
@app.post("/atualizar")
def atualizar_metrica(payload: AtualizarPayload):
    db = get_supabase()

    # 1) Verifica se o produto existe
    produto = db.table("produtos").select("*").eq("id_produto", payload.id_produto).execute()
    if not produto.data:
        raise HTTPException(404, "Produto não encontrado")

    # 2) Insere registro na tabela metrica_historica
    db.table("metrica_historica").insert({
        "id_produto": payload.id_produto,
        "metrica": payload.metrica,
        "valor": payload.valor
    }).execute()

    return {"status": "ok", "mensagem": "Métrica registrada com sucesso"}

# ------------------------------------------------------------
# ENDPOINT: RANKING (SIMPLIFICADO)
# ------------------------------------------------------------
@app.get("/ranking")
def ranking():
    db = get_supabase()
    result = db.table("metrica_historica").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhuma métrica encontrada")

    ranking = sorted(result.data, key=lambda x: x["valor"], reverse=True)
    return ranking

# ------------------------------------------------------------
# ENDPOINT: PONTUAÇÃO (SIMPLIFICADO)
# ------------------------------------------------------------
@app.get("/pontuacao")
def pontuacao():
    db = get_supabase()
    result = db.table("metrica_historica").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhuma métrica encontrada")

    scores = {}
    for row in result.data:
        pid = row["id_produto"]
        scores[pid] = scores.get(pid, 0) + row["valor"]

    return scores
