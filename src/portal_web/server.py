from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routes import api
import uvicorn
import os

app = FastAPI(title="Sistema de Autocura Cognitiva")

# Configuração dos templates
templates = Jinja2Templates(directory="templates")

# Montagem dos arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir rotas da API
app.include_router(api.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 