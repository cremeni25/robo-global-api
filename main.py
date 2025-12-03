from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from supabase_client import (
    get_supabase,
    fetch_one,
    fetch_all,
    insert_row,
    SupabaseConfigError,
)

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos de afiliados usando Supabase.",
    version="2.0.0",
)

# ==========================
# MODELOS Pydantic
# ==========================


class AtualizarMetricasPayload(BaseModel):
    """
    Payload para atualizar métricas externas de um produto.
    A API calcula e registra as métricas internas (scores).
    """
    id_produto: str = Field(..., description="UUID do produto na tabela produtos.")
    metricas: Dict[str, float] = Field(
        ...,
        description=(
            "Chave = nome da métrica (CLIQUES, VENDAS, CPC, ROI, CONVERSAO opcional), "
            "Valor = número."
        ),
    )


class Produto(BaseModel):
    id_produto: str
    nome_produto: Optional[str] = None
    plataforma: Optional[str] = None
    ativo: Optional[bool] = None


class RankingItem(BaseModel):
    id_produto: str
    nome_produto: Optional[str] = None
    plataforma: Optional[str] = None
    score_global_final: float
    score_qualidade: Optional[float] = None
    score_performance: Optional[float] = None


class StatusResponse(BaseModel):
    status: str
    detalhes: Optional[str] = None


# ==========================
# CONSTANTES DE MÉTRICAS
# ==========================

METRICAS_EXTERNAS = ["CLIQUES", "VENDAS", "CONVERSAO", "CPC", "ROI"]
METRICAS_INTERNAS = ["SCORE_QUALIDADE", "SCORE_PERFORMANCE", "SCORE_GLOBAL_FINAL"]


# ==========================
# FUNÇÕES AUXILIARES
# ==========================


def get_produto_or_404(id_produto: str) -> dict:
    produto = fetch_one("produtos", id_produto=id_produto)
    if not produto:
        raise HTTPException(
            status_code=404, detail=f"Produto {id_produto} não encontrado."
        )
    return produto


def get_plataforma_metrica(id_produto: str, nome_metrica: str) -> dict:
    """
    Busca o cadastro da métrica na tabela plataforma_metrica
    sem diferenciar maiúsculas/minúsculas.
    """
    nome_normalizado = nome_metrica.strip().lower()

    # Busca todas as métricas do produto
    rows = fetch_all(
        "plataforma_metrica",
        id_produto=id_produto,
    )

    if not rows:
        raise HTTPException(
            status_code=400,
            detail=f"Nenhuma métrica encontrada para o produto {id_produto}.",
        )

    # Valida ignorando maiúsculas/minúsculas
    for row in rows:
        if row["nome_metrica"].strip().lower() == nome_normalizado:
            return row

    raise HTTPException(
        status_code=400,
        detail=f"Métrica '{nome_metrica}' não cadastrada para o produto {id_produto}.",
    )



def registrar_valor_metrica(id_plataforma_metrica: str, valor: float) -> None:
    """
    Insere um novo registro em metrica_historica para uma métrica específica.
    """
    row = {
        "id_plataforma_metrica": id_plataforma_metrica,
        "valor_numero": float(valor),
    }
    insert_row("metrica_historica", row)


def get_ultimo_valor_score(
    id_produto: str, nome_metrica: str
) -> Optional[float]:
    """
    Busca o último valor registrado em metrica_historica
    para uma métrica interna (score) de um produto.
    """
    client = get_supabase()

    # 1) pega o cadastro da métrica interna para o produto
    pm_rows = (
        client.table("plataforma_metrica")
        .select("id_plataforma_metrica")
        .eq("id_produto", id_produto)
        .eq("nome_metrica", nome_metrica)
        .execute()
        .data
        or []
    )

    if not pm_rows:
        return None

    id_pm = pm_rows[0]["id_plataforma_metrica"]

    # 2) pega o último histórico
    hist_rows = (
        client.table("metrica_historica")
        .select("valor_numero, coletado_em")
        .eq("id_metrica_historica", None)  # apenas para evitar erro de lint
    )  # este trecho será sobrescrito abaixo

    hist_rows = (
        client.table("metrica_historica")
        .select("valor_numero, coletado_em")
        .eq("id_plataforma_metrica", id_pm)
        .order("coletado_em", desc=True)
        .limit(1)
        .execute()
        .data
        or []
    )

    if not hist_rows:
        return None

    return float(hist_rows[0]["valor_numero"])


