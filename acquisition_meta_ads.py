# acquisition_meta_ads.py
# ROBO GLOBAL AI — BLOCO B (ACQUISITION ENGINE — META ADS)
# Versão: 1.0
# Data: 25/12/2025
# ARQUIVO COMPLETO PARA SUBSTITUIÇÃO TOTAL
# EXECUÇÃO REAL — GASTO REAL — REGISTRO REAL

"""
REQUISITOS (ENV VARS — OBRIGATÓRIO):
- META_ACCESS_TOKEN
- META_AD_ACCOUNT_ID
- META_API_VERSION (ex: v19.0)

ORÇAMENTO:
- DAILY_BUDGET = 10.00 (moeda da conta)
- MAX_TEST_SPEND = 10.00

REGRAS:
- Cria campanha REAL
- Ativa campanha REAL
- Monitora gasto REAL
- Ao atingir o teto → PAUSA AUTOMÁTICA
- Qualquer erro → PAUSA + ERRO EXPLÍCITO
"""

import os
import time
import requests
from datetime import datetime, timezone
from typing import Dict, Any

# ================================
# CONFIGURAÇÕES OBRIGATÓRIAS
# ================================

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")
META_API_VERSION = os.getenv("META_API_VERSION", "v19.0")

DAILY_BUDGET = 10.00
MAX_TEST_SPEND = 10.00

if not META_ACCESS_TOKEN:
    raise RuntimeError("META_ACCESS_TOKEN não definido")

if not META_AD_ACCOUNT_ID:
    raise RuntimeError("META_AD_ACCOUNT_ID não definido")

META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

# ================================
# ESTADO INTERNO (REAL)
# ================================

STATE: Dict[str, Any] = {
    "status": "IDLE",
    "campaign_id": None,
    "adset_id": None,
    "started_at": None,
    "last_spend": 0.0,
    "total_spend": 0.0,
    "last_error": None,
}

# ================================
# FUNÇÕES AUXILIARES
# ================================

def _headers():
    return {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}"
    }

def _post(url: str, data: dict):
    response = requests.post(
        url,
        data=data,
        headers=_headers(),
        timeout=30
    )
    if not response.ok:
        raise RuntimeError(response.text)
    return response.json()

def _get(url: str, params: dict = None):
    response = requests.get(
        url,
        params=params or {},
        headers=_headers(),
        timeout=30
    )
    if not response.ok:
        raise RuntimeError(response.text)
    return response.json()

# ================================
# CRIAÇÃO DE CAMPANHA REAL
# ================================

def create_campaign():
    url = f"{META_BASE_URL}/act_{META_AD_ACCOUNT_ID}/campaigns"
    payload = {
        "name": "RoboGlobalAI-Test",
        "objective": "OUTCOME_TRAFFIC",
        "status": "PAUSED",
        "special_ad_categories": []
    }
    result = _post(url, payload)
    STATE["campaign_id"] = result.get("id")
    return STATE["campaign_id"]

def create_adset():
    url = f"{META_BASE_URL}/act_{META_AD_ACCOUNT_ID}/adsets"
    daily_budget_cents = int(DAILY_BUDGET * 100)

    payload = {
        "name": "RoboGlobalAI-AdSet",
        "campaign_id": STATE["campaign_id"],
        "daily_budget": daily_budget_cents,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LINK_CLICKS",
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": '{"geo_locations": {"countries": ["BR"]}}',
        "status": "PAUSED"
    }

    result = _post(url, payload)
    STATE["adset_id"] = result.get("id")
    return STATE["adset_id"]

def activate_campaign():
    _post(
        f"{META_BASE_URL}/{STATE['campaign_id']}",
        {"status": "ACTIVE"}
    )
    _post(
        f"{META_BASE_URL}/{STATE['adset_id']}",
        {"status": "ACTIVE"}
    )

    STATE["status"] = "RUNNING"
    STATE["started_at"] = datetime.now(timezone.utc)

# ================================
# MONITORAMENTO DE GASTO REAL
# ================================

def fetch_spend():
    url = f"{META_BASE_URL}/act_{META_AD_ACCOUNT_ID}/insights"
    params = {
        "fields": "spend",
        "date_preset": "today"
    }

    result = _get(url, params)
    data = result.get("data", [])

    spend = float(data[0].get("spend", 0.0)) if data else 0.0

    STATE["last_spend"] = spend
    STATE["total_spend"] = spend

    return spend

def pause_campaign():
    if STATE["campaign_id"]:
        _post(
            f"{META_BASE_URL}/{STATE['campaign_id']}",
            {"status": "PAUSED"}
        )
    if STATE["adset_id"]:
        _post(
            f"{META_BASE_URL}/{STATE['adset_id']}",
            {"status": "PAUSED"}
        )

    STATE["status"] = "PAUSED"

# ================================
# EXECUÇÃO REAL CONTROLADA
# ================================

def run_real_test():
    try:
        create_campaign()
        create_adset()
        activate_campaign()

        for _ in range(10):
            time.sleep(30)
            spend = fetch_spend()

            if spend >= MAX_TEST_SPEND:
                pause_campaign()
                break

        return {
            "status": STATE["status"],
            "campaign_id": STATE["campaign_id"],
            "adset_id": STATE["adset_id"],
            "total_spend": STATE["total_spend"],
        }

    except Exception as e:
        STATE["status"] = "ERROR"
        STATE["last_error"] = str(e)
        pause_campaign()
        raise
