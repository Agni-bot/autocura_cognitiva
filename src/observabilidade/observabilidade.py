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

# Importação dos módulos anteriores
from monitoramento.monitoramento import MetricaDimensional
from diagnostico.diagnostico import Diagnostico, PadraoAnomalia
from gerador_acoes.gerador_acoes import PlanoAcao, AcaoCorretiva, TipoAcao

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Observabilidade4D")

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
    
    def _mapear_cor_peso(self, peso: float) -> str:
        """
        Mapeia um peso para uma cor.
        
        Args:
            peso: Valor do peso (0-1)
            
        Returns:
            Código de cor em formato hexadecimal
        """
        # Mapeia peso para cor (vermelho para baixo, verde para alto)
        r = int(255 * (1 - peso))
        g = int(255 * peso)
        b = 0
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def visualizar_plano_acao(self, plano: PlanoAcao, 
                             titulo: str = "Plano de Ação",
                             salvar: bool = True) -> str:
        """
        Cria visualização de plano de ação.
        
        Args:
            plano: Plano de ação
            titulo: Título do gráfico
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        if not plano.acoes:
            logger.warning("Plano sem ações para visualização")
            return ""
        
        # Prepara dados
        acoes = []
        for i, acao in enumerate(plano.acoes):
            acoes.append({
                "id": acao.id,
                "tipo": acao.tipo.name,
                "descricao": acao.descricao,
                "prioridade": acao.prioridade,
                "risco": acao.risco,
                "tempo": acao.tempo_estimado,
                "ordem": i
            })
        
        df = pd.DataFrame(acoes)
        
        # Cria figura
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Distribuição por Tipo de Ação",
                "Prioridade vs. Risco",
                "Tempo Estimado por Ação",
                "Impacto Estimado por Dimensão"
            ),
            specs=[
                [{"type": "pie"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # Gráfico de pizza por tipo
        contagem_tipos = df["tipo"].value_counts()
        fig.add_trace(
            go.Pie(
                labels=contagem_tipos.index,
                values=contagem_tipos.values,
                marker=dict(
                    colors=[self.paleta_cores.get(tipo.lower(), "#95a5a6") for tipo in contagem_tipos.index]
                )
            ),
            row=1, col=1
        )
        
        # Gráfico de dispersão prioridade vs. risco
        fig.add_trace(
            go.Scatter(
                x=df["prioridade"],
                y=df["risco"],
                mode="markers+text",
                text=df["ordem"] + 1,  # +1 para começar em 1
                textposition="middle center",
                marker=dict(
                    size=15,
                    color=[self.paleta_cores.get(tipo.lower(), "#95a5a6") for tipo in df["tipo"]]
                ),
                hovertemplate="<b>%{text}</b><br>Prioridade: %{x:.2f}<br>Risco: %{y:.2f}"
            ),
            row=1, col=2
        )
        
        # Gráfico de barras de tempo estimado
        fig.add_trace(
            go.Bar(
                x=df["ordem"] + 1,  # +1 para começar em 1
                y=df["tempo"],
                marker=dict(
                    color=[self.paleta_cores.get(tipo.lower(), "#95a5a6") for tipo in df["tipo"]]
                ),
                hovertemplate="<b>Ação %{x}</b><br>Tempo: %{y} s"
            ),
            row=2, col=1
        )
        
        # Gráfico de barras de impacto estimado
        impactos = []
        dimensoes = set()
        
        for acao in plano.acoes:
            for dim, impacto in acao.impacto_estimado.items():
                impactos.append({
                    "acao": acao.id,
                    "ordem": next(i for i, a in enumerate(plano.acoes) if a.id == acao.id),
                    "dimensao": dim,
                    "impacto": impacto
                })
                dimensoes.add(dim)
        
        if impactos:
            df_impactos = pd.DataFrame(impactos)
            
            for dimensao in dimensoes:
                df_dim = df_impactos[df_impactos["dimensao"] == dimensao]
                
                fig.add_trace(
                    go.Bar(
                        x=df_dim["ordem"] + 1,  # +1 para começar em 1
                        y=df_dim["impacto"],
                        name=dimensao,
                        marker=dict(
                            color=self.paleta_cores.get(dimensao, "#95a5a6")
                        ),
                        hovertemplate=f"<b>Ação %{{x}}</b><br>{dimensao}: %{{y:.2f}}"
                    ),
                    row=2, col=2
                )
        
        # Atualiza layout
        fig.update_layout(
            title=titulo,
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(title_text="Prioridade", row=1, col=2)
        fig.update_yaxes(title_text="Risco", row=1, col=2)
        
        fig.update_xaxes(title_text="Ação", row=2, col=1)
        fig.update_yaxes(title_text="Tempo (s)", row=2, col=1)
        
        fig.update_xaxes(title_text="Ação", row=2, col=2)
        fig.update_yaxes(title_text="Impacto", row=2, col=2)
        
        # Salva ou retorna como HTML
        if salvar:
            nome_arquivo = f"plano_acao_{int(time.time())}.html"
            caminho_completo = os.path.join(self.diretorio_saida, nome_arquivo)
            fig.write_html(caminho_completo)
            logger.info(f"Visualização salva em {caminho_completo}")
            return caminho_completo
        else:
            # Retorna como HTML
            return fig.to_html(include_plotlyjs='cdn')


class ProjetorTemporal:
    """
    Simula estados futuros baseados em tendências atuais.
    
    Como um oráculo digital que desvenda os véus do tempo,
    projeta as sombras do futuro a partir das luzes do presente,
    permitindo vislumbrar os caminhos possíveis antes de percorrê-los.
    """
    def __init__(self):
        self.modelos = {}
        self.historico_metricas = {}
        self.lock = threading.Lock()
        logger.info("ProjetorTemporal inicializado")
    
    def adicionar_metrica(self, metrica: MetricaDimensional):
        """
        Adiciona uma métrica ao histórico para projeção.
        
        Args:
            metrica: Métrica a ser adicionada
        """
        with self.lock:
            chave = f"{metrica.dimensao}:{metrica.nome}"
            
            if chave not in self.historico_metricas:
                self.historico_metricas[chave] = []
            
            self.historico_metricas[chave].append((metrica.timestamp, metrica.valor))
            
            # Mantém histórico ordenado por timestamp
            self.historico_metricas[chave].sort(key=lambda x: x[0])
            
            # Limita tamanho do histórico
            max_pontos = 1000
            if len(self.historico_metricas[chave]) > max_pontos:
                self.historico_metricas[chave] = self.historico_metricas[chave][-max_pontos:]
    
    def _ajustar_modelo_linear(self, pontos: List[Tuple[float, float]]) -> Tuple[float, float, float]:
        """
        Ajusta um modelo linear aos pontos.
        
        Args:
            pontos: Lista de tuplas (timestamp, valor)
            
        Returns:
            Tupla (inclinação, intercepto, r²)
        """
        if len(pontos) < 2:
            return 0.0, 0.0, 0.0
        
        x = np.array([p[0] for p in pontos])
        y = np.array([p[1] for p in pontos])
        
        # Normaliza timestamps para evitar problemas numéricos
        x_min = x.min()
        x = x - x_min
        
        # Ajusta modelo
        slope, intercept, r_value, _, _ = stats.linregress(x, y)
        
        # Ajusta intercepto para timestamp original
        intercept = intercept - slope * x_min
        
        return slope, intercept, r_value ** 2
    
    def _ajustar_modelo_polinomial(self, pontos: List[Tuple[float, float]], grau: int = 2) -> Tuple[np.ndarray, float]:
        """
        Ajusta um modelo polinomial aos pontos.
        
        Args:
            pontos: Lista de tuplas (timestamp, valor)
            grau: Grau do polinômio
            
        Returns:
            Tupla (coeficientes, r²)
        """
        if len(pontos) < grau + 1:
            return np.zeros(grau + 1), 0.0
        
        x = np.array([p[0] for p in pontos])
        y = np.array([p[1] for p in pontos])
        
        # Normaliza timestamps para evitar problemas numéricos
        x_min = x.min()
        x_range = x.max() - x_min
        
        if x_range == 0:
            return np.zeros(grau + 1), 0.0
        
        x_norm = (x - x_min) / x_range
        
        # Ajusta modelo
        coefs = np.polyfit(x_norm, y, grau)
        
        # Calcula valores previstos
        y_pred = np.polyval(coefs, x_norm)
        
        # Calcula R²
        ss_total = np.sum((y - np.mean(y)) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)
        
        r2 = 1 - (ss_residual / ss_total) if ss_total > 0 else 0
        
        # Armazena parâmetros de normalização junto com coeficientes
        coefs_com_norm = np.append(coefs, [x_min, x_range])
        
        return coefs_com_norm, r2
    
    def _prever_modelo_linear(self, slope: float, intercept: float, timestamps: List[float]) -> List[float]:
        """
        Realiza previsões com modelo linear.
        
        Args:
            slope: Inclinação da reta
            intercept: Intercepto da reta
            timestamps: Lista de timestamps para previsão
            
        Returns:
            Lista de valores previstos
        """
        return [slope * t + intercept for t in timestamps]
    
    def _prever_modelo_polinomial(self, coefs_com_norm: np.ndarray, timestamps: List[float]) -> List[float]:
        """
        Realiza previsões com modelo polinomial.
        
        Args:
            coefs_com_norm: Coeficientes com parâmetros de normalização
            timestamps: Lista de timestamps para previsão
            
        Returns:
            Lista de valores previstos
        """
        # Extrai parâmetros de normalização
        x_min = coefs_com_norm[-2]
        x_range = coefs_com_norm[-1]
        coefs = coefs_com_norm[:-2]
        
        # Normaliza timestamps
        x_norm = [(t - x_min) / x_range for t in timestamps]
        
        # Realiza previsões
        return [np.polyval(coefs, x) for x in x_norm]
    
    def projetar_metrica(self, dimensao: str, nome: str, 
                        horizonte: float = 3600,  # 1 hora
                        num_pontos: int = 20,
                        tipo_modelo: str = "auto") -> Dict[str, Any]:
        """
        Projeta valores futuros para uma métrica.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            horizonte: Horizonte de projeção em segundos
            num_pontos: Número de pontos a projetar
            tipo_modelo: Tipo de modelo ('linear', 'polinomial', 'auto')
            
        Returns:
            Dicionário com resultados da projeção
        """
        with self.lock:
            chave = f"{dimensao}:{nome}"
            
            if chave not in self.historico_metricas or len(self.historico_metricas[chave]) < 2:
                return {
                    "sucesso": False,
                    "erro": "Histórico insuficiente para projeção"
                }
            
            # Obtém pontos históricos
            pontos = self.historico_metricas[chave]
            
            # Ajusta modelos
            slope, intercept, r2_linear = self._ajustar_modelo_linear(pontos)
            coefs_poli, r2_poli = self._ajustar_modelo_polinomial(pontos, grau=2)
            
            # Seleciona melhor modelo
            if tipo_modelo == "auto":
                if r2_poli > r2_linear:
                    tipo_modelo = "polinomial"
                else:
                    tipo_modelo = "linear"
            
            # Gera timestamps para projeção
            ultimo_timestamp = pontos[-1][0]
            timestamps_projecao = [ultimo_timestamp + (i + 1) * horizonte / num_pontos for i in range(num_pontos)]
            
            # Realiza projeção
            if tipo_modelo == "linear":
                valores_projetados = self._prever_modelo_linear(slope, intercept, timestamps_projecao)
                r2 = r2_linear
                modelo_info = {
                    "tipo": "linear",
                    "slope": slope,
                    "intercept": intercept
                }
            else:  # polinomial
                valores_projetados = self._prever_modelo_polinomial(coefs_poli, timestamps_projecao)
                r2 = r2_poli
                modelo_info = {
                    "tipo": "polinomial",
                    "coeficientes": coefs_poli[:-2].tolist(),  # Exclui parâmetros de normalização
                    "grau": len(coefs_poli) - 3  # -2 para norm params, -1 para indexação base 0
                }
            
            # Cria resultado
            resultado = {
                "sucesso": True,
                "dimensao": dimensao,
                "nome": nome,
                "horizonte": horizonte,
                "ultimo_timestamp": ultimo_timestamp,
                "ultimo_valor": pontos[-1][1],
                "timestamps_projecao": timestamps_projecao,
                "valores_projetados": valores_projetados,
                "r2": r2,
                "modelo": modelo_info,
                "num_pontos_historico": len(pontos)
            }
            
            return resultado
    
    def projetar_impacto_acao(self, metrica_projecao: Dict[str, Any], 
                             acao: AcaoCorretiva) -> Dict[str, Any]:
        """
        Projeta o impacto de uma ação corretiva em uma métrica.
        
        Args:
            metrica_projecao: Resultado de projeção da métrica
            acao: Ação corretiva
            
        Returns:
            Dicionário com projeção após impacto da ação
        """
        if not metrica_projecao["sucesso"]:
            return metrica_projecao
        
        # Verifica se a ação tem impacto na dimensão da métrica
        dimensao = metrica_projecao["dimensao"]
        if dimensao not in acao.impacto_estimado:
            return {
                **metrica_projecao,
                "impacto_acao": {
                    "id": acao.id,
                    "tipo": acao.tipo.name,
                    "valor": 0.0,
                    "valores_projetados_com_impacto": metrica_projecao["valores_projetados"]
                }
            }
        
        # Obtém impacto estimado
        impacto = acao.impacto_estimado[dimensao]
        
        # Calcula valores projetados com impacto
        valores_originais = metrica_projecao["valores_projetados"]
        valores_com_impacto = []
        
        for valor in valores_originais:
            # Impacto positivo reduz o valor (para métricas negativas como latência, erros)
            # Impacto negativo aumenta o valor
            if impacto >= 0:
                novo_valor = valor * (1 - impacto)
            else:
                novo_valor = valor * (1 + abs(impacto))
            
            valores_com_impacto.append(novo_valor)
        
        # Adiciona informações de impacto ao resultado
        resultado = {
            **metrica_projecao,
            "impacto_acao": {
                "id": acao.id,
                "tipo": acao.tipo.name,
                "valor": impacto,
                "valores_projetados_com_impacto": valores_com_impacto
            }
        }
        
        return resultado
    
    def projetar_impacto_plano(self, metrica_projecao: Dict[str, Any], 
                              plano: PlanoAcao) -> Dict[str, Any]:
        """
        Projeta o impacto de um plano de ação completo em uma métrica.
        
        Args:
            metrica_projecao: Resultado de projeção da métrica
            plano: Plano de ação
            
        Returns:
            Dicionário com projeção após impacto do plano
        """
        if not metrica_projecao["sucesso"] or not plano.acoes:
            return metrica_projecao
        
        # Obtém dimensão da métrica
        dimensao = metrica_projecao["dimensao"]
        
        # Calcula impacto combinado do plano
        impacto_combinado = 0.0
        for acao in plano.acoes:
            if dimensao in acao.impacto_estimado:
                impacto_acao = acao.impacto_estimado[dimensao]
                
                # Combina impactos (evita ultrapassar 1.0 para impactos positivos)
                if impacto_acao >= 0:
                    impacto_combinado = impacto_combinado + impacto_acao * (1 - impacto_combinado)
                else:
                    # Para impactos negativos, soma diretamente
                    impacto_combinado += impacto_acao
        
        # Calcula valores projetados com impacto
        valores_originais = metrica_projecao["valores_projetados"]
        valores_com_impacto = []
        
        for valor in valores_originais:
            # Impacto positivo reduz o valor (para métricas negativas como latência, erros)
            # Impacto negativo aumenta o valor
            if impacto_combinado >= 0:
                novo_valor = valor * (1 - impacto_combinado)
            else:
                novo_valor = valor * (1 + abs(impacto_combinado))
            
            valores_com_impacto.append(novo_valor)
        
        # Adiciona informações de impacto ao resultado
        resultado = {
            **metrica_projecao,
            "impacto_plano": {
                "id": plano.id,
                "valor_combinado": impacto_combinado,
                "num_acoes": len(plano.acoes),
                "valores_projetados_com_impacto": valores_com_impacto
            }
        }
        
        return resultado
    
    def visualizar_projecao(self, projecao: Dict[str, Any], 
                           titulo: str = None,
                           mostrar_impacto: bool = True,
                           salvar: bool = True) -> str:
        """
        Cria visualização de projeção temporal.
        
        Args:
            projecao: Resultado de projeção
            titulo: Título do gráfico (opcional)
            mostrar_impacto: Se True, mostra projeção com impacto
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        if not projecao["sucesso"]:
            logger.warning(f"Projeção falhou: {projecao.get('erro', 'Erro desconhecido')}")
            return ""
        
        # Define título se não fornecido
        if titulo is None:
            titulo = f"Projeção de {projecao['nome']} ({projecao['dimensao']})"
        
        # Prepara dados históricos
        chave = f"{projecao['dimensao']}:{projecao['nome']}"
        pontos_historicos = self.historico_metricas.get(chave, [])
        
        timestamps_hist = [datetime.datetime.fromtimestamp(p[0]) for p in pontos_historicos]
        valores_hist = [p[1] for p in pontos_historicos]
        
        # Prepara dados de projeção
        timestamps_proj = [datetime.datetime.fromtimestamp(t) for t in projecao["timestamps_projecao"]]
        valores_proj = projecao["valores_projetados"]
        
        # Cria figura
        plt.figure(figsize=(12, 6))
        
        # Define estilo
        sns.set_style("whitegrid")
        
        # Plota dados históricos
        plt.plot(timestamps_hist, valores_hist, 
               marker='o', 
               linestyle='-', 
               color='#3498db',
               label='Histórico')
        
        # Plota projeção
        plt.plot(timestamps_proj, valores_proj, 
               marker='x', 
               linestyle='--', 
               color='#e74c3c',
               label=f'Projeção (R² = {projecao["r2"]:.2f})')
        
        # Plota projeção com impacto
        if mostrar_impacto:
            if "impacto_acao" in projecao:
                impacto = projecao["impacto_acao"]
                plt.plot(timestamps_proj, impacto["valores_projetados_com_impacto"], 
                       marker='+', 
                       linestyle='-.', 
                       color='#2ecc71',
                       label=f'Com impacto de ação ({impacto["valor"]:.2f})')
            
            elif "impacto_plano" in projecao:
                impacto = projecao["impacto_plano"]
                plt.plot(timestamps_proj, impacto["valores_projetados_com_impacto"], 
                       marker='+', 
                       linestyle='-.', 
                       color='#2ecc71',
                       label=f'Com impacto do plano ({impacto["valor_combinado"]:.2f})')
        
        # Adiciona linha vertical no último ponto histórico
        ultimo_timestamp = datetime.datetime.fromtimestamp(projecao["ultimo_timestamp"])
        plt.axvline(x=ultimo_timestamp, color='#95a5a6', linestyle=':', label='Agora')
        
        # Formata gráfico
        plt.title(titulo)
        plt.xlabel("Tempo")
        plt.ylabel(f"{projecao['nome']} ({projecao['dimensao']})")
        plt.legend(loc="best")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.gcf().autofmt_xdate()  # Rotaciona labels do eixo x
        
        plt.tight_layout()
        
        # Salva ou retorna como base64
        if salvar:
            nome_arquivo = f"projecao_{projecao['dimensao']}_{projecao['nome']}_{int(time.time())}.png"
            caminho_completo = os.path.join("/tmp", nome_arquivo)
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