def calcular_scores(
    cliques: float,
    vendas: float,
    cpc: float,
    roi: float,
    conversao: Optional[float] = None,
) -> Dict[str, float]:
    """
    Fórmulas de exemplo para cálculo dos scores.
    🔧 Ponto ÚNICO de ajuste: se quiser mudar a lógica do robô,
    ajuste apenas esta função.

    - CONVERSAO = VENDAS / CLIQUES (se não informado e cliques > 0)
    - SCORE_QUALIDADE: foca mais em CONVERSAO e ROI
    - SCORE_PERFORMANCE: foca em VENDAS, CLIQUES e CPC
    - SCORE_GLOBAL_FINAL: combinação dos dois

    Escala: 0 a 100 (limitado por min/max simples).
    """
    if conversao is None:
        if cliques > 0:
            conversao = vendas / cliques
        else:
            conversao = 0.0

    # Normalizações simples (exemplos, podem ser ajustadas)
    conv_pct = conversao * 100  # ex: 0.03 -> 3%
    roi_norm = roi  # assumindo já em %
    vendas_norm = vendas
    cliques_norm = cliques
    cpc_norm = cpc

    # Evitar divisões por zero
    if cpc_norm <= 0:
        cpc_norm = 0.01

    # Qualidade: quanto melhor a conversão e o ROI, maior o score
    score_qualidade = (conv_pct * 0.6) + (roi_norm * 0.4)

    # Performance: mais vendas e mais cliques, com penalização por CPC alto
    score_performance = (vendas_norm * 2.0) + (cliques_norm * 0.5) - (cpc_norm * 1.5)

    # Normalização simples para não explodir:
    score_qualidade = max(0.0, min(score_qualidade, 100.0))
    score_performance = max(0.0, min(score_performance, 100.0))

    # Combinação final
    score_global = (score_qualidade * 0.4) + (score_performance * 0.6)
    score_global = max(0.0, min(score_global, 100.0))

    return {
        "CONVERSAO": conversao,
        "SCORE_QUALIDADE": score_qualidade,
        "SCORE_PERFORMANCE": score_performance,
        "SCORE_GLOBAL_FINAL": score_global,
    }


# ==========================
# ENDPOINTS
# ==========================


@app.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    try:
        _ = get_supabase()
        return StatusResponse(status="ok", detalhes="Conectado ao Supabase.")
    except SupabaseConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conectar ao Supabase: {e}",
        )


@app.get("/produtos", response_model=List[Produto])
def listar_produtos() -> List[Produto]:
    rows = fetch_all("produtos")
    return [
        Produto(
            id_produto=row["id_produto"],
            nome_produto=row.get("nome_produto"),
            plataforma=row.get("plataforma"),
            ativo=row.get("ativo"),
        )
        for row in rows
    ]


