# Módulo de Monitoramento Multidimensional

import time
import threading
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import logging
import json
from datetime import datetime
from fastapi import FastAPI
import random

# Configuração do FastAPI
app = FastAPI(title="Monitoramento Multidimensional")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("MonitoramentoMultidimensional")

# Estruturas de dados para métricas
@dataclass
class MetricaDimensional:
    """
    Estrutura de dados para métricas multidimensionais com contexto temporal e espacial.
    
    Como cristais de dados que capturam a essência do sistema,
    cada métrica é um prisma que refrata a realidade operacional
    em dimensões que transcendem o óbvio.
    """
    id: str
    nome: str
    valor: float
    timestamp: float
    dimensao: str
    unidade: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
    contexto: Dict[str, Any] = field(default_factory=dict)
    confianca: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a métrica para formato de dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "valor": self.valor,
            "timestamp": self.timestamp,
            "dimensao": self.dimensao,
            "unidade": self.unidade,
            "tags": self.tags,
            "metadados": self.metadados,
            "contexto": self.contexto,
            "confianca": self.confianca
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricaDimensional':
        """Cria uma instância de métrica a partir de um dicionário."""
        return cls(
            id=data["id"],
            nome=data["nome"],
            valor=data["valor"],
            timestamp=data["timestamp"],
            dimensao=data["dimensao"],
            unidade=data["unidade"],
            tags=data.get("tags", {}),
            metadados=data.get("metadados", {}),
            contexto=data.get("contexto", {}),
            confianca=data.get("confianca", 1.0)
        )

# Armazenamento de métricas em memória
metricas_store: List[MetricaDimensional] = []

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/api/metricas")
async def get_metricas():
    # Se não houver métricas, gerar algumas de exemplo
    if not metricas_store:
        metricas_store.extend([
            MetricaDimensional(
                id=f"metric_{i}",
                nome=nome,
                valor=random.uniform(0, 100),
                timestamp=time.time(),
                dimensao=dim,
                unidade=unidade,
                tags={"ambiente": "producao"},
                metadados={"fonte": "simulador"}
            )
            for i, (nome, dim, unidade) in enumerate([
                ("cpu_usage", "recursos", "percentual"),
                ("memory_usage", "recursos", "percentual"),
                ("latency", "performance", "ms"),
                ("throughput", "performance", "rps"),
                ("error_rate", "qualidade", "percentual")
            ])
        ])
    
    return [metric.__dict__ for metric in metricas_store]

@app.get("/api/metricas/{metrica_id}")
async def get_metrica(metrica_id: str):
    for metrica in metricas_store:
        if metrica.id == metrica_id:
            return metrica.__dict__
    return {"error": "Métrica não encontrada"}, 404

