from fastapi import APIRouter, HTTPException
from typing import List, Dict
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/metricas")
async def get_metricas():
    return {
        "throughput": round(random.uniform(100, 1000), 2),
        "taxa_erro": round(random.uniform(0, 5), 2),
        "latencia": round(random.uniform(10, 100), 2)
    }

@router.get("/alertas")
async def get_alertas():
    severidades = ["alert-warning", "alert-danger", "alert-info"]
    alertas = []
    
    for i in range(random.randint(0, 5)):
        alertas.append({
            "titulo": f"Alerta {i+1}",
            "descricao": f"Descrição do alerta {i+1}",
            "severidade": random.choice(severidades),
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat()
        })
    
    return alertas

@router.get("/acoes")
async def get_acoes():
    tipos = ["Otimização", "Manutenção", "Correção"]
    acoes = []
    
    for i in range(random.randint(0, 5)):
        acoes.append({
            "tipo": random.choice(tipos),
            "descricao": f"Ação {i+1} para melhoria do sistema",
            "prioridade": random.randint(1, 5)
        })
    
    return acoes 