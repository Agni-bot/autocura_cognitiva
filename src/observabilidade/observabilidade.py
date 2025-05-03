# Módulo de Observabilidade 4D

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
import logging
import json
import time
import threading
from collections import deque, defaultdict
import datetime
import os
import io
import base64
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import flask
from flask import Flask, render_template, jsonify, request
import uuid
import requests

# Configuração de logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_file = os.getenv('LOG_FILE', '/app/logs/observabilidade.log')

# Cria diretório de logs se não existir
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Observabilidade4D")

# Configuração das URLs dos serviços
MONITORAMENTO_URL = os.getenv('MONITORAMENTO_URL', 'http://127.0.0.1:8081')
DIAGNOSTICO_URL = os.getenv('DIAGNOSTICO_URL', 'http://localhost:5002')
GERADOR_ACOES_URL = os.getenv('GERADOR_ACOES_URL', 'http://localhost:5003')

# Classes locais para substituir importações diretas
@dataclass
class MetricaDimensional:
    """Classe local que substitui a importação de monitoramento.monitoramento.MetricaDimensional"""
    id: str
    nome: str
    valor: float
    timestamp: float
    dimensao: str
    unidade: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PadraoAnomalia:
    """Classe local que substitui a importação de diagnostico.diagnostico.PadraoAnomalia"""
    id: str
    nome: str
    dimensoes: List[str]
    descricao: str
    severidade: float

@dataclass
class Diagnostico:
    """Classe local que substitui a importação de diagnostico.diagnostico.Diagnostico"""
    id: str
    timestamp: float
    anomalias_detectadas: List[Tuple[PadraoAnomalia, float]]
    metricas_analisadas: List[str]
    contexto: Dict[str, Any] = field(default_factory=dict)

class TipoAcao:
    """Classe local que substitui a importação de gerador_acoes.gerador_acoes.TipoAcao"""
    HOTFIX = "HOTFIX"
    REFATORACAO = "REFATORACAO"
    REDESIGN = "REDESIGN"

@dataclass
class AcaoCorretiva:
    """Classe local que substitui a importação de gerador_acoes.gerador_acoes.AcaoCorretiva"""
    id: str
    tipo: str
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]
    tempo_estimado: float
    recursos_necessarios: Dict[str, Any]
    prioridade: float = 0.0
    dependencias: List[str] = field(default_factory=list)
    risco: float = 0.5
    reversivel: bool = True
    contexto: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlanoAcao:
    """Classe local que substitui a importação de gerador_acoes.gerador_acoes.PlanoAcao"""
    id: str
    diagnostico_id: str
    acoes: List[AcaoCorretiva]
    timestamp: float
    score: float = 0.0
    status: str = "criado"
    resultado: Optional[Dict[str, Any]] = None
    metricas_impactadas: List[str] = field(default_factory=list)

# Funções para comunicação com outros serviços
def obter_metricas_do_monitoramento(metrica_id=None):
    """
    Obtém métricas do serviço de monitoramento via API REST.
    
    Args:
        metrica_id: ID opcional da métrica específica
        
    Returns:
        Lista de métricas ou uma métrica específica
    """
    try:
        base_url = f"{MONITORAMENTO_URL}/api/metricas"
        if metrica_id:
            url = f"{base_url}/{metrica_id}"
        else:
            url = base_url
            
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if metrica_id:
            # Retorna uma única métrica
            return MetricaDimensional(
                id=data["id"],
                nome=data["nome"],
                valor=data["valor"],
                timestamp=data["timestamp"],
                dimensao=data["dimensao"],
                unidade=data["unidade"],
                tags=data.get("tags", {}),
                metadados=data.get("metadados", {})
            )
        else:
            # Retorna lista de métricas
            metricas = []
            for item in data:
                metrica = MetricaDimensional(
                    id=item["id"],
                    nome=item["nome"],
                    valor=item["valor"],
                    timestamp=item["timestamp"],
                    dimensao=item["dimensao"],
                    unidade=item["unidade"],
                    tags=item.get("tags", {}),
                    metadados=item.get("metadados", {})
                )
                metricas.append(metrica)
            return metricas
            
    except Exception as e:
        logger.error(f"Erro ao obter métricas do monitoramento: {e}")
        return []