class ColetorBase:
    """
    Classe base para todos os coletores de métricas.
    
    Como sentinelas silenciosas que observam o fluxo do tempo,
    os coletores capturam sinais sutis nas correntes de dados,
    testemunhas imparciais do comportamento do sistema.
    """
    def __init__(self, nome: str, intervalo: float = 1.0):
        self.nome = nome
        self.intervalo = intervalo
        self.ativo = False
        self.thread = None
        self.callbacks = []
        logger.info(f"Coletor {self.nome} inicializado com intervalo de {self.intervalo}s")
    
    def iniciar(self):
        """Inicia a coleta de métricas em uma thread separada."""
        if self.ativo:
            logger.warning(f"Coletor {self.nome} já está ativo")
            return
        
        self.ativo = True
        self.thread = threading.Thread(target=self._loop_coleta, daemon=True)
        self.thread.start()
        logger.info(f"Coletor {self.nome} iniciado")
    
    def parar(self):
        """Para a coleta de métricas."""
        self.ativo = False
        if self.thread:
            self.thread.join(timeout=2*self.intervalo)
        logger.info(f"Coletor {self.nome} parado")
    
    def registrar_callback(self, callback):
        """Registra uma função de callback para receber métricas coletadas."""
        self.callbacks.append(callback)
        logger.debug(f"Callback registrado para coletor {self.nome}")
    
    def _loop_coleta(self):
        """Loop principal de coleta que executa em uma thread separada."""
        while self.ativo:
            try:
                metricas = self.coletar()
                for metrica in metricas:
                    for callback in self.callbacks:
                        callback(metrica)
            except Exception as e:
                logger.error(f"Erro na coleta de {self.nome}: {str(e)}")
            
            time.sleep(self.intervalo)
    
    def coletar(self) -> List[MetricaDimensional]:
        """
        Método abstrato para coleta de métricas.
        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar o método coletar()")


class ColetorThroughput(ColetorBase):
    """
    Coletor especializado em métricas de throughput operacional.
    
    Como um contador de batimentos cardíacos do sistema,
    mede o pulso das operações, o ritmo vital
    que sustenta o fluxo de processamento.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, janela_media: int = 10):
        super().__init__(nome, intervalo)
        self.janela_media = janela_media
        self.historico = deque(maxlen=janela_media)
        self.contador = 0
        self.ultimo_timestamp = time.time()
    
    def registrar_operacao(self, quantidade: int = 1, contexto: Dict[str, Any] = None):
        """Registra a ocorrência de operações para cálculo de throughput."""
        self.contador += quantidade
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de throughput baseadas no contador de operações."""
        agora = time.time()
        delta_t = agora - self.ultimo_timestamp
        
        if delta_t > 0:
            taxa = self.contador / delta_t
            self.historico.append(taxa)
            media_movel = sum(self.historico) / len(self.historico)
            
            # Reset para próxima janela
            self.contador = 0
            self.ultimo_timestamp = agora
            
            # Criação das métricas
            metrica_instantanea = MetricaDimensional(
                id=f"{self.nome}_instantaneo",
                nome=f"{self.nome}_instantaneo",
                valor=taxa,
                timestamp=agora,
                dimensao="throughput",
                unidade="ops/s"
            )
            
            metrica_media = MetricaDimensional(
                id=f"{self.nome}_media_movel",
                nome=f"{self.nome}_media_movel",
                valor=media_movel,
                timestamp=agora,
                dimensao="throughput",
                unidade="ops/s"
            )
            
            return [metrica_instantanea, metrica_media]
        
        return []


class ColetorErros(ColetorBase):
    """
    Coletor especializado em métricas de erros contextuais.
    
    Como um arqueólogo de falhas que escava nas camadas do tempo,
    cataloga os vestígios de exceções e anomalias,
    preservando o contexto em que ocorreram.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, categorias: List[str] = None):
        super().__init__(nome, intervalo)
        self.categorias = categorias or ["geral"]
        self.contadores = {cat: 0 for cat in self.categorias}
        self.contextos = {cat: [] for cat in self.categorias}
        self.lock = threading.Lock()
    
    def registrar_erro(self, categoria: str = "geral", contexto: Dict[str, Any] = None):
        """Registra a ocorrência de um erro com seu contexto."""
        with self.lock:
            if categoria not in self.contadores:
                self.contadores[categoria] = 0
                self.contextos[categoria] = []
            
            self.contadores[categoria] += 1
            if contexto:
                self.contextos[categoria].append(contexto)
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de erros baseadas nos contadores por categoria."""
        metricas = []
        agora = time.time()
        
        with self.lock:
            for categoria, contador in self.contadores.items():
                # Contexto agregado para esta categoria
                contexto_agregado = {
                    "categoria": categoria,
                    "exemplos": self.contextos[categoria][-5:] if self.contextos[categoria] else []
                }
                
                metrica = MetricaDimensional(
                    id=f"{self.nome}_{categoria}",
                    nome=f"{self.nome}_{categoria}",
                    valor=contador,
                    timestamp=agora,
                    dimensao="erros",
                    unidade="contagem"
                )
                
                metricas.append(metrica)
                
                # Reset dos contadores após coleta
                self.contadores[categoria] = 0
                self.contextos[categoria] = []
        
        return metricas


class ColetorLatencia(ColetorBase):
    """
    Coletor especializado em métricas de latência cognitiva.
    
    Como um cronometrista do pensamento artificial,
    mede os intervalos entre estímulo e resposta,
    o tempo de viagem das ideias através do labirinto neural.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, percentis: List[float] = None):
        super().__init__(nome, intervalo)
        self.percentis = percentis or [50, 90, 95, 99]
        self.medicoes = []
        self.lock = threading.Lock()
    
    def registrar_latencia(self, valor: float, contexto: Dict[str, Any] = None):
        """Registra uma medição de latência com seu contexto."""
        with self.lock:
            self.medicoes.append((valor, contexto or {}))
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de latência baseadas nas medições registradas."""
        metricas = []
        agora = time.time()
        
        with self.lock:
            if not self.medicoes:
                return []
            
            # Extrai valores de latência
            valores = [m[0] for m in self.medicoes]
            contextos = [m[1] for m in self.medicoes]
            
            # Calcula estatísticas
            media = np.mean(valores)
            mediana = np.median(valores)
            percentis_calc = np.percentile(valores, self.percentis)
            
            # Cria métricas para média e mediana
            metrica_media = MetricaDimensional(
                id=f"{self.nome}_media",
                nome=f"{self.nome}_media",
                valor=media,
                timestamp=agora,
                dimensao="latencia",
                unidade="ms"
            )
            
            metrica_mediana = MetricaDimensional(
                id=f"{self.nome}_mediana",
                nome=f"{self.nome}_mediana",
                valor=mediana,
                timestamp=agora,
                dimensao="latencia",
                unidade="ms"
            )
            
            metricas.extend([metrica_media, metrica_mediana])
            
            # Cria métricas para percentis
            for i, p in enumerate(self.percentis):
                metrica_percentil = MetricaDimensional(
                    id=f"{self.nome}_p{p}",
                    nome=f"{self.nome}_p{p}",
                    valor=percentis_calc[i],
                    timestamp=agora,
                    dimensao="latencia",
                    unidade="ms"
                )
                metricas.append(metrica_percentil)
            
            # Reset das medições após coleta
            self.medicoes = []
        
        return metricas


class ColetorRecursosFractais(ColetorBase):
    """
    Coletor especializado em métricas de consumo de recursos fractais.
    
    Como um cartógrafo de paisagens computacionais,
    mapeia o terreno multidimensional dos recursos,
    revelando padrões auto-similares em diferentes escalas.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, dimensoes: List[str] = None):
        super().__init__(nome, intervalo)
        self.dimensoes = dimensoes or ["cpu", "memoria", "io", "rede"]
        self.leituras = {dim: [] for dim in self.dimensoes}
        self.escalas = [0.1, 1.0, 10.0]  # Escalas de tempo para análise fractal
    
    def registrar_consumo(self, dimensao: str, valor: float, escala: float = 1.0, contexto: Dict[str, Any] = None):
        """Registra uma medição de consumo de recurso com escala e contexto."""
        if dimensao in self.dimensoes:
            self.leituras[dimensao].append((valor, escala, contexto or {}))
    
    def _calcular_dimensao_fractal(self, valores: List[float]) -> float:
        """
        Calcula uma aproximação da dimensão fractal usando o método box-counting.
        Esta é uma implementação simplificada para demonstração.
        """
        if len(valores) < 10:
            return 1.0  # Valor padrão para poucas amostras
        
        # Normaliza valores
        valores_norm = np.array(valores) / max(valores)
        
        # Calcula dimensão fractal aproximada
        steps = min(5, len(valores) // 2)
        counts = []
        scales = []
        
        for step in range(1, steps + 1):
            box_size = 1.0 / step
            boxes = np.ceil(valores_norm / box_size)
            unique_boxes = len(np.unique(boxes))
            counts.append(unique_boxes)
            scales.append(box_size)
        
        if len(counts) < 2:
            return 1.0
        
        # Regressão log-log
        log_counts = np.log(counts)
        log_scales = np.log(scales)
        
        # Calcula inclinação (dimensão fractal)
        slope, _ = np.polyfit(log_scales, log_counts, 1)
        return abs(slope)
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de consumo de recursos com análise fractal."""
        metricas = []
        agora = time.time()
        
        for dimensao in self.dimensoes:
            if not self.leituras[dimensao]:
                continue
            
            # Extrai valores por escala
            por_escala = {}
            for valor, escala, _ in self.leituras[dimensao]:
                if escala not in por_escala:
                    por_escala[escala] = []
                por_escala[escala].append(valor)
            
            # Calcula métricas por escala
            for escala, valores in por_escala.items():
                media = np.mean(valores)
                variacao = np.std(valores) if len(valores) > 1 else 0
                
                metrica = MetricaDimensional(
                    id=f"{self.nome}_{dimensao}_escala_{escala}",
                    nome=f"{self.nome}_{dimensao}_escala_{escala}",
                    valor=media,
                    timestamp=agora,
                    dimensao="recursos",
                    unidade="percentual"
                )
                metricas.append(metrica)
            
            # Calcula dimensão fractal se houver dados suficientes
            todos_valores = [v for v, _, _ in self.leituras[dimensao]]
            if len(todos_valores) >= 10:
                dim_fractal = self._calcular_dimensao_fractal(todos_valores)
                
                metrica_fractal = MetricaDimensional(
                    id=f"{self.nome}_{dimensao}_dimensao_fractal",
                    nome=f"{self.nome}_{dimensao}_dimensao_fractal",
                    valor=dim_fractal,
                    timestamp=agora,
                    dimensao="fractal",
                    unidade="dimensao"
                )
                metricas.append(metrica_fractal)
            
            # Reset das leituras após coleta
            self.leituras[dimensao] = []
        
        return metricas


class AgregadorTemporal:
    """
    Agrega métricas em diferentes janelas temporais.
    
    Como um tecelão do tempo que entrelaça os fios dos eventos,
    cria padrões visíveis nas tramas do passado,
    revelando tendências ocultas nas dobras temporais.
    """
    def __init__(self, janelas: List[int] = None):
        self.janelas = janelas or [60, 300, 900, 3600]  # segundos
        self.metricas = {}  # Dict[str, Dict[int, List[MetricaDimensional]]]
        self.lock = threading.Lock()
        logger.info(f"AgregadorTemporal inicializado com janelas: {self.janelas}")
    
    def adicionar_metrica(self, metrica: MetricaDimensional):
        """
        Adiciona uma métrica às janelas temporais.
        
        Args:
            metrica: Métrica a ser adicionada
        """
        with self.lock:
            nome_chave = f"{metrica.dimensao}:{metrica.nome}"
            
            if nome_chave not in self.metricas:
                self.metricas[nome_chave] = {janela: [] for janela in self.janelas}
            
            # Adiciona a métrica a cada janela
            agora = time.time()
            for janela in self.janelas:
                # Remove métricas antigas
                self.metricas[nome_chave][janela] = [
                    m for m in self.metricas[nome_chave][janela]
                    if agora - m.timestamp <= janela
                ]
                
                # Adiciona nova métrica
                self.metricas[nome_chave][janela].append(metrica)
    
    def obter_metricas_janela(self, dimensao: str, nome: str, janela: int) -> List[MetricaDimensional]:
        """
        Obtém métricas de uma janela temporal específica.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            janela: Tamanho da janela em segundos
            
        Returns:
            Lista de métricas na janela
        """
        with self.lock:
            nome_chave = f"{dimensao}:{nome}"
            
            if nome_chave not in self.metricas or janela not in self.metricas[nome_chave]:
                return []
            
            # Filtra métricas dentro da janela
            agora = time.time()
            return [
                m for m in self.metricas[nome_chave][janela]
                if agora - m.timestamp <= janela
            ]
    
    def calcular_estatisticas(self, dimensao: str, nome: str, janela: int) -> Dict[str, float]:
        """
        Calcula estatísticas para uma métrica em uma janela temporal.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            janela: Tamanho da janela em segundos
            
        Returns:
            Dicionário com estatísticas (média, mediana, min, max, etc.)
        """
        metricas = self.obter_metricas_janela(dimensao, nome, janela)
        
        if not metricas:
            return {
                "contagem": 0,
                "media": None,
                "mediana": None,
                "min": None,
                "max": None,
                "desvio_padrao": None
            }
        
        valores = [m.valor for m in metricas]
        
        return {
            "contagem": len(valores),
            "media": np.mean(valores),
            "mediana": np.median(valores),
            "min": min(valores),
            "max": max(valores),
            "desvio_padrao": np.std(valores) if len(valores) > 1 else 0
        }
    
    def detectar_tendencia(self, dimensao: str, nome: str, janela: int) -> Dict[str, Any]:
        """
        Detecta tendência para uma métrica em uma janela temporal.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            janela: Tamanho da janela em segundos
            
        Returns:
            Dicionário com informações de tendência
        """
        metricas = self.obter_metricas_janela(dimensao, nome, janela)
        
        if len(metricas) < 3:
            return {
                "direcao": "estavel",
                "inclinacao": 0,
                "confianca": 0,
                "amostras": len(metricas)
            }
        
        # Ordena por timestamp
        metricas.sort(key=lambda m: m.timestamp)
        
        # Extrai valores e timestamps
        valores = np.array([m.valor for m in metricas])
        timestamps = np.array([m.timestamp for m in metricas])
        
        # Normaliza timestamps para começar de 0
        timestamps = timestamps - timestamps[0]
        
        # Regressão linear
        if len(timestamps) > 1:
            inclinacao, intercepto = np.polyfit(timestamps, valores, 1)
            
            # Calcula valores previstos
            valores_previstos = inclinacao * timestamps + intercepto
            
            # Calcula erro quadrático médio
            mse = np.mean((valores - valores_previstos) ** 2)
            
            # Calcula variância total
            variancia_total = np.var(valores)
            
            # Calcula R² (coeficiente de determinação)
            r2 = 1 - (mse / variancia_total) if variancia_total > 0 else 0
            
            # Determina direção
            if abs(inclinacao) < 0.001 or r2 < 0.3:
                direcao = "estavel"
            elif inclinacao > 0:
                direcao = "crescente"
            else:
                direcao = "decrescente"
            
            return {
                "direcao": direcao,
                "inclinacao": inclinacao,
                "confianca": r2,
                "amostras": len(metricas)
            }
        
        return {
            "direcao": "estavel",
            "inclinacao": 0,
            "confianca": 0,
            "amostras": len(metricas)
        }


class ProcessadorContexto:
    """
    Enriquece dados brutos com informações contextuais.
    
    Como um alquimista de dados que transmuta sinais em significados,
    destila a essência contextual das métricas brutas,
    revelando a narrativa oculta nos números.
    """
    def __init__(self):
        self.contextos_globais = {}
        self.processadores = {}
        self.lock = threading.Lock()
        logger.info("ProcessadorContexto inicializado")
    
    def adicionar_contexto_global(self, chave: str, valor: Any):
        """
        Adiciona uma informação ao contexto global.
        
        Args:
            chave: Chave do contexto
            valor: Valor do contexto
        """
        with self.lock:
            self.contextos_globais[chave] = valor
    
    def registrar_processador(self, dimensao: str, processador: Callable[[MetricaDimensional, Dict[str, Any]], Dict[str, Any]]):
        """
        Registra um processador de contexto para uma dimensão específica.
        
        Args:
            dimensao: Dimensão da métrica
            processador: Função que recebe (metrica, contexto_global) e retorna contexto adicional
        """
        with self.lock:
            if dimensao not in self.processadores:
                self.processadores[dimensao] = []
            
            self.processadores[dimensao].append(processador)
            logger.info(f"Processador de contexto registrado para dimensão '{dimensao}'")
    
    def processar(self, metrica: MetricaDimensional) -> MetricaDimensional:
        """
        Processa uma métrica, enriquecendo seu contexto.
        
        Args:
            metrica: Métrica a ser processada
            
        Returns:
            Métrica com contexto enriquecido
        """
        with self.lock:
            # Cria cópia da métrica para não modificar a original
            nova_metrica = MetricaDimensional(
                id=metrica.id,
                nome=metrica.nome,
                valor=metrica.valor,
                timestamp=metrica.timestamp,
                dimensao=metrica.dimensao,
                unidade=metrica.unidade,
                contexto=metrica.contexto.copy(),
                confianca=metrica.confianca
            )
            
            # Adiciona contexto global
            for chave, valor in self.contextos_globais.items():
                if chave not in nova_metrica.contexto:
                    nova_metrica.contexto[chave] = valor
            
            # Aplica processadores específicos da dimensão
            if metrica.dimensao in self.processadores:
                for processador in self.processadores[metrica.dimensao]:
                    try:
                        contexto_adicional = processador(metrica, self.contextos_globais)
                        if contexto_adicional:
                            nova_metrica.contexto.update(contexto_adicional)
                    except Exception as e:
                        logger.error(f"Erro no processador de contexto: {str(e)}")
            
            return nova_metrica


class AnalisadorFluxoContínuo:
    """
    Processa streams de dados em tempo real.
    
    Como um observador atento no rio de dados que flui incessantemente,
    identifica padrões efêmeros nas correntes de informação,
    capturando insights antes que se dissolvam no oceano do tempo.
    """
    def __init__(self, tamanho_janela: int = 100):
        self.janela_deslizante = {}  # Dict[str, deque]
        self.callbacks = {}  # Dict[str, List[Callable]]
        self.tamanho_janela = tamanho_janela
        self.lock = threading.Lock()
        logger.info(f"AnalisadorFluxoContínuo inicializado com janela de {tamanho_janela}")
    
    def registrar_callback(self, dimensao: str, callback: Callable[[List[MetricaDimensional]], None]):
        """
        Registra um callback para processar métricas de uma dimensão específica.
        
        Args:
            dimensao: Dimensão da métrica
            callback: Função que recebe lista de métricas e processa
        """
        with self.lock:
            if dimensao not in self.callbacks:
                self.callbacks[dimensao] = []
            
            self.callbacks[dimensao].append(callback)
            logger.info(f"Callback registrado para dimensão '{dimensao}'")
    
    def processar_metrica(self, metrica: MetricaDimensional):
        """
        Processa uma métrica, adicionando-a à janela deslizante e notificando callbacks.
        
        Args:
            metrica: Métrica a ser processada
        """
        with self.lock:
            dimensao = metrica.dimensao
            
            # Inicializa janela se não existir
            if dimensao not in self.janela_deslizante:
                self.janela_deslizante[dimensao] = deque(maxlen=self.tamanho_janela)
            
            # Adiciona métrica à janela
            self.janela_deslizante[dimensao].append(metrica)
            
            # Notifica callbacks
            if dimensao in self.callbacks:
                janela_atual = list(self.janela_deslizante[dimensao])
                for callback in self.callbacks[dimensao]:
                    try:
                        callback(janela_atual)
                    except Exception as e:
                        logger.error(f"Erro no callback de fluxo contínuo: {str(e)}")
    
    def obter_janela(self, dimensao: str) -> List[MetricaDimensional]:
        """
        Obtém a janela atual de métricas para uma dimensão.
        
        Args:
            dimensao: Dimensão da métrica
            
        Returns:
            Lista de métricas na janela
        """
        with self.lock:
            if dimensao not in self.janela_deslizante:
                return []
            
            return list(self.janela_deslizante[dimensao])
    
    def calcular_estatisticas_janela(self, dimensao: str) -> Dict[str, Dict[str, Any]]:
        """
        Calcula estatísticas para todas as métricas na janela de uma dimensão.
        
        Args:
            dimensao: Dimensão da métrica
            
        Returns:
            Dicionário com estatísticas por nome de métrica
        """
        janela = self.obter_janela(dimensao)
        
        if not janela:
            return {}
        
        # Agrupa por nome
        por_nome = {}
        for metrica in janela:
            if metrica.nome not in por_nome:
                por_nome[metrica.nome] = []
            por_nome[metrica.nome].append(metrica)
        
        # Calcula estatísticas por nome
        estatisticas = {}
        for nome, metricas in por_nome.items():
            valores = [m.valor for m in metricas]
            
            estatisticas[nome] = {
                "contagem": len(valores),
                "media": np.mean(valores),
                "mediana": np.median(valores),
                "min": min(valores),
                "max": max(valores),
                "desvio_padrao": np.std(valores) if len(valores) > 1 else 0,
                "ultima_atualizacao": max(m.timestamp for m in metricas)
            }
        
        return estatisticas


# Exemplo de uso
if __name__ == "__main__":
    import uvicorn
    
    # Inicializa os coletores
    coletor_throughput = ColetorThroughput("api_requests", intervalo=5.0)
    coletor_erros = ColetorErros("api_errors", intervalo=5.0)
    coletor_latencia = ColetorLatencia("api_latencia", intervalo=5.0)
    
    # Inicia os coletores
    logger.info("Módulo random importado com sucesso")
    logger.info(f"Coletor {coletor_throughput.nome} inicializado com intervalo de {coletor_throughput.intervalo}s")
    logger.info(f"Coletor {coletor_erros.nome} inicializado com intervalo de {coletor_erros.intervalo}s")
    logger.info(f"Coletor {coletor_latencia.nome} inicializado com intervalo de {coletor_latencia.intervalo}s")
    
    coletor_throughput.iniciar()
    coletor_erros.iniciar()
    coletor_latencia.iniciar()
    
    # Registra algumas operações para teste
    logger.info("Tentando registrar operação com random.randint")
    valor = random.randint(1, 10)
    logger.info(f"Valor gerado: {valor}")
    coletor_throughput.registrar_operacao(valor)
    
    # Inicia o servidor
    uvicorn.run(app, host="0.0.0.0", port=8080)
