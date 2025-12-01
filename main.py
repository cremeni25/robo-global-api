from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from supabase_client import get_supabase

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos de afiliados usando Supabase.",
    version="1.0.0",
)


class Produto(BaseModel):
    id: int
    nome: str
    score: float


class AtualizarPayload(BaseModel):
    produtos: Optional[List[Produto]] = None


@app.get("/status")
def status():
    return {"status": "online"}


@app.get("/produtos")
def listar_produtos():
    supabase = get_supabase()
    data = supabase.table("produtos").select("*").execute()
    return data.data


@app.get("/ranking")
def ranking():
    supabase = get_supabase()
    data = supabase.table("produtos").select("*").order("score", desc=True).execute()
    return data.data


@app.get("/pontuacao/{produto_id}")
def pontuacao(produto_id: int):
    supabase = get_supabase()
    result = supabase.table("produtos").select("*").eq("id", produto_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return result.data


@app.post("/atualizar")
def atualizar(payload: AtualizarPayload):
    supabase = get_supabase()

    if not payload.produtos:
        raise HTTPException(status_code=400, detail="Nenhum produto enviado.")

    updates = []
    for p in payload.produtos:
        updates.append(
            supabase.table("produtos")
            .update({"nome": p.nome, "score": p.score})
            .eq("id", p.id)
            .execute()
        )

    return {"status": "atualizado", "itens": len(updates)}

