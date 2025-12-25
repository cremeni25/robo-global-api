# acquisition_meta_ads.py
# ROBO GLOBAL AI — BLOCO B (ACQUISITION ENGINE — META ADS)
# Versão: 1.1 (fix import-safe)
# Data: 25/12/2025
# EXECUÇÃO REAL — GASTO REAL — REGISTRO REAL

import os
import time
import requests
from datetime import datetime, timezone
from typing import Dict, Any

# ================================
# ORÇAMENTO
# ================================

DAILY_BUDGET = 10.00
MAX_TEST_SPEND = 10.00

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

def _load_env():
    token = os.getenv("META_ACCESS_TOKEN")
    account = os.getenv("META_AD_ACCOUNT_ID")
    version = os.getenv("META_API_VERSION", "v19.0")

    if not token:
        raise RuntimeError("META_ACCESS_TOKEN não definido")
    if not account:
        raise RuntimeError("META_AD_ACCOUNT_ID não definido")

    return token, account, version

def _headers(token):
    return {"Authorization": f"Bearer {token}"}

def _post(url: str, data: dict, token: str):
    response = requests.post(url, data=data, headers=_headers(token), timeout=30)
    if not response.ok:
        raise RuntimeError(response.text)
    return response.json()

def _get(url: str, params: dict, token: str):
    response = requests.get(url, params=params, headers=_headers(token), timeout=30)
    if not response.ok:
        raise RuntimeError(response.text)
    return response.json()

# ================================
# EXECUÇÃO REAL CONTROLADA
# ================================

def run_real_test():
    global MAX_TEST_SPEND

    try:
        token, account_id, api_version = _load_env()
        base_url = f"https://graph.facebook.com/{api_version}"

        # CREATE CAMPAIGN
        campaign = _post(
            f"{base_url}/act_{account_id}/campaigns",
            {
                "name": "RoboGlobalAI-Test",
                "objective": "OUTCOME_TRAFFIC",
                "status": "PAUSED",
                "special_ad_categories": []
            },
            token
        )
        STATE["campaign_id"] = campaign["id"]

        # CREATE ADSET
        adset = _post(
            f"{base_url}/act_{account_id}/adsets",
            {
                "name": "RoboGlobalAI-AdSet",
                "campaign_id": STATE["campaign_id"],
                "daily_budget": int(DAILY_BUDGET * 100),
                "billing_event": "IMPRESSIONS",
                "optimization_goal": "LINK_CLICKS",
                "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
                "targeting": '{"geo_locations":{"countries":["BR"]}}',
                "status": "PAUSED"
            },
            token
        )
        STATE["adset_id"] = adset["id"]

        # ACTIVATE
        _post(f"{base_url}/{STATE['campaign_id']}", {"status": "ACTIVE"}, token)
        _post(f"{base_url}/{STATE['adset_id']}", {"status": "ACTIVE"}, token)

        STATE["status"] = "RUNNING"
        STATE["started_at"] = datetime.now(timezone.utc)

        # MONITOR
        while True:
            time.sleep(30)
            insights = _get(
                f"{base_url}/act_{account_id}/insights",
                {"fields": "spend", "date_preset": "today"},
                token
            )

            spend = float(insights["data"][0]["spend"]) if insights["data"] else 0.0
            STATE["total_spend"] = spend

            if spend >= MAX_TEST_SPEND:
                _post(f"{base_
