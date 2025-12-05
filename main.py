from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from db import get_conn

app = FastAPI()

class AtualizarMetricasPayload(BaseModel):
    id_produto: str
    metricas: Dict[str, float]

@app.get("/status")
def status():
    return {"status": "ok"}

# minimal template
