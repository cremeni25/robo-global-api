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
async def atualizar_metricas(payload: AtualizarPayload):

    supabase = get_supabase()

    id_produto = payload.id_produto
    referencia_data = payload.referencia_data or date.today()

    metricas_payload = {
        "CLIQUES": payload.cliques,
        "VENDAS": payload.vendas,
        "CONVERSAO": payload.conversao,
        "CPC": payload.cpc,
        "ROI": payload.roi
    }

    # 1) Buscar catálogo de métricas
    metricas_tipo = supabase.table("metricas_tipo").select("*").execute().data
    mapa_metricas = {m["codigo"]: m["id"] for m in metricas_tipo}

    results = []

    for codigo, valor in metricas_payload.items():
        if valor is None:
            continue  # só grava se tiver valor enviado

        if codigo not in mapa_metricas:
            raise HTTPException(
                status_code=400,
                detail=f"Métrica {codigo} não cadastrada no banco."
            )

        id_metrica = mapa_metricas[codigo]

        # 2) Upsert para histórico
        supabase.table("produto_metrica_historico").upsert({
            "id_produto": id_produto,
            "id_metrica": id_metrica,
            "valor": valor,
            "referencia_data": referencia_data
        }, on_conflict=["id_produto", "id_metrica", "referencia_data"]).execute()

        results.append({codigo: "ok"})

    return {
        "status": "sucesso",
        "referencia_data": str(referencia_data),
        "metricas_processadas": results
    }


# -----------------------------
# RANKING (SIMPLIFICADO)
# -----------------------------
@app.get("/ranking")
def ranking():
    db = get_supabase()
    result = db.table("metricas").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhuma métrica encontrada")

    # Agrupar por produto e somar valores
    scores = {}
    for row in result.data:
        pid = row["id_produto"]
        scores[pid] = scores.get(pid, 0) + float(row["valor"])

    # Transformar em lista ordenada
    ranking = [
        {"id_produto": pid, "score_total": total}
        for pid, total in scores.items()
    ]

    ranking.sort(key=lambda x: x["score_total"], reverse=True)

    return ranking

# ------------------------------------------------------------
# ENDPOINT: PONTUAÇÃO (EVOLUÍDO)
# ------------------------------------------------------------
@app.get("/pontuacao")
def pontuacao():
    db = get_supabase()
    result = db.table("metricas").select("*").execute()

    if not result.data:
        raise HTTPException(404, "Nenhuma métrica encontrada")

    scores = {}

    # Agrupa e soma valores por produto
    for row in result.data:
        pid = row["id_produto"]
        valor = row.get("valor", 0)

        if valor is None:
            valor = 0

        scores[pid] = scores.get(pid, 0) + valor

    # Formatar resultado
    resposta = [
        {"id_produto": pid, "score_total": round(total, 2)}
        for pid, total in scores.items()
    ]

    # Ordenar por score (decrescente)
    resposta = sorted(resposta, key=lambda x: x["score_total"], reverse=True)

    return resposta