@app.post("/atualizar", response_model=Dict[str, float])
def atualizar_metricas(payload: AtualizarMetricasPayload):
    """
    Recebe métricas externas de um produto,
    grava histórico e calcula os scores internos.
    """
    produto = get_produto_or_404(payload.id_produto)

    # Extrai métricas externas com defaults seguros
    cli = float(payload.metricas.get("CLIQUES", 0))
    ven = float(payload.metricas.get("VENDAS", 0))
    cpc = float(payload.metricas.get("CPC", 0))
    roi = float(payload.metricas.get("ROI", 0))
    conv_input = payload.metricas.get("CONVERSAO")

    # 1) Registrar histórico das EXTERNAS
    for nome in METRICAS_EXTERNAS:
        if nome == "CONVERSAO" and conv_input is None:
            # Se não foi enviada, vamos calcular depois
            continue

        valor = payload.metricas.get(nome)
        if valor is None:
            # não envia histórico de métrica ausente
            continue

        pm = get_plataforma_metrica(payload.id_produto, nome)
        registrar_valor_metrica(pm["id_plataforma_metrica"], float(valor))

    # 2) Calcular CONVERSAO + SCORES internos
    scores = calcular_scores(
        cliques=cli,
        vendas=ven,
        cpc=cpc,
        roi=roi,
        conversao=float(conv_input) if conv_input is not None else None,
    )

    # 3) Registrar histórico das métricas internas (incluindo CONVERSAO)
    #    CONVERSAO pode ser considerada "externa derivada" ou interna – aqui gravamos de qualquer forma.
    for nome in ["CONVERSAO"] + METRICAS_INTERNAS:
        valor = scores[nome]
        pm = get_plataforma_metrica(payload.id_produto, nome)
        registrar_valor_metrica(pm["id_plataforma_metrica"], float(valor))

    # 4) Retorna apenas os scores finais calculados (inclui conversão)
    return scores


@app.get("/ranking", response_model=List[RankingItem])
def get_ranking() -> List[RankingItem]:
    """
    Monta ranking com base no último SCORE_GLOBAL_FINAL de cada produto.
    """
    client = get_supabase()

    # 1) Busca todas as métricas SCORE_GLOBAL_FINAL
    pm_rows = (
        client.table("plataforma_metrica")
        .select("id_plataforma_metrica, id_produto")
        .eq("nome_metrica", "SCORE_GLOBAL_FINAL")
        .execute()
        .data
        or []
    )

    if not pm_rows:
        return []

    ranking_tmp = []

    # 2) Para cada métrica, pega o último histórico
    for pm in pm_rows:
        id_pm = pm["id_plataforma_metrica"]
        id_prod = pm["id_produto"]

        hist_rows = (
            client.table("metrica_historica")
            .select("valor_numero, coletado_em")
            .eq("id_plataforma_metrica", id_pm)
            .order("coletado_em", desc=True)
            .limit(1)
            .execute()
            .data
            or []
        )

        if not hist_rows:
            continue

        score_val = float(hist_rows[0]["valor_numero"])
        ranking_tmp.append((id_prod, score_val))

    if not ranking_tmp:
        return []

    # 3) Busca dados dos produtos em um único select
    ids_produtos = list({p[0] for p in ranking_tmp})

    produtos_rows = (
        client.table("produtos")
        .select("id_produto, nome_produto, plataforma")
        .in_("id_produto", ids_produtos)
        .execute()
        .data
        or []
    )

    produtos_map = {p["id_produto"]: p for p in produtos_rows}

    # 4) Monta lista final e ordena por score desc
    ranking_items: List[RankingItem] = []

    # Opcional: pegar também os últimos SCORE_QUALIDADE e SCORE_PERFORMANCE
    for id_prod, score_global in ranking_tmp:
        prod = produtos_map.get(id_prod, {})
        score_qual = get_ultimo_valor_score(id_prod, "SCORE_QUALIDADE")
        score_perf = get_ultimo_valor_score(id_prod, "SCORE_PERFORMANCE")

        ranking_items.append(
            RankingItem(
                id_produto=id_prod,
                nome_produto=prod.get("nome_produto"),
                plataforma=prod.get("plataforma"),
                score_global_final=score_global,
                score_qualidade=score_qual,
                score_performance=score_perf,
            )
        )

    ranking_items.sort(key=lambda x: x.score_global_final, reverse=True)
    return ranking_items


@app.get("/pontuacao", response_model=List[RankingItem])
def get_pontuacao() -> List[RankingItem]:
    """
    Alias de /ranking para manter compatibilidade de contrato.
    """
    return get_ranking()