def obter_diagnostico(diagnostico_id):
    """
    Obtém um diagnóstico do serviço de diagnóstico via API REST.
    
    Args:
        diagnostico_id: ID do diagnóstico
        
    Returns:
        Objeto Diagnostico ou None se ocorrer erro
    """
    try:
        url = f"{DIAGNOSTICO_URL}/api/diagnosticos/{diagnostico_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        anomalias = []
        for anom_data in data.get("anomalias_detectadas", []):
            padrao = PadraoAnomalia(
                id=anom_data["anomalia"]["id"],
                nome=anom_data["anomalia"]["nome"],
                dimensoes=anom_data["anomalia"]["dimensoes"],
                descricao=anom_data["anomalia"].get("descricao", ""),
                severidade=anom_data["anomalia"].get("severidade", 0.5)
            )
            confianca = anom_data["confianca"]
            anomalias.append((padrao, confianca))
            
        return Diagnostico(
            id=data["id"],
            timestamp=data["timestamp"],
            anomalias_detectadas=anomalias,
            metricas_analisadas=data.get("metricas_analisadas", []),
            contexto=data.get("contexto", {})
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter diagnóstico: {e}")
        return None

def obter_plano_acao(plano_id):
    """
    Obtém um plano de ação do serviço de gerador de ações via API REST.
    
    Args:
        plano_id: ID do plano de ação
        
    Returns:
        Objeto PlanoAcao ou None se ocorrer erro
    """
    try:
        url = f"{GERADOR_ACOES_URL}/api/acoes/planos/{plano_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        acoes = []
        for acao_data in data.get("acoes", []):
            acao = AcaoCorretiva(
                id=acao_data["id"],
                tipo=acao_data["tipo"],
                descricao=acao_data["descricao"],
                comandos=acao_data["comandos"],
                impacto_estimado=acao_data["impacto_estimado"],
                tempo_estimado=acao_data["tempo_estimado"],
                recursos_necessarios=acao_data["recursos_necessarios"],
                prioridade=acao_data.get("prioridade", 0.0),
                dependencias=acao_data.get("dependencias", []),
                risco=acao_data.get("risco", 0.5),
                reversivel=acao_data.get("reversivel", True),
                contexto=acao_data.get("contexto", {})
            )
            acoes.append(acao)
            
        return PlanoAcao(
            id=data["id"],
            diagnostico_id=data["diagnostico_id"],
            acoes=acoes,
            timestamp=data["timestamp"],
            score=data.get("score", 0.0),
            status=data.get("status", "criado"),
            resultado=data.get("resultado"),
            metricas_impactadas=data.get("metricas_impactadas", [])
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter plano de ação: {e}")
        return None

@dataclass
class EventoSistema:
    """
    Representa um evento significativo no sistema.
    
    Como um marco temporal na linha da história do sistema,
    cada evento é um ponto de referência que ancora a narrativa,
    permitindo reconstruir a sequência que levou ao presente.
    """
    id: str
    tipo: str  # 'anomalia', 'diagnostico', 'acao', 'alerta', etc.
    timestamp: float
    descricao: str
    severidade: str  # 'info', 'warning', 'error', 'critical'
    fonte: str
    dados: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o evento para formato de dicionário."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "timestamp": self.timestamp,
            "descricao": self.descricao,
            "severidade": self.severidade,
            "fonte": self.fonte,
            "dados": self.dados
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventoSistema':
        """Cria uma instância de evento a partir de um dicionário."""
        return cls(
            id=data["id"],
            tipo=data["tipo"],
            timestamp=data["timestamp"],
            descricao=data["descricao"],
            severidade=data["severidade"],
            fonte=data["fonte"],
            dados=data.get("dados", {})
        )


class VisualizadorHolografico:
    """
    Apresenta o estado do sistema em múltiplas dimensões.
    
    Como um cartógrafo de realidades multidimensionais,
    projeta o espaço-tempo do sistema em representações visuais,
    revelando padrões invisíveis nas intersecções das dimensões.
    """
    def __init__(self, diretorio_saida: str = "visualizacoes"):
        self.diretorio_saida = diretorio_saida
        self.paleta_cores = {
            "throughput": "#3498db",  # Azul
            "erros": "#e74c3c",       # Vermelho
            "latencia": "#f39c12",    # Laranja
            "recursos": "#2ecc71",    # Verde
            "normal": "#95a5a6",      # Cinza
            "warning": "#f39c12",     # Laranja
            "critical": "#e74c3c",    # Vermelho
            "info": "#3498db",        # Azul
            "hotfix": "#e74c3c",      # Vermelho
            "refatoracao": "#f39c12", # Laranja
            "redesign": "#2ecc71"     # Verde
        }
        
        # Cria diretório de saída se não existir
        os.makedirs(diretorio_saida, exist_ok=True)
        
        logger.info(f"VisualizadorHolografico inicializado com diretório de saída: {diretorio_saida}")
    
    def _preparar_dados_metricas(self, metricas: List[MetricaDimensional]) -> pd.DataFrame:
        """
        Prepara dados de métricas para visualização.
        
        Args:
            metricas: Lista de métricas
            
        Returns:
            DataFrame com dados preparados
        """
        # Converte métricas para formato tabular
        dados = []
        
        for metrica in metricas:
            dados.append({
                "nome": metrica.nome,
                "valor": metrica.valor,
                "timestamp": metrica.timestamp,
                "dimensao": metrica.dimensao,
                "unidade": metrica.unidade,
                "datetime": datetime.datetime.fromtimestamp(metrica.timestamp)
            })
        
        # Cria DataFrame
        df = pd.DataFrame(dados)
        
        # Ordena por timestamp
        if not df.empty:
            df = df.sort_values("timestamp")
        
        return df
    
    def _preparar_dados_eventos(self, eventos: List[EventoSistema]) -> pd.DataFrame:
        """
        Prepara dados de eventos para visualização.
        
        Args:
            eventos: Lista de eventos
            
        Returns:
            DataFrame com dados preparados
        """
        # Converte eventos para formato tabular
        dados = []
        
        for evento in eventos:
            dados.append({
                "id": evento.id,
                "tipo": evento.tipo,
                "timestamp": evento.timestamp,
                "descricao": evento.descricao,
                "severidade": evento.severidade,
                "fonte": evento.fonte,
                "datetime": datetime.datetime.fromtimestamp(evento.timestamp)
            })
        
        # Cria DataFrame
        df = pd.DataFrame(dados)
        
        # Ordena por timestamp
        if not df.empty:
            df = df.sort_values("timestamp")
        
        return df
    
    def _mapear_cor_peso(self, peso: float) -> str:
        """
        Mapeia peso para cor.
        
        Args:
            peso: Valor de peso (0-1)
            
        Returns:
            Código de cor hexadecimal
        """
        if peso < 0.3:
            return "#3498db"  # Azul (fraco)
        elif peso < 0.7:
            return "#f39c12"  # Laranja (médio)
        else:
            return "#e74c3c"  # Vermelho (forte)
    
    def visualizar_metricas_temporais(self, metricas: List[MetricaDimensional], 
                                     titulo: str = "Evolução Temporal de Métricas",
                                     agrupar_por_dimensao: bool = True,
                                     eventos: List[EventoSistema] = None,
                                     salvar: bool = True) -> str:
        """
        Cria visualização temporal de métricas com eventos opcionais.
        
        Args:
            metricas: Lista de métricas
            titulo: Título do gráfico
            agrupar_por_dimensao: Se True, agrupa métricas por dimensão
            eventos: Lista opcional de eventos para marcar no gráfico
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        # Prepara dados
        df = self._preparar_dados_metricas(metricas)
        
        if df.empty:
            logger.warning("Sem dados para visualização temporal")
            return ""
        
        # Cria figura
        plt.figure(figsize=(12, 8))
        
        # Define estilo
        sns.set_style("whitegrid")
        
        # Agrupa por dimensão ou nome
        if agrupar_por_dimensao:
            grupos = df.groupby("dimensao")
            
            # Cria subplots para cada dimensão
            fig, axes = plt.subplots(len(grupos), 1, figsize=(12, 3*len(grupos)), sharex=True)
            
            # Ajusta para caso de apenas uma dimensão
            if len(grupos) == 1:
                axes = [axes]
            
            for (dimensao, grupo), ax in zip(grupos, axes):
                # Agrupa por nome dentro da dimensão
                for nome, subgrupo in grupo.groupby("nome"):
                    ax.plot(subgrupo["datetime"], subgrupo["valor"], 
                           label=nome, 
                           marker='o', 
                           linestyle='-', 
                           alpha=0.7,
                           color=self.paleta_cores.get(dimensao, None))
                
                ax.set_title(f"Dimensão: {dimensao}")
                ax.set_ylabel(grupo["unidade"].iloc[0] if not grupo["unidade"].empty else "Valor")
                ax.legend(loc="upper right")
                ax.grid(True, linestyle='--', alpha=0.7)
            
            # Adiciona eventos se fornecidos
            if eventos:
                df_eventos = self._preparar_dados_eventos(eventos)
                
                for ax in axes:
                    ylim = ax.get_ylim()
                    for _, evento in df_eventos.iterrows():
                        ax.axvline(x=evento["datetime"], color=self.paleta_cores.get(evento["severidade"], "#95a5a6"), 
                                 linestyle='--', alpha=0.5)
                    ax.set_ylim(ylim)  # Restaura limites originais
            
            # Formata eixo x no subplot inferior
            axes[-1].set_xlabel("Tempo")
            axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
        else:
            # Visualiza todas as métricas em um único gráfico
            plt.figure(figsize=(12, 6))
            
            for nome, grupo in df.groupby("nome"):
                plt.plot(grupo["datetime"], grupo["valor"], 
                       label=nome, 
                       marker='o', 
                       linestyle='-', 
                       alpha=0.7,
                       color=self.paleta_cores.get(grupo["dimensao"].iloc[0], None))
            
            # Adiciona eventos se fornecidos
            if eventos:
                df_eventos = self._preparar_dados_eventos(eventos)
                ylim = plt.ylim()
                for _, evento in df_eventos.iterrows():
                    plt.axvline(x=evento["datetime"], color=self.paleta_cores.get(evento["severidade"], "#95a5a6"), 
                              linestyle='--', alpha=0.5)
                plt.ylim(ylim)  # Restaura limites originais
            
            plt.title(titulo)
            plt.xlabel("Tempo")
            plt.ylabel("Valor")
            plt.legend(loc="upper right")
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
        
        # Salva ou retorna como base64
        if salvar:
            nome_arquivo = f"metricas_temporais_{int(time.time())}.png"
            caminho_completo = os.path.join(self.diretorio_saida, nome_arquivo)
            plt.savefig(caminho_completo, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"Visualização salva em {caminho_completo}")
            return caminho_completo
        else:
            # Retorna como string base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_str}"
    
    def visualizar_correlacao_metricas(self, metricas: List[MetricaDimensional],
                                      titulo: str = "Matriz de Correlação entre Métricas",
                                      salvar: bool = True) -> str:
        """
        Cria matriz de correlação entre métricas.
        
        Args:
            metricas: Lista de métricas
            titulo: Título do gráfico
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        # Prepara dados
        df = self._preparar_dados_metricas(metricas)
        
        if df.empty:
            logger.warning("Sem dados para visualização de correlação")
            return ""
        
        # Pivota DataFrame para ter métricas como colunas
        df_pivot = df.pivot_table(index='timestamp', columns='nome', values='valor')
        
        # Calcula correlação
        corr = df_pivot.corr()
        
        # Cria figura
        plt.figure(figsize=(10, 8))
        
        # Cria mapa de calor
        mask = np.triu(np.ones_like(corr, dtype=bool))  # Máscara para triângulo superior
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", 
                   vmin=-1, vmax=1, center=0, square=True, linewidths=.5)
        
        plt.title(titulo)
        plt.tight_layout()
        
        # Salva ou retorna como base64
        if salvar:
            nome_arquivo = f"correlacao_metricas_{int(time.time())}.png"
            caminho_completo = os.path.join(self.diretorio_saida, nome_arquivo)
            plt.savefig(caminho_completo, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"Visualização salva em {caminho_completo}")
            return caminho_completo
        else:
            # Retorna como string base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_str}"
    
    def visualizar_grafo_causal(self, nos: List[Dict[str, Any]], 
                              arestas: List[Dict[str, Any]],
                              titulo: str = "Grafo Causal de Anomalias",
                              salvar: bool = True) -> str:
        """
        Cria visualização de grafo causal.
        
        Args:
            nos: Lista de nós (dicionários com 'id' e 'nome')
            arestas: Lista de arestas (dicionários com 'origem', 'destino' e 'peso')
            titulo: Título do gráfico
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        # Cria grafo
        G = nx.DiGraph()
        
        # Adiciona nós
        for no in nos:
            G.add_node(no["id"], nome=no.get("nome", no["id"]))
        
        # Adiciona arestas
        for aresta in arestas:
            G.add_edge(aresta["origem"], aresta["destino"], peso=aresta.get("peso", 1.0))
        
        # Cria figura
        plt.figure(figsize=(12, 10))
        
        # Define layout
        pos = nx.spring_layout(G, seed=42)
        
        # Define tamanhos dos nós baseados em grau
        tamanhos = [300 + 100 * G.degree(node) for node in G.nodes()]
        
        # Define cores das arestas baseadas em peso
        cores_arestas = [self._mapear_cor_peso(G[u][v].get("peso", 1.0)) for u, v in G.edges()]
        
        # Define larguras das arestas baseadas em peso
        larguras = [1 + 2 * G[u][v].get("peso", 1.0) for u, v in G.edges()]
        
        # Desenha nós
        nx.draw_networkx_nodes(G, pos, node_size=tamanhos, node_color="#3498db", alpha=0.8)
        
        # Desenha arestas
        nx.draw_networkx_edges(G, pos, width=larguras, edge_color=cores_arestas, 
                              arrowsize=15, arrowstyle='->', alpha=0.7)
        
        # Adiciona labels
        labels = {node: G.nodes[node].get("nome", node) for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")
        
        plt.title(titulo)
        plt.axis("off")
        plt.tight_layout()
        
        # Salva ou retorna como base64
        if salvar:
            nome_arquivo = f"grafo_causal_{int(time.time())}.png"
            caminho_completo = os.path.join(self.diretorio_saida, nome_arquivo)
            plt.savefig(caminho_completo, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"Visualização salva em {caminho_completo}")
            return caminho_completo
        else:
            # Retorna como string base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_str}"

def verificar_servicos_dependentes():
    """
    Verifica se os serviços dependentes estão disponíveis.
    Retorna True se todos os serviços estiverem disponíveis.
    """
    servicos = {
        "monitoramento": f"{MONITORAMENTO_URL}/health",
        "diagnostico": f"{DIAGNOSTICO_URL}/health",
        "gerador-acoes": f"{GERADOR_ACOES_URL}/health"
    }
    
    for nome, url in servicos.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                logger.error(f"Serviço {nome} retornou status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Erro ao conectar com serviço {nome}: {e}")
            return False
    
    return True

def obter_diagnosticos_ativos():
    """Busca diagnósticos ativos do serviço de diagnóstico via API REST."""
    try:
        url = f"{DIAGNOSTICO_URL}/api/v1/diagnosticos"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            dados = response.json()
            # Se necessário, adaptar para a estrutura de Diagnostico local
            return [Diagnostico(**d) for d in dados]
        else:
            logger.warning(f"Diagnóstico: resposta inesperada {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Erro ao obter diagnósticos ativos: {e}")
        return []

def obter_acoes_priorizadas():
    """Busca ações priorizadas do serviço de ações via API REST."""
    try:
        url = f"{GERADOR_ACOES_URL}/api/v1/acoes"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            dados = response.json()
            # Se necessário, adaptar para a estrutura de AcaoCorretiva local
            return [AcaoCorretiva(**a) for a in dados]
        else:
            logger.warning(f"Ações: resposta inesperada {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Erro ao obter ações priorizadas: {e}")
        return []

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # Inicializa o visualizador
    visualizador = VisualizadorHolografico()
    
    # Verifica serviços dependentes antes de iniciar
    try:
        if not verificar_servicos_dependentes():
            logger.warning("Alguns serviços dependentes não estão disponíveis. Continuando com funcionalidade limitada...")
    except Exception as e:
        logger.warning(f"Erro ao verificar serviços dependentes: {e}. Continuando com funcionalidade limitada...")
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route('/api/v1/metricas', methods=['GET'])
    def get_metricas():
        try:
            metricas = obter_metricas_do_monitoramento()
            return jsonify([m.__dict__ for m in metricas]), 200
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return jsonify({"erro": "Erro ao obter métricas"}), 500

    @app.route('/api/v1/status', methods=['GET'])
    def get_status():
        try:
            status = verificar_servicos_dependentes()
            return jsonify(status), 200
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return jsonify({"erro": "Erro ao obter status dos serviços"}), 500

    @app.route('/api/v1/diagnosticos', methods=['GET'])
    def get_diagnosticos():
        try:
            diagnosticos = obter_diagnosticos_ativos()
            return jsonify([d.__dict__ for d in diagnosticos]), 200
        except Exception as e:
            logger.error(f"Erro ao obter diagnósticos: {e}")
            return jsonify({"erro": "Erro ao obter diagnósticos"}), 500

    @app.route('/api/v1/acoes', methods=['GET'])
    def get_acoes():
        try:
            acoes = obter_acoes_priorizadas()
            return jsonify([a.__dict__ for a in acoes]), 200
        except Exception as e:
            logger.error(f"Erro ao obter ações: {e}")
            return jsonify({"erro": "Erro ao obter ações"}), 500
    
    @app.route('/api/visualizacoes/metricas-temporais', methods=['POST'])
    def criar_visualizacao_metricas_temporais():
        try:
            data = request.json
            
            # Obtém métricas do monitoramento se não fornecidas
            if 'metricas' not in data:
                metricas = obter_metricas_do_monitoramento()
            else:
                metricas = []
                for metrica_data in data['metricas']:
                    metrica = MetricaDimensional(
                        id=metrica_data["id"],
                        nome=metrica_data["nome"],
                        valor=metrica_data["valor"],
                        timestamp=metrica_data["timestamp"],
                        dimensao=metrica_data["dimensao"],
                        unidade=metrica_data["unidade"],
                        tags=metrica_data.get("tags", {}),
                        metadados=metrica_data.get("metadados", {})
                    )
                    metricas.append(metrica)
            
            # Obtém eventos se fornecidos
            eventos = None
            if 'eventos' in data:
                eventos = []
                for evento_data in data['eventos']:
                    evento = EventoSistema.from_dict(evento_data)
                    eventos.append(evento)
            
            # Cria visualização
            resultado = visualizador.visualizar_metricas_temporais(
                metricas=metricas,
                titulo=data.get('titulo', 'Evolução Temporal de Métricas'),
                agrupar_por_dimensao=data.get('agrupar_por_dimensao', True),
                eventos=eventos,
                salvar=True
            )
            
            return jsonify({
                "sucesso": True,
                "caminho_arquivo": resultado,
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"Erro ao criar visualização de métricas temporais: {e}")
            return jsonify({
                "sucesso": False,
                "erro": str(e),
                "timestamp": time.time()
            }), 500
    
    @app.route('/api/v1/relatorio-completo', methods=['GET'])
    def gerar_relatorio_completo():
        try:
            # Obtém métricas
            metricas = obter_metricas_do_monitoramento()
            
            # Obtém diagnósticos
            diagnosticos = obter_diagnosticos_ativos()
            
            # Obtém ações
            acoes = obter_acoes_priorizadas()
            
            # Gera visualizações
            visualizacao_metricas = visualizador.visualizar_metricas_temporais(
                metricas=metricas,
                titulo="Evolução Temporal das Métricas do Sistema",
                agrupar_por_dimensao=True,
                salvar=False
            )
            
            visualizacao_correlacao = visualizador.visualizar_correlacao_metricas(
                metricas=metricas,
                titulo="Correlação entre Métricas do Sistema",
                salvar=False
            )
            
            # Prepara relatório
            relatorio = {
                "status_geral": {
                    "timestamp": time.time(),
                    "status_servicos": verificar_servicos_dependentes(),
                    "metricas_ativas": len(metricas),
                    "diagnosticos_ativos": len(diagnosticos),
                    "acoes_pendentes": len(acoes)
                },
                "metricas": {
                    "visualizacao_temporal": visualizacao_metricas,
                    "visualizacao_correlacao": visualizacao_correlacao,
                    "dados": [m.__dict__ for m in metricas]
                },
                "diagnosticos": [d.__dict__ for d in diagnosticos],
                "acoes": [a.__dict__ for a in acoes],
                "recomendacoes": {
                    "curto_prazo": [a for a in acoes if a.tipo == "HOTFIX"],
                    "medio_prazo": [a for a in acoes if a.tipo == "REFATORACAO"],
                    "longo_prazo": [a for a in acoes if a.tipo == "REDESIGN"]
                }
            }
            
            return jsonify(relatorio), 200
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório completo: {e}")
            return jsonify({
                "erro": str(e),
                "timestamp": time.time()
            }), 500
    
    @app.route('/relatorio', methods=['GET'])
    def mostrar_relatorio():
        return render_template('relatorio.html')
    
    @app.route('/portal', methods=['GET'])
    def portal_central():
        return render_template('portal.html')
    
    @app.route('/', methods=['GET'])
    def pagina_inicial():
        return render_template('index.html')
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080)
