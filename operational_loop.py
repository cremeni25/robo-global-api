# operational_loop.py
# LOOP OPERACIONAL REAL — ROBO GLOBAL AI
# Executa continuamente no Render

import time
import requests
from datetime import datetime
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LOOP_INTERVAL_SECONDS = int(os.getenv("LOOP_INTERVAL_SECONDS", "600"))  # 10 minutos

STATUS_ENDPOINT = f"{API_BASE_URL}/status"
CICLO_ENDPOINT = f"{API_BASE_URL}/ciclo"
REGISTRO_ENDPOINT = f"{API_BASE_URL}/resultado"

def log(msg):
    print(f"[ROBO-LOOP] {datetime.utcnow().isoformat()} | {msg}", flush=True)

def executar_ciclo():
    try:
        log("Iniciando ciclo operacional")

        status_response = requests.get(STATUS_ENDPOINT, timeout=10)
        status_response.raise_for_status()
        status = status_response.json()
        if not isinstance(status, dict) or not isinstance(status.get("operacao_ativa"), bool):
            log("WORKER_CONTRACT_MISMATCH expected=operacao_ativa:boolean execution_skipped=true")
            return

        if status.get("operacao_ativa") is not True:
            log("Operação não ativa — ciclo encerrado")
            return

        response = requests.post(CICLO_ENDPOINT, timeout=30)
        response.raise_for_status()
        resultado = response.json()

        requests.post(REGISTRO_ENDPOINT, json={
            "timestamp": datetime.utcnow().isoformat(),
            "resultado": resultado
        }, timeout=10)

        log(f"Ciclo executado com sucesso: {resultado.get('status')}")

    except Exception as e:
        log(f"ERRO NO CICLO categoria={type(e).__name__}")

def loop_infinito():
    log("LOOP OPERACIONAL INICIADO — ROBO GLOBAL VIVO")
    while True:
        executar_ciclo()
        log(f"Aguardando {LOOP_INTERVAL_SECONDS} segundos para próximo ciclo")
        time.sleep(LOOP_INTERVAL_SECONDS)


def report_affiliate_configuration_presence():
    """Report configured setting names only; never read or disclose values."""
    import os
    import json
    for platform in ("HOTMART", "EDUZZ", "MONETIZZE"):
        names = sorted(name for name in os.environ
                       if name.startswith(platform + "_")
                       and name.replace("_", "").isalnum()
                       and bool(os.environ.get(name, "").strip()))
        print("[AFFILIATE_CONFIG] " + json.dumps({
            "platform": platform, "configured_variable_names": names,
            "credential_values_disclosed": False,
            "catalog_access_verified": False,
        }, sort_keys=True), flush=True)

if __name__ == "__main__":
    report_affiliate_configuration_presence()
    loop_infinito()