class InterfaceControleAdaptativa:
    """
    Ajusta-se ao contexto e necessidades do operador.
    
    Como um camaleão digital que se adapta ao ambiente,
    transforma sua aparência e comportamento para refletir
    o contexto operacional e as necessidades do momento.
    """
    def __init__(self, host: str = "0.0.0.0", porta: int = 5000):
        self.host = host
        self.porta = porta
        self.app = Flask(__name__)
        self.dash_app = dash.Dash(__name__, server=self.app, url_base_pathname="/dashboard/")
        self.visualizador = VisualizadorHolografico()
        self.projetor = ProjetorTemporal()
        self.metricas_recentes = {}
        self.eventos_recentes = deque(maxlen=1000)
        self.diagnosticos_recentes = deque(maxlen=100)
        self.planos_recentes = deque(maxlen=100)
        self.lock = threading.Lock()
        
        # Configura rotas Flask
        self._configurar_rotas()
        
        # Configura layout Dash
        self._configurar_dashboard()
        
        logger.info(f"InterfaceControleAdaptativa inicializada em {host}:{porta}")
    
    def _configurar_rotas(self):
        """Configura rotas da API Flask."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html', titulo="Sistema de Autocura Cognitiva")
        
        @self.app.route('/api/metricas', methods=['GET'])
        def obter_metricas():
            with self.lock:
                return jsonify({
                    "metricas": list(self.metricas_recentes.values())
                })
        
        @self.app.route('/api/eventos', methods=['GET'])
        def obter_eventos():
            with self.lock:
                return jsonify({
                    "eventos": [e.to_dict() for e in self.eventos_recentes]
                })
        
        @self.app.route('/api/diagnosticos', methods=['GET'])
        def obter_diagnosticos():
            with self.lock:
                return jsonify({
                    "diagnosticos": [d.to_dict() for d in self.diagnosticos_recentes]
                })
        
        @self.app.route('/api/planos', methods=['GET'])
        def obter_planos():
            with self.lock:
                return jsonify({
                    "planos": [p.to_dict() for p in self.planos_recentes]
                })
        
        @self.app.route('/api/projecao/<dimensao>/<nome>', methods=['GET'])
        def obter_projecao(dimensao, nome):
            horizonte = request.args.get('horizonte', 3600, type=float)
            num_pontos = request.args.get('pontos', 20, type=int)
            tipo_modelo = request.args.get('modelo', 'auto')
            
            with self.lock:
                projecao = self.projetor.projetar_metrica(
                    dimensao=dimensao,
                    nome=nome,
                    horizonte=horizonte,
                    num_pontos=num_pontos,
                    tipo_modelo=tipo_modelo
                )
                
                return jsonify(projecao)
    
    def _configurar_dashboard(self):
        """Configura layout e callbacks do dashboard Dash."""
        
        # Layout principal
        self.dash_app.layout = html.Div([
            html.H1("Sistema de Autocura Cognitiva - Dashboard 4D"),
            
            html.Div([
                html.Div([
                    html.H3("Métricas em Tempo Real"),
                    dcc.Graph(id='grafico-metricas'),
                    dcc.Interval(
                        id='intervalo-metricas',
                        interval=5000,  # 5 segundos
                        n_intervals=0
                    )
                ], className='six columns'),
                
                html.Div([
                    html.H3("Eventos do Sistema"),
                    html.Div(id='tabela-eventos'),
                    dcc.Interval(
                        id='intervalo-eventos',
                        interval=5000,  # 5 segundos
                        n_intervals=0
                    )
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                html.Div([
                    html.H3("Projeção Temporal"),
                    html.Div([
                        html.Label("Dimensão:"),
                        dcc.Dropdown(id='dropdown-dimensao', value='latencia'),
                        
                        html.Label("Métrica:"),
                        dcc.Dropdown(id='dropdown-metrica'),
                        
                        html.Label("Horizonte (segundos):"),
                        dcc.Input(id='input-horizonte', type='number', value=3600),
                        
                        html.Button('Atualizar Projeção', id='botao-projecao')
                    ]),
                    dcc.Graph(id='grafico-projecao')
                ], className='six columns'),
                
                html.Div([
                    html.H3("Diagnósticos e Planos"),
                    html.Div(id='tabela-diagnosticos'),
                    dcc.Interval(
                        id='intervalo-diagnosticos',
                        interval=10000,  # 10 segundos
                        n_intervals=0
                    )
                ], className='six columns')
            ], className='row')
        ])
        
        # Callbacks
        
        @self.dash_app.callback(
            Output('grafico-metricas', 'figure'),
            Input('intervalo-metricas', 'n_intervals')
        )
        def atualizar_grafico_metricas(_):
            with self.lock:
                # Agrupa métricas por dimensão
                metricas_por_dimensao = {}
                for metrica in self.metricas_recentes.values():
                    if metrica.dimensao not in metricas_por_dimensao:
                        metricas_por_dimensao[metrica.dimensao] = []
                    metricas_por_dimensao[metrica.dimensao].append(metrica)
                
                # Cria figura com subplots
                fig = make_subplots(
                    rows=len(metricas_por_dimensao) or 1,
                    cols=1,
                    subplot_titles=[dim.capitalize() for dim in metricas_por_dimensao.keys()] or ["Sem dados"]
                )
                
                # Adiciona traces para cada dimensão
                for i, (dimensao, metricas) in enumerate(metricas_por_dimensao.items()):
                    for metrica in metricas:
                        # Obtém histórico da métrica
                        chave = f"{metrica.dimensao}:{metrica.nome}"
                        pontos = self.projetor.historico_metricas.get(chave, [])
                        
                        if pontos:
                            timestamps = [datetime.datetime.fromtimestamp(p[0]) for p in pontos]
                            valores = [p[1] for p in pontos]
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=timestamps,
                                    y=valores,
                                    mode='lines+markers',
                                    name=metrica.nome
                                ),
                                row=i+1,
                                col=1
                            )
                
                # Atualiza layout
                fig.update_layout(
                    height=200 * (len(metricas_por_dimensao) or 1),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                return fig
        
        @self.dash_app.callback(
            Output('tabela-eventos', 'children'),
            Input('intervalo-eventos', 'n_intervals')
        )
        def atualizar_tabela_eventos(_):
            with self.lock:
                if not self.eventos_recentes:
                    return html.Div("Nenhum evento registrado")
                
                # Cria tabela de eventos
                eventos = list(self.eventos_recentes)[-10:]  # Últimos 10 eventos
                
                cabecalho = html.Thead(html.Tr([
                    html.Th("Timestamp"),
                    html.Th("Tipo"),
                    html.Th("Severidade"),
                    html.Th("Descrição")
                ]))
                
                linhas = []
                for evento in reversed(eventos):  # Mais recentes primeiro
                    timestamp = datetime.datetime.fromtimestamp(evento.timestamp).strftime('%H:%M:%S')
                    
                    # Define cor baseada na severidade
                    cor = {
                        "info": "#3498db",
                        "warning": "#f39c12",
                        "error": "#e74c3c",
                        "critical": "#c0392b"
                    }.get(evento.severidade, "#95a5a6")
                    
                    linhas.append(html.Tr([
                        html.Td(timestamp),
                        html.Td(evento.tipo),
                        html.Td(evento.severidade, style={"color": cor}),
                        html.Td(evento.descricao)
                    ]))
                
                corpo = html.Tbody(linhas)
                
                return html.Table([cabecalho, corpo], className="table")
        
        @self.dash_app.callback(
            Output('dropdown-metrica', 'options'),
            Input('dropdown-dimensao', 'value')
        )
        def atualizar_opcoes_metricas(dimensao):
            with self.lock:
                # Filtra métricas pela dimensão selecionada
                metricas = [m for m in self.metricas_recentes.values() if m.dimensao == dimensao]
                
                # Cria opções para dropdown
                opcoes = [{'label': m.nome, 'value': m.nome} for m in metricas]
                
                return opcoes or [{'label': 'Nenhuma métrica disponível', 'value': ''}]
        
        @self.dash_app.callback(
            Output('grafico-projecao', 'figure'),
            Input('botao-projecao', 'n_clicks'),
            [dash.dependencies.State('dropdown-dimensao', 'value'),
             dash.dependencies.State('dropdown-metrica', 'value'),
             dash.dependencies.State('input-horizonte', 'value')]
        )
        def atualizar_projecao(_, dimensao, nome, horizonte):
            if not dimensao or not nome:
                # Retorna gráfico vazio
                return go.Figure()
            
            with self.lock:
                # Realiza projeção
                projecao = self.projetor.projetar_metrica(
                    dimensao=dimensao,
                    nome=nome,
                    horizonte=float(horizonte) if horizonte else 3600,
                    num_pontos=20,
                    tipo_modelo='auto'
                )
                
                if not projecao["sucesso"]:
                    # Retorna gráfico vazio com mensagem de erro
                    fig = go.Figure()
                    fig.add_annotation(
                        text=projecao.get("erro", "Erro na projeção"),
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        showarrow=False
                    )
                    return fig
                
                # Prepara dados históricos
                chave = f"{dimensao}:{nome}"
                pontos_historicos = self.projetor.historico_metricas.get(chave, [])
                
                timestamps_hist = [datetime.datetime.fromtimestamp(p[0]) for p in pontos_historicos]
                valores_hist = [p[1] for p in pontos_historicos]
                
                # Prepara dados de projeção
                timestamps_proj = [datetime.datetime.fromtimestamp(t) for t in projecao["timestamps_projecao"]]
                valores_proj = projecao["valores_projetados"]
                
                # Cria figura
                fig = go.Figure()
                
                # Adiciona dados históricos
                fig.add_trace(
                    go.Scatter(
                        x=timestamps_hist,
                        y=valores_hist,
                        mode='lines+markers',
                        name='Histórico',
                        line=dict(color='#3498db')
                    )
                )
                
                # Adiciona projeção
                fig.add_trace(
                    go.Scatter(
                        x=timestamps_proj,
                        y=valores_proj,
                        mode='lines+markers',
                        name=f'Projeção (R² = {projecao["r2"]:.2f})',
                        line=dict(color='#e74c3c', dash='dash')
                    )
                )
                
                # Adiciona linha vertical no último ponto histórico
                ultimo_timestamp = datetime.datetime.fromtimestamp(projecao["ultimo_timestamp"])
                fig.add_vline(
                    x=ultimo_timestamp,
                    line_width=1,
                    line_dash="dot",
                    line_color="#95a5a6",
                    annotation_text="Agora"
                )
                
                # Atualiza layout
                fig.update_layout(
                    title=f"Projeção de {nome} ({dimensao})",
                    xaxis_title="Tempo",
                    yaxis_title=f"{nome} ({dimensao})",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                return fig
        
        @self.dash_app.callback(
            Output('tabela-diagnosticos', 'children'),
            Input('intervalo-diagnosticos', 'n_intervals')
        )
        def atualizar_tabela_diagnosticos(_):
            with self.lock:
                if not self.diagnosticos_recentes:
                    return html.Div("Nenhum diagnóstico registrado")
                
                # Cria tabela de diagnósticos
                diagnosticos = list(self.diagnosticos_recentes)[-5:]  # Últimos 5 diagnósticos
                
                cabecalho = html.Thead(html.Tr([
                    html.Th("Timestamp"),
                    html.Th("Anomalias"),
                    html.Th("Causa Raiz"),
                    html.Th("Confiança"),
                    html.Th("Ações")
                ]))
                
                linhas = []
                for diag in reversed(diagnosticos):  # Mais recentes primeiro
                    timestamp = datetime.datetime.fromtimestamp(diag.timestamp).strftime('%H:%M:%S')
                    
                    # Encontra plano associado
                    plano_associado = next((p for p in self.planos_recentes if p.diagnostico_id == diag.id), None)
                    
                    # Texto de ações
                    if plano_associado:
                        texto_acoes = f"{len(plano_associado.acoes)} ações ({plano_associado.status})"
                    else:
                        texto_acoes = "Sem plano"
                    
                    linhas.append(html.Tr([
                        html.Td(timestamp),
                        html.Td(f"{len(diag.anomalias_detectadas)} detectadas"),
                        html.Td(diag.causa_raiz or "Desconhecida"),
                        html.Td(f"{diag.confianca:.2f}"),
                        html.Td(texto_acoes)
                    ]))
                
                corpo = html.Tbody(linhas)
                
                return html.Table([cabecalho, corpo], className="table")
    
    def adicionar_metrica(self, metrica: MetricaDimensional):
        """
        Adiciona uma métrica ao sistema.
        
        Args:
            metrica: Métrica a ser adicionada
        """
        with self.lock:
            # Armazena métrica
            chave = f"{metrica.dimensao}:{metrica.nome}"
            self.metricas_recentes[chave] = metrica
            
            # Adiciona ao projetor
            self.projetor.adicionar_metrica(metrica)
    
    def adicionar_evento(self, evento: EventoSistema):
        """
        Adiciona um evento ao sistema.
        
        Args:
            evento: Evento a ser adicionado
        """
        with self.lock:
            self.eventos_recentes.append(evento)
    
    def adicionar_diagnostico(self, diagnostico: Diagnostico):
        """
        Adiciona um diagnóstico ao sistema.
        
        Args:
            diagnostico: Diagnóstico a ser adicionado
        """
        with self.lock:
            self.diagnosticos_recentes.append(diagnostico)
            
            # Cria evento associado
            evento = EventoSistema(
                id=f"evento_diag_{diagnostico.id}",
                tipo="diagnostico",
                timestamp=diagnostico.timestamp,
                descricao=f"Diagnóstico: {diagnostico.causa_raiz or 'Sem causa identificada'}",
                severidade="warning" if diagnostico.anomalias_detectadas else "info",
                fonte="sistema_diagnostico",
                dados={"diagnostico_id": diagnostico.id}
            )
            
            self.adicionar_evento(evento)
    
    def adicionar_plano(self, plano: PlanoAcao):
        """
        Adiciona um plano de ação ao sistema.
        
        Args:
            plano: Plano a ser adicionado
        """
        with self.lock:
            self.planos_recentes.append(plano)
            
            # Cria evento associado
            evento = EventoSistema(
                id=f"evento_plano_{plano.id}",
                tipo="plano_acao",
                timestamp=plano.timestamp,
                descricao=f"Plano de ação gerado com {len(plano.acoes)} ações",
                severidade="info",
                fonte="gerador_acoes",
                dados={"plano_id": plano.id, "diagnostico_id": plano.diagnostico_id}
            )
            
            self.adicionar_evento(evento)
    
    def atualizar_status_plano(self, plano_id: str, status: str):
        """
        Atualiza o status de um plano.
        
        Args:
            plano_id: ID do plano
            status: Novo status
        """
        with self.lock:
            # Encontra plano
            for plano in self.planos_recentes:
                if plano.id == plano_id:
                    plano.status = status
                    
                    # Cria evento associado
                    evento = EventoSistema(
                        id=f"evento_status_{plano.id}_{int(time.time())}",
                        tipo="atualizacao_status",
                        timestamp=time.time(),
                        descricao=f"Plano {plano.id} atualizado para '{status}'",
                        severidade="info",
                        fonte="sistema_execucao",
                        dados={"plano_id": plano.id, "status": status}
                    )
                    
                    self.adicionar_evento(evento)
                    break
    
    def iniciar(self):
        """Inicia o servidor Flask."""
        self.app.run(host=self.host, port=self.porta)


class Observabilidade4D:
    """
    Coordena os diferentes componentes de observabilidade.
    
    Como um maestro que rege a orquestra da percepção,
    harmoniza as diferentes perspectivas do sistema,
    criando uma visão holística que transcende as dimensões individuais.
    """
    def __init__(self, diretorio_saida: str = "visualizacoes"):
        self.visualizador = VisualizadorHolografico(diretorio_saida)
        self.projetor = ProjetorTemporal()
        self.interface = InterfaceControleAdaptativa()
        self.thread_interface = None
        self.metricas_recentes = {}
        self.eventos_recentes = deque(maxlen=1000)
        self.diagnosticos_recentes = deque(maxlen=100)
        self.planos_recentes = deque(maxlen=100)
        self.lock = threading.Lock()
        logger.info("Observabilidade4D inicializada")
    
    def iniciar_interface(self):
        """Inicia a interface de controle em uma thread separada."""
        if self.thread_interface is not None:
            logger.warning("Interface já está em execução")
            return
        
        self.thread_interface = threading.Thread(target=self.interface.iniciar, daemon=True)
        self.thread_interface.start()
        logger.info("Interface de controle iniciada")
    
    def registrar_metrica(self, metrica: MetricaDimensional):
        """
        Registra uma métrica no sistema.
        
        Args:
            metrica: Métrica a ser registrada
        """
        with self.lock:
            # Armazena métrica
            chave = f"{metrica.dimensao}:{metrica.nome}"
            self.metricas_recentes[chave] = metrica
            
            # Adiciona ao projetor
            self.projetor.adicionar_metrica(metrica)
            
            # Adiciona à interface
            self.interface.adicionar_metrica(metrica)
    
    def registrar_evento(self, evento: EventoSistema):
        """
        Registra um evento no sistema.
        
        Args:
            evento: Evento a ser registrado
        """
        with self.lock:
            self.eventos_recentes.append(evento)
            self.interface.adicionar_evento(evento)
    
    def registrar_diagnostico(self, diagnostico: Diagnostico):
        """
        Registra um diagnóstico no sistema.
        
        Args:
            diagnostico: Diagnóstico a ser registrado
        """
        with self.lock:
            self.diagnosticos_recentes.append(diagnostico)
            self.interface.adicionar_diagnostico(diagnostico)
            
            # Registra métricas do diagnóstico
            for metrica in diagnostico.metricas_analisadas:
                self.registrar_metrica(metrica)
            
            # Cria evento associado
            evento = EventoSistema(
                id=f"evento_diag_{diagnostico.id}",
                tipo="diagnostico",
                timestamp=diagnostico.timestamp,
                descricao=f"Diagnóstico: {diagnostico.causa_raiz or 'Sem causa identificada'}",
                severidade="warning" if diagnostico.anomalias_detectadas else "info",
                fonte="sistema_diagnostico",
                dados={"diagnostico_id": diagnostico.id}
            )
            
            self.registrar_evento(evento)
    
    def registrar_plano(self, plano: PlanoAcao):
        """
        Registra um plano de ação no sistema.
        
        Args:
            plano: Plano a ser registrado
        """
        with self.lock:
            self.planos_recentes.append(plano)
            self.interface.adicionar_plano(plano)
            
            # Cria evento associado
            evento = EventoSistema(
                id=f"evento_plano_{plano.id}",
                tipo="plano_acao",
                timestamp=plano.timestamp,
                descricao=f"Plano de ação gerado com {len(plano.acoes)} ações",
                severidade="info",
                fonte="gerador_acoes",
                dados={"plano_id": plano.id, "diagnostico_id": plano.diagnostico_id}
            )
            
            self.registrar_evento(evento)
    
    def atualizar_status_plano(self, plano_id: str, status: str):
        """
        Atualiza o status de um plano.
        
        Args:
            plano_id: ID do plano
            status: Novo status
        """
        with self.lock:
            # Encontra plano
            for plano in self.planos_recentes:
                if plano.id == plano_id:
                    plano.status = status
                    
                    # Atualiza na interface
                    self.interface.atualizar_status_plano(plano_id, status)
                    
                    # Cria evento associado
                    evento = EventoSistema(
                        id=f"evento_status_{plano.id}_{int(time.time())}",
                        tipo="atualizacao_status",
                        timestamp=time.time(),
                        descricao=f"Plano {plano.id} atualizado para '{status}'",
                        severidade="info",
                        fonte="sistema_execucao",
                        dados={"plano_id": plano.id, "status": status}
                    )
                    
                    self.registrar_evento(evento)
                    break
    
    def visualizar_metricas(self, dimensao: str = None, 
                           periodo: float = 3600,  # 1 hora
                           salvar: bool = True) -> str:
        """
        Cria visualização de métricas.
        
        Args:
            dimensao: Dimensão específica para filtrar (opcional)
            periodo: Período de tempo em segundos
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        with self.lock:
            # Filtra métricas pela dimensão
            if dimensao:
                metricas = [m for m in self.metricas_recentes.values() if m.dimensao == dimensao]
            else:
                metricas = list(self.metricas_recentes.values())
            
            # Filtra eventos recentes
            agora = time.time()
            eventos_periodo = [e for e in self.eventos_recentes if agora - e.timestamp <= periodo]
            
            # Cria visualização
            return self.visualizador.visualizar_metricas_temporais(
                metricas=metricas,
                titulo=f"Métricas {dimensao or 'Todas as Dimensões'} - Últimas {periodo/3600:.1f}h",
                agrupar_por_dimensao=dimensao is None,
                eventos=eventos_periodo,
                salvar=salvar
            )
    
    def visualizar_correlacao(self, metricas: List[str] = None, 
                             salvar: bool = True) -> str:
        """
        Cria visualização de correlação entre métricas.
        
        Args:
            metricas: Lista de nomes de métricas (opcional)
            salvar: Se True, salva a visualização em arquivo
            
        Returns:
            Caminho do arquivo salvo ou string base64 da imagem
        """
        with self.lock:
            # Filtra métricas pelos nomes
            if metricas:
                metricas_selecionadas = []
                for nome in metricas:
                    for metrica in self.metricas_recentes.values():
                        if metrica.nome == nome:
                            metricas_selecionadas.append(metrica)
            else:
                metricas_selecionadas = list(self.metricas_recentes.values())
            
            # Cria visualização
            return self.visualizador.visualizar_correlacao_metricas(
                metricas=metricas_selecionadas,
                titulo="Matriz de Correlação entre Métricas",
                salvar=salvar
            )
    
    def visualizar_diagnostico(self, diagnostico_id: str, 
                              salvar: bool = True) -> Dict[str, str]:
        """
        Cria visualizações para um diagnóstico.
        
        Args:
            diagnostico_id: ID do diagnóstico
            salvar: Se True, salva as visualizações em arquivo
            
        Returns:
            Dicionário com caminhos ou strings base64 das imagens
        """
        with self.lock:
            # Encontra diagnóstico
            diagnostico = next((d for d in self.diagnosticos_recentes if d.id == diagnostico_id), None)
            
            if not diagnostico:
                logger.warning(f"Diagnóstico {diagnostico_id} não encontrado")
                return {}
            
            # Cria visualizações
            resultados = {}
            
            # Visualização de métricas
            resultados["metricas"] = self.visualizador.visualizar_metricas_temporais(
                metricas=diagnostico.metricas_analisadas,
                titulo=f"Métricas do Diagnóstico {diagnostico_id}",
                agrupar_por_dimensao=True,
                salvar=salvar
            )
            
            # Visualização de grafo causal (se houver anomalias)
            if diagnostico.anomalias_detectadas:
                # Cria nós para anomalias
                nos = []
                for anomalia, confianca in diagnostico.anomalias_detectadas:
                    nos.append({
                        "id": anomalia.id,
                        "nome": anomalia.nome,
                        "confianca": confianca
                    })
                
                # Cria nó para causa raiz
                if diagnostico.causa_raiz:
                    nos.append({
                        "id": "causa_raiz",
                        "nome": diagnostico.causa_raiz
                    })
                
                # Cria arestas
                arestas = []
                if diagnostico.causa_raiz:
                    for anomalia, confianca in diagnostico.anomalias_detectadas:
                        arestas.append({
                            "origem": "causa_raiz",
                            "destino": anomalia.id,
                            "peso": confianca
                        })
                
                # Cria arestas entre anomalias relacionadas
                for i, (anomalia1, _) in enumerate(diagnostico.anomalias_detectadas):
                    for j, (anomalia2, _) in enumerate(diagnostico.anomalias_detectadas):
                        if i != j and any(dim in anomalia2.dimensoes for dim in anomalia1.dimensoes):
                            arestas.append({
                                "origem": anomalia1.id,
                                "destino": anomalia2.id,
                                "peso": 0.5  # Peso padrão para relações entre anomalias
                            })
                
                resultados["grafo_causal"] = self.visualizador.visualizar_grafo_causal(
                    nos=nos,
                    arestas=arestas,
                    titulo=f"Grafo Causal do Diagnóstico {diagnostico_id}",
                    salvar=salvar
                )
            
            return resultados
    
    def visualizar_plano(self, plano_id: str, 
                        salvar: bool = True) -> Dict[str, str]:
        """
        Cria visualizações para um plano de ação.
        
        Args:
            plano_id: ID do plano
            salvar: Se True, salva as visualizações em arquivo
            
        Returns:
            Dicionário com caminhos ou strings base64 das imagens
        """
        with self.lock:
            # Encontra plano
            plano = next((p for p in self.planos_recentes if p.id == plano_id), None)
            
            if not plano:
                logger.warning(f"Plano {plano_id} não encontrado")
                return {}
            
            # Cria visualizações
            resultados = {}
            
            # Visualização do plano
            resultados["plano"] = self.visualizador.visualizar_plano_acao(
                plano=plano,
                titulo=f"Plano de Ação {plano_id}",
                salvar=salvar
            )
            
            # Visualização de projeções para métricas impactadas
            if plano.metricas_impactadas:
                projecoes = {}
                
                for nome_metrica in plano.metricas_impactadas:
                    # Encontra dimensão da métrica
                    dimensao = None
                    for metrica in self.metricas_recentes.values():
                        if metrica.nome == nome_metrica:
                            dimensao = metrica.dimensao
                            break
                    
                    if dimensao:
                        # Realiza projeção
                        projecao = self.projetor.projetar_metrica(
                            dimensao=dimensao,
                            nome=nome_metrica,
                            horizonte=3600,  # 1 hora
                            num_pontos=20,
                            tipo_modelo='auto'
                        )
                        
                        if projecao["sucesso"]:
                            # Projeta impacto do plano
                            projecao_com_impacto = self.projetor.projetar_impacto_plano(projecao, plano)
                            
                            # Cria visualização
                            projecoes[nome_metrica] = self.projetor.visualizar_projecao(
                                projecao=projecao_com_impacto,
                                titulo=f"Projeção de {nome_metrica} com Impacto do Plano",
                                mostrar_impacto=True,
                                salvar=salvar
                            )
                
                if projecoes:
                    resultados["projecoes"] = projecoes
            
            return resultados
    
    def gerar_relatorio(self, periodo: float = 86400,  # 24 horas
                       salvar: bool = True) -> Dict[str, Any]:
        """
        Gera um relatório completo do sistema.
        
        Args:
            periodo: Período de tempo em segundos
            salvar: Se True, salva as visualizações em arquivo
            
        Returns:
            Dicionário com informações e visualizações do relatório
        """
        with self.lock:
            agora = time.time()
            inicio_periodo = agora - periodo
            
            # Filtra dados pelo período
            metricas = list(self.metricas_recentes.values())
            eventos = [e for e in self.eventos_recentes if e.timestamp >= inicio_periodo]
            diagnosticos = [d for d in self.diagnosticos_recentes if d.timestamp >= inicio_periodo]
            planos = [p for p in self.planos_recentes if p.timestamp >= inicio_periodo]
            
            # Cria visualizações
            visualizacoes = {}
            
            # Visualização de métricas
            visualizacoes["metricas"] = self.visualizador.visualizar_metricas_temporais(
                metricas=metricas,
                titulo=f"Métricas - Últimas {periodo/3600:.1f}h",
                agrupar_por_dimensao=True,
                eventos=eventos,
                salvar=salvar
            )
            
            # Visualização de correlação
            visualizacoes["correlacao"] = self.visualizador.visualizar_correlacao_metricas(
                metricas=metricas,
                titulo="Matriz de Correlação entre Métricas",
                salvar=salvar
            )
            
            # Estatísticas de eventos
            eventos_por_tipo = {}
            eventos_por_severidade = {}
            
            for evento in eventos:
                if evento.tipo not in eventos_por_tipo:
                    eventos_por_tipo[evento.tipo] = 0
                eventos_por_tipo[evento.tipo] += 1
                
                if evento.severidade not in eventos_por_severidade:
                    eventos_por_severidade[evento.severidade] = 0
                eventos_por_severidade[evento.severidade] += 1
            
            # Estatísticas de diagnósticos
            anomalias_detectadas = {}
            
            for diagnostico in diagnosticos:
                for anomalia, _ in diagnostico.anomalias_detectadas:
                    if anomalia.id not in anomalias_detectadas:
                        anomalias_detectadas[anomalia.id] = 0
                    anomalias_detectadas[anomalia.id] += 1
            
            # Estatísticas de planos
            acoes_por_tipo = {tipo.name: 0 for tipo in TipoAcao}
            planos_por_status = {}
            
            for plano in planos:
                for acao in plano.acoes:
                    acoes_por_tipo[acao.tipo.name] += 1
                
                if plano.status not in planos_por_status:
                    planos_por_status[plano.status] = 0
                planos_por_status[plano.status] += 1
            
            # Cria relatório
            relatorio = {
                "periodo": {
                    "inicio": datetime.datetime.fromtimestamp(inicio_periodo).isoformat(),
                    "fim": datetime.datetime.fromtimestamp(agora).isoformat(),
                    "duracao_horas": periodo / 3600
                },
                "estatisticas": {
                    "metricas": {
                        "total": len(metricas),
                        "por_dimensao": {dim: len([m for m in metricas if m.dimensao == dim]) for dim in set(m.dimensao for m in metricas)}
                    },
                    "eventos": {
                        "total": len(eventos),
                        "por_tipo": eventos_por_tipo,
                        "por_severidade": eventos_por_severidade
                    },
                    "diagnosticos": {
                        "total": len(diagnosticos),
                        "anomalias_detectadas": anomalias_detectadas
                    },
                    "planos": {
                        "total": len(planos),
                        "acoes_por_tipo": acoes_por_tipo,
                        "por_status": planos_por_status
                    }
                },
                "visualizacoes": visualizacoes
            }
            
            # Salva relatório em arquivo
            if salvar:
                nome_arquivo = f"relatorio_{int(time.time())}.json"
                caminho_completo = os.path.join(self.visualizador.diretorio_saida, nome_arquivo)
                
                with open(caminho_completo, 'w') as f:
                    json.dump(relatorio, f, indent=2)
                
                logger.info(f"Relatório salvo em {caminho_completo}")
                relatorio["arquivo"] = caminho_completo
            
            return relatorio


