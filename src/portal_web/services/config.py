import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações da API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Portal Web - Autocura Cognitiva"
    
    # Configurações de Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    
    # Configurações do Banco de Dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./autocura.db")
    
    # Configurações do Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Configurações do WebSocket
    WS_URL: str = os.getenv("WS_URL", "ws://localhost:8000/ws")
    
    # Configurações de Log
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações de Cache
    CACHE_TTL: int = 300  # 5 minutos
    
    class Config:
        case_sensitive = True

settings = Settings() 