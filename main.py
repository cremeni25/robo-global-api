from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from supabase_client_new import get_supabase

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos usando Supabase.",
    version="3.1.0"
)

# -----------------------------
# MODELO DO PAYLOAD
# -----------------------------
class AtualizarPayload(BaseModel):
    id_produto: str
    metrica: str
    valor: float

# -----------------------------
# STATUS
# -----------------------------
@app.get("/status")
def status():
    return {"status": "ok"}

# -----------------------------
# LISTAR PRODUTOS
# -----------------------------
@app.get("/produtos")
def listar_produtos():
    db = get_supabase()
    result = db.table("produtos").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhum produto encontrado")
    
    return result.data

# -----------------------------
# ATUALIZAR MÉTRICA
# -----------------------------
@app.post("/atualizar")
def atualizar_metrica(payload: AtualizarPayload):
    db = get_supabase()

    # 1 — Verificar se produto existe
    produto = db.table("produtos").select("*").eq("id_produto", payload.id_produto).execute()
    if not produto.data:
        raise HTTPException(404, "Produto não encontrado")

    # 2 — Inserir ou atualizar métrica
    db.table("metricas").upsert({
        "id_produto": payload.id_produto,
        "metrica": payload.metrica,
        "valor": payload.valor
    }).execute()

    return {"status": "ok", "mensagem": "Métrica atualizada"}

# -----------------------------
# RANKING (SIMPLIFICADO)
# -----------------------------
@app.get("/ranking")
def ranking():
    db = get_supabase()
    result = db.table("metricas").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhuma métrica encontrada")

    ranking = sorted(result.data, key=lambda x: x["valor"], reverse=True)

    return ranking

# -----------------------------
# PONTUAÇÃO (SIMPLIFICADA)
# -----------------------------
@app.get("/pontuacao")
def pontuacao():
    db = get_supabase()
    result = db.table("metricas").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhuma métrica encontrada")

    scores = {}
    for row in result.data:
        pid = row["id_produto"]
        scores[pid] = scores.get(pid, 0) + row["valor"]

    return scores
