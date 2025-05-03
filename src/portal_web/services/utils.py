import json
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_response(data: Any, message: str = "Success", status_code: int = 200) -> Dict:
    """Formata a resposta da API de forma consistente."""
    return {
        "status_code": status_code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

def handle_exception(e: Exception) -> None:
    """Trata exceções e gera respostas HTTP apropriadas."""
    if isinstance(e, HTTPException):
        raise e
    logger.error(f"Erro não tratado: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Ocorreu um erro interno no servidor"
    )

def validate_json(data: str) -> bool:
    """Valida se uma string é um JSON válido."""
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

def format_metric_data(metric: Dict) -> Dict:
    """Formata dados de métricas para visualização."""
    return {
        "name": metric.get("name"),
        "value": metric.get("value"),
        "unit": metric.get("unit"),
        "timestamp": metric.get("timestamp"),
        "tags": metric.get("tags", {}),
        "metadata": metric.get("metadata", {})
    }

def format_alert_data(alert: Dict) -> Dict:
    """Formata dados de alertas para visualização."""
    return {
        "id": alert.get("id"),
        "severity": alert.get("severity"),
        "message": alert.get("message"),
        "timestamp": alert.get("timestamp"),
        "status": alert.get("status"),
        "source": alert.get("source"),
        "metadata": alert.get("metadata", {})
    }

def format_diagnostic_data(diagnostic: Dict) -> Dict:
    """Formata dados de diagnóstico para visualização."""
    return {
        "id": diagnostic.get("id"),
        "problem": diagnostic.get("problem"),
        "root_cause": diagnostic.get("root_cause"),
        "recommendations": diagnostic.get("recommendations", []),
        "timestamp": diagnostic.get("timestamp"),
        "status": diagnostic.get("status"),
        "metadata": diagnostic.get("metadata", {})
    }

def format_action_data(action: Dict) -> Dict:
    """Formata dados de ações para visualização."""
    return {
        "id": action.get("id"),
        "type": action.get("type"),
        "description": action.get("description"),
        "status": action.get("status"),
        "timestamp": action.get("timestamp"),
        "execution_time": action.get("execution_time"),
        "result": action.get("result"),
        "metadata": action.get("metadata", {})
    } 