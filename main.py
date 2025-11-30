from fastapi import FastAPI
from supabase_client import supabase

app = FastAPI(title="Robo Global de Afiliados - API Profissional")

@app.get("/status")
def status():
    return {"status":"online","versao":"pro"}

@app.get("/produtos")
def produtos():
    return supabase.table("produtos").select("*").execute().data

@app.get("/ranking")
def ranking():
    return supabase.table("ranking").select("*").execute().data

@app.get("/pontuacao")
def pontuacao():
    return supabase.table("pontuacao").select("*").execute().data

@app.post("/atualizar")
def atualizar():
    return {"mensagem":"Função de atualização profissional ativa"} 
