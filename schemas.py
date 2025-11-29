from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProdutoCreate(BaseModel):
    nome: str
    plataforma: str
    pais: str
    nicho: Optional[str] = None
    preco: Optional[float] = None
    comissao_percentual: Optional[float] = None
    comissao_valor: Optional[float] = None
    link_venda: Optional[str] = None
    link_afiliado: Optional[str] = None
    moeda: Optional[str] = "BRL"
    ativo: Optional[bool] = True

class ProdutoOut(BaseModel):
    id_produto: UUID
    nome: str
    plataforma: str
    pais: str
    nicho: Optional[str]
    preco: Optional[float]

    class Config:
        orm_mode = True

class MetricasPlataformaCreate(BaseModel):
    id_produto: UUID
    epc: Optional[float] = None
    cvr: Optional[float] = None
    refund: Optional[float] = None
    vendas_7d: Optional[int] = None
    vendas_30d: Optional[int] = None
    gravidade: Optional[float] = None
    tickets_suporte: Optional[int] = None

class RankingItem(BaseModel):
    nome: str
    plataforma: str
    pais: str
    score_global_final: float
