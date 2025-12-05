from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import supabase
import os

# Inicialização da API
app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos usando Supabase.",
    version="3.0.0"
)

# Conexão com Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Erro: Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")

client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Endpoint de status
@app.get("/status")
def status():
    return {"status": "ok"}

# Endpoint para listar produtos
@app.get("/produtos")
def listar_produtos():
    try:
        response = client.table("produtos").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de atualização de métricas
class AtualizarPayload(BaseModel):
    id_produto: str
    metrica: str
    valor: float

@app.post("/atualizar")
def atualizar(payload: AtualizarPayload):
    try:
        # Validar se produto existe
        produto = client.table("produtos").select("*").eq("id_produto", payload.id_produto).execute()
        if not produto.data:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        # Buscar métrica na tabela plataforma_metrica
        metrica = client.table("plataforma_metrica").select("*").eq("nome_metrica", payload.metrica).execute()
        if not metrica.data:
            raise HTTPException(status_code=400, detail=f"Métrica '{payload.metrica}' não cadastrada.")

        # Inserir no histórico
        insert_data = {
            "id_produto": payload.id_produto,
            "nome_metrica": payload.metrica,
            "valor": payload.valor,
        }
        client.table("metrica_historica").insert(insert_data).execute()

        return {"status": "ok", "mensagem": "Métrica atualizada com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint ranking
@app.get("/ranking")
def ranking():
    try:
        response = client.rpc("calcular_ranking").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint pontuação
@app.get("/pontuacao")
def pontuacao():
    try:
        response = client.rpc("calcular_pontuacao").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