# Exemplo de uso
if __name__ == "__main__":
    # Cria observabilidade
    observabilidade = Observabilidade4D(diretorio_saida="/tmp/visualizacoes")
    
    # Inicia interface
    observabilidade.iniciar_interface()
    
    # Simula métricas
    for i in range(50):
        # Métrica de latência
        latencia = MetricaDimensional(
            nome="api_latencia_p95",
            valor=100 + 10 * math.sin(i / 5) + random.uniform(-5, 5),
            timestamp=time.time() - (50 - i) * 60,  # Últimos 50 minutos
            contexto={"endpoint": "/api/data"},
            dimensao="latencia",
            unidade="ms"
        )
        
        # Métrica de throughput
        throughput = MetricaDimensional(
            nome="api_requests_media_movel",
            valor=200 + 20 * math.cos(i / 10) + random.uniform(-10, 10),
            timestamp=time.time() - (50 - i) * 60,
            contexto={"tipo": "media_movel", "janela": 10},
            dimensao="throughput",
            unidade="ops/s"
        )
        
        # Métrica de erros
        erros = MetricaDimensional(
            nome="api_errors_http",
            valor=max(0, 5 + 3 * math.sin(i / 8) + random.uniform(-2, 2)),
            timestamp=time.time() - (50 - i) * 60,
            contexto={"categoria": "http"},
            dimensao="erros",
            unidade="contagem"
        )
        
        # Registra métricas
        observabilidade.registrar_metrica(latencia)
        observabilidade.registrar_metrica(throughput)
        observabilidade.registrar_metrica(erros)
        
        # Simula eventos
        if i % 10 == 0:
            evento = EventoSistema(
                id=f"evento_{i}",
                tipo="sistema",
                timestamp=time.time() - (50 - i) * 60,
                descricao=f"Evento de sistema {i}",
                severidade="info",
                fonte="simulacao",
                dados={}
            )
            
            observabilidade.registrar_evento(evento)
    
    # Simula diagnóstico
    from diagnostico.diagnostico import Diagnostico, PadraoAnomalia
    
    # Cria padrões de anomalia
    padrao_latencia = PadraoAnomalia(
        id="latencia_alta",
        nome="Latência elevada",
        dimensoes=["latencia"],
        metricas_relacionadas=["api_latencia_p95"],
        limiar_confianca=0.7,
        descricao="Padrão de latência elevada nas APIs"
    )
    
    # Cria diagnóstico
    diagnostico = Diagnostico(
        id=f"diag_{int(time.time())}",
        timestamp=time.time(),
        anomalias_detectadas=[(padrao_latencia, 0.85)],
        metricas_analisadas=[
            latencia,
            throughput,
            erros
        ],
        causa_raiz="Latência elevada devido a carga excessiva",
        confianca=0.8,
        recomendacoes=["Aumentar recursos", "Implementar cache"],
        contexto={}
    )
    
    observabilidade.registrar_diagnostico(diagnostico)
    
    # Simula plano de ação
    from gerador_acoes.gerador_acoes import PlanoAcao, AcaoCorretiva, TipoAcao
    
    # Cria ações
    acao1 = AcaoCorretiva(
        id=f"acao_1_{int(time.time())}",
        tipo=TipoAcao.HOTFIX,
        descricao="Aumentar recursos para reduzir latência",
        comandos=[
            "kubectl scale deployment api-service --replicas=5",
            "kubectl set resources deployment api-service --limits=cpu=2,memory=4Gi"
        ],
        impacto_estimado={
            "latencia": 0.4,
            "throughput": 0.1
        },
        tempo_estimado=60,
        recursos_necessarios={},
        prioridade=0.8,
        risco=0.2
    )
    
    acao2 = AcaoCorretiva(
        id=f"acao_2_{int(time.time())}",
        tipo=TipoAcao.REFATORACAO,
        descricao="Implementar camada de cache",
        comandos=[
            "kubectl apply -f redis-cache.yaml",
            "kubectl set env deployment api-service ENABLE_CACHE=true"
        ],
        impacto_estimado={
            "latencia": 0.6,
            "throughput": 0.3
        },
        tempo_estimado=300,
        recursos_necessarios={},
        prioridade=0.6,
        risco=0.4
    )
    
    # Cria plano
    plano = PlanoAcao(
        id=f"plano_{int(time.time())}",
        diagnostico_id=diagnostico.id,
        acoes=[acao1, acao2],
        timestamp=time.time(),
        score=0.75,
        status="criado",
        metricas_impactadas=["api_latencia_p95", "api_requests_media_movel"]
    )
    
    observabilidade.registrar_plano(plano)
    
    # Atualiza status do plano
    time.sleep(2)
    observabilidade.atualizar_status_plano(plano.id, "em_execucao")
    
    # Cria visualizações
    visualizacao_metricas = observabilidade.visualizar_metricas(periodo=3600)
    print(f"Visualização de métricas: {visualizacao_metricas}")
    
    visualizacao_correlacao = observabilidade.visualizar_correlacao()
    print(f"Visualização de correlação: {visualizacao_correlacao}")
    
    visualizacao_diagnostico = observabilidade.visualizar_diagnostico(diagnostico.id)
    print(f"Visualização de diagnóstico: {visualizacao_diagnostico}")
    
    visualizacao_plano = observabilidade.visualizar_plano(plano.id)
    print(f"Visualização de plano: {visualizacao_plano}")
    
    # Gera relatório
    relatorio = observabilidade.gerar_relatorio(periodo=3600)
    print(f"Relatório gerado: {relatorio.get('arquivo')}")
    
    # Mantém o programa em execução para a interface web
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Programa encerrado pelo usuário")
