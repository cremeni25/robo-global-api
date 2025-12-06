from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any
from supabase_client import get_supabase, get_config


app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos usando Supabase.",
    version="4.0.0"
)

# ------------------------------------------------------------
# MODELAGEM DO PAYLOAD /atualizar
# ------------------------------------------------------------

class AtualizarPayload(BaseModel):
    id_produto: str
    cliques: Optional[float] = None
    vendas: Optional[float] = None
    conversao: Optional[float] = None
    cpc: Optional[float] = None
    roi: Optional[float] = None
    referencia_data: Optional[date] = None


# ------------------------------------------------------------
# ENDPOINT STATUS
# ------------------------------------------------------------

@app.get("/status")
async def status():
    try:
        supabase = get_supabase()
        supabase.table("produtos").select("id_produto").limit(1).execute()
        return {"status": "ok", "supabase": "conectado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# ENDPOINT /produtos
# ------------------------------------------------------------

@app.get("/produtos")
async def listar_produtos():
    supabase = get_supabase()
    result = supabase.table("produtos").select("*").execute()
    return result.data


# ------------------------------------------------------------
# ENDPOINT /atualizar  (INSERÇÃO DE MÉTRICAS)
# ------------------------------------------------------------

@app.post("/atualizar")
async def atualizar_metricas(payload: AtualizarPayload):

    supabase = get_supabase()

    id_produto = payload.id_produto
    referencia = payload.referencia_data or date.today()

    metricas_recebidas = {
        "CLIQUES": payload.cliques,
        "VENDAS": payload.vendas,
        "CONVERSAO": payload.conversao,
        "CPC": payload.cpc,
        "ROI": payload.roi
    }

    # 1) Carregar catálogo de métricas
    catalogo = supabase.table("metricas_tipo").select("*").execute()
    mapa_metricas = {m["codigo"]: m["id"] for m in catalogo.data}

    processadas = []

    # 2) Inserir ou atualizar métricas
    for codigo, valor in metricas_recebidas.items():

        if valor is None:
            continue

        if codigo not in mapa_metricas:
            raise HTTPException(
                status_code=400,
                detail=f"Métrica {codigo} não cadastrada no Supabase"
            )

        id_metrica = mapa_metricas[codigo]

        supabase.table("produto_metrica_historico").upsert({
            "id_produto": id_produto,
            "id_metrica": id_metrica,
            "valor": valor,
            "referencia_data": referencia
        }, on_conflict=["id_produto", "id_metrica", "referencia_data"]).execute()

        processadas.append({codigo: "ok"})

    return {
        "status": "sucesso",
        "referencia_data": str(referencia),
        "metricas": processadas
    }


# ------------------------------------------------------------
# ENDPOINT /pontuacao (CALCULA PONTUAÇÃO DO PRODUTO)
# ------------------------------------------------------------

@app.get("/pontuacao/{id_produto}")
async def calcular_pontuacao(id_produto: str):

    supabase = get_supabase()

    # 1) Buscar histórico
    historico = supabase.table("produto_metrica_historico").select("*").eq("id_produto", id_produto).execute()
    metricas = historico.data
