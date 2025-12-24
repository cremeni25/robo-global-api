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

        status = requests.get(STATUS_ENDPOINT, timeout=10).json()

        if status.get("operacao_ativa") is not True:
            log("Operação não ativa — ciclo encerrado")
            return

        response = requests.post(CICLO_ENDPOINT, timeout=30)
        resultado = response.json()

        requests.post(REGISTRO_ENDPOINT, json={
            "timestamp": datetime.utcnow().isoformat(),
            "resultado": resultado
        }, timeout=10)

        log(f"Ciclo executado com sucesso: {resultado.get('status')}")

    except Exception as e:
        log(f"ERRO NO CICLO: {str(e)}")

def loop_infinito():
    log("LOOP OPERACIONAL INICIADO — ROBO GLOBAL VIVO")
    while True:
        executar_ciclo()
        log(f"Aguardando {LOOP_INTERVAL_SECONDS} segundos para próximo ciclo")
        time.sleep(LOOP_INTERVAL_SECONDS)

if __name__ == "__main__":
    loop_infinito()
