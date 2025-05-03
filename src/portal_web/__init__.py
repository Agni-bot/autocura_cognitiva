from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Portal Web - Sistema de Autocura Cognitiva",
    description="Interface web para monitoramento, diagnóstico e recuperação automática",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Importar rotas
from .routes import monitoramento, diagnostico, acoes, observabilidade

# Registrar rotas
app.include_router(monitoramento.router, prefix="/api/monitoramento", tags=["monitoramento"])
app.include_router(diagnostico.router, prefix="/api/diagnostico", tags=["diagnostico"])
app.include_router(acoes.router, prefix="/api/acoes", tags=["acoes"])
app.include_router(observabilidade.router, prefix="/api/observabilidade", tags=["observabilidade"]) 