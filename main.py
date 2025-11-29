from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Produto, MetricasPlataforma, MetricasInteligentes
from schemas import ProdutoCreate, ProdutoOut, MetricasPlataformaCreate, RankingItem
from motor import (
    calc_lucratividade,
    calc_estabilidade,
    calc_tendencia,
    calc_risco,
    calc_score_global,
)

app = FastAPI(title="Robo Global de Recomendacao - Python")

@app.get("/")
def raiz():
    return {"status": "online", "mensagem": "Robo Global ativo"}

@app.get("/health")
def healthcheck(db: Session = Depends(get_db)):
    # apenas testa se consegue consultar algo simples
    db.execute("SELECT 1")
    return {"status": "ok"}

@app.post("/ingestao/produto", response_model=ProdutoOut)
def criar_produto(payload: ProdutoCreate, db: Session = Depends(get_db)):
    produto = Produto(**payload.dict())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto

@app.post("/ingestao/metricas")
def criar_metricas(payload: MetricasPlataformaCreate, db: Session = Depends(get_db)):
    metricas = MetricasPlataforma(**payload.dict())
    db.add(metricas)
    db.commit()

    # calcula scores inteligentes automaticamente
    luc = calc_lucratividade(metricas.comissao_valor if hasattr(metricas, "comissao_valor") else None,
                             metricas.cvr, metricas.refund)
    est = calc_estabilidade(metricas.vendas_30d, metricas.vendas_7d)
    ten = calc_tendencia(metricas.vendas_30d, metricas.vendas_7d)
    risco = calc_risco(metricas.refund)
    score_global = calc_score_global(luc, est, ten, risco)

    inteligencia = MetricasInteligentes(
        id_produto=metricas.id_produto,
        score_lucratividade=luc,
        score_estabilidade=est,
        score_tendencia=ten,
        score_risco=risco,
        score_global_final=score_global,
        selo_recomendacao="TOP" if score_global >= 80 else "OK" if score_global >= 60 else "OBSERVAR",
    )
    db.add(inteligencia)
    db.commit()

    return {"status": "ok", "score_global_final": float(score_global)}

@app.get("/ranking/top3", response_model=List[RankingItem])
def ranking_top3(db: Session = Depends(get_db)):
    query = (
        db.query(
            Produto.nome,
            Produto.plataforma,
            Produto.pais,
            MetricasInteligentes.score_global_final,
        )
        .join(MetricasInteligentes, Produto.id_produto == MetricasInteligentes.id_produto)
        .order_by(MetricasInteligentes.score_global_final.desc())
        .limit(3)
    )
    resultados = query.all()
    return [
        RankingItem(
            nome=r[0],
            plataforma=r[1],
            pais=r[2],
            score_global_final=float(r[3]),
        )
        for r in resultados
    ]
