# Módulo de Diagnóstico por Rede Neural de Alta Ordem

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
import logging
import json
import time
import threading
from collections import deque, defaultdict
import networkx as nx
from scipy import stats
import random
import math
from datetime import datetime

# Importação do módulo de monitoramento
from monitoramento.monitoramento import MetricaDimensional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("DiagnosticoRedeNeural")

@dataclass
class PadraoAnomalia:
    """
    Representa um padrão de anomalia detectado no sistema.
    
    Como uma constelação de sintomas no céu da cognição,
    cada padrão é uma assinatura única de desequilíbrio,
    um hieróglifo que conta a história de uma perturbação.
    """
    id: str
    nome: str
    dimensoes: List[str]
    metricas_relacionadas: List[str]
    limiar_confianca: float
    padrao_temporal: Optional[List[float]] = None
    funcao_deteccao: Optional[Callable] = None
    descricao: str = ""
    
    def corresponde(self, metricas: List[MetricaDimensional], contexto: Dict[str, Any] = None) -> Tuple[bool, float]:
        """
        Verifica se um conjunto de métricas corresponde a este padrão de anomalia.
        Retorna um tuple (corresponde, confianca).
        """
        if self.funcao_deteccao:
            try:
                return self.funcao_deteccao(metricas, contexto or {})
            except Exception as e:
                logger.error(f"Erro na função de detecção do padrão {self.id}: {str(e)}")
                return False, 0.0
        
        # Implementação padrão se não houver função personalizada
        # Verifica se as métricas necessárias estão presentes
        nomes_metricas = set(m.nome for m in metricas)
        if not all(m in nomes_metricas for m in self.metricas_relacionadas):
            return False, 0.0
        
        # Filtra métricas relevantes
        metricas_relevantes = [m for m in metricas if m.nome in self.metricas_relacionadas]
        
        # Verifica padrão temporal se disponível
        if self.padrao_temporal and len(metricas_relevantes) >= len(self.padrao_temporal):
            # Ordena por timestamp
            metricas_relevantes.sort(key=lambda m: m.timestamp)
            
            # Normaliza valores
            valores = [m.valor for m in metricas_relevantes[-len(self.padrao_temporal):]]
            valores_norm = [(v - min(valores)) / (max(valores) - min(valores) + 1e-10) for v in valores]
            
            # Compara com o padrão
            padrao_norm = [(p - min(self.padrao_temporal)) / (max(self.padrao_temporal) - min(self.padrao_temporal) + 1e-10) 
                          for p in self.padrao_temporal]
            
            # Calcula similaridade (correlação)
            corr, _ = stats.pearsonr(valores_norm, padrao_norm)
            confianca = max(0, (corr + 1) / 2)  # Mapeia de [-1,1] para [0,1]
            
            return confianca >= self.limiar_confianca, confianca
        
        # Implementação simplificada: verifica se alguma métrica está fora dos limites normais
        # Assume que o contexto contém informações sobre limites normais
        if contexto and "limites" in contexto:
            limites = contexto["limites"]
            anomalias = []
            
            for metrica in metricas_relevantes:
                if metrica.nome in limites:
                    min_val, max_val = limites[metrica.nome]
                    if metrica.valor < min_val or metrica.valor > max_val:
                        anomalias.append((metrica.nome, metrica.valor, min_val, max_val))
            
            confianca = len(anomalias) / len(metricas_relevantes) if metricas_relevantes else 0
            return confianca >= self.limiar_confianca, confianca
        
        return False, 0.0


@dataclass
class Diagnostico:
    """
    Resultado de um processo de diagnóstico.
    
    Como um mapa da verdade emergente nas sombras dos dados,
    cada diagnóstico é uma narrativa causal que conecta
    os fragmentos dispersos em uma história coerente.
    """
    id: str
    timestamp: float
    anomalias_detectadas: List[Tuple[PadraoAnomalia, float]]
    metricas_analisadas: List[MetricaDimensional]
    causa_raiz: Optional[str] = None
    confianca: float = 0.0
    recomendacoes: List[str] = field(default_factory=list)
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o diagnóstico para formato de dicionário."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "anomalias": [
                {
                    "id": anomalia.id,
                    "nome": anomalia.nome,
                    "confianca": conf
                }
                for anomalia, conf in self.anomalias_detectadas
            ],
            "metricas_analisadas": [m.to_dict() for m in self.metricas_analisadas],
            "causa_raiz": self.causa_raiz,
            "confianca": self.confianca,
            "recomendacoes": self.recomendacoes,
            "contexto": self.contexto
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], catalogo_anomalias: Dict[str, PadraoAnomalia]) -> 'Diagnostico':
        """Cria uma instância de diagnóstico a partir de um dicionário."""
        anomalias_detectadas = [
            (catalogo_anomalias[a["id"]], a["confianca"])
            for a in data["anomalias"]
            if a["id"] in catalogo_anomalias
        ]
        
        metricas_analisadas = [
            MetricaDimensional.from_dict(m) for m in data["metricas_analisadas"]
        ]
        
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            anomalias_detectadas=anomalias_detectadas,
            metricas_analisadas=metricas_analisadas,
            causa_raiz=data.get("causa_raiz"),
            confianca=data.get("confianca", 0.0),
            recomendacoes=data.get("recomendacoes", []),
            contexto=data.get("contexto", {})
        )


class MotorRegrasEspecialistas:
    """
    Implementa árvores de decisão dinâmicas para diagnóstico.
    
    Como um oráculo digital que consulta o conhecimento acumulado,
    destila sabedoria de experiências passadas em regras adaptativas,
    um jardim de caminhos decisórios que se bifurcam e convergem.
    """
    def __init__(self):
        self.regras = []
        self.historico_execucoes = deque(maxlen=1000)
        self.lock = threading.Lock()
        logger.info("MotorRegrasEspecialistas inicializado")
    
    def adicionar_regra(self, condicao: Callable, acao: Callable, prioridade: int = 0, 
                       nome: str = None, descricao: str = None):
        """
        Adiciona uma regra ao motor.
        
        Args:
            condicao: Função que recebe (metricas, contexto) e retorna um booleano
            acao: Função que recebe (metricas, contexto) e retorna um resultado
            prioridade: Valor numérico para ordenação de regras (maior = mais prioritário)
            nome: Nome identificador da regra
            descricao: Descrição detalhada da regra
        """
        nome = nome or f"regra_{len(self.regras)}"
        
        with self.lock:
            self.regras.append({
                "nome": nome,
                "descricao": descricao,
                "condicao": condicao,
                "acao": acao,
                "prioridade": prioridade,
                "execucoes": 0,
                "sucessos": 0,
                "ultima_execucao": None
            })
            # Ordena regras por prioridade
            self.regras.sort(key=lambda r: r["prioridade"], reverse=True)
        
        logger.info(f"Regra '{nome}' adicionada com prioridade {prioridade}")
    
    def executar(self, metricas: List[MetricaDimensional], contexto: Dict[str, Any] = None) -> List[Any]:
        """
        Executa todas as regras aplicáveis e retorna os resultados.
        
        Args:
            metricas: Lista de métricas para análise
            contexto: Dicionário com informações contextuais
            
        Returns:
            Lista de resultados das ações executadas
        """
        contexto = contexto or {}
        resultados = []
        
        with self.lock:
            for regra in self.regras:
                try:
                    # Verifica se a condição é satisfeita
                    if regra["condicao"](metricas, contexto):
                        # Executa a ação
                        resultado = regra["acao"](metricas, contexto)
                        
                        # Atualiza estatísticas
                        regra["execucoes"] += 1
                        regra["ultima_execucao"] = time.time()
                        if resultado is not None:
                            regra["sucessos"] += 1
                        
                        # Registra execução no histórico
                        self.historico_execucoes.append({
                            "regra": regra["nome"],
                            "timestamp": regra["ultima_execucao"],
                            "resultado": resultado is not None,
                            "contexto": {k: contexto[k] for k in contexto if isinstance(contexto[k], (str, int, float, bool))}
                        })
                        
                        # Adiciona resultado à lista
                        if resultado is not None:
                            resultados.append(resultado)
                    
                except Exception as e:
                    logger.error(f"Erro ao executar regra '{regra['nome']}': {str(e)}")
        
        return resultados
    
    def avaliar_desempenho(self) -> Dict[str, Any]:
        """
        Avalia o desempenho das regras com base no histórico de execuções.
        Retorna estatísticas sobre cada regra.
        """
        with self.lock:
            estatisticas = []
            
            for regra in self.regras:
                taxa_sucesso = regra["sucessos"] / regra["execucoes"] if regra["execucoes"] > 0 else 0
                
                estatisticas.append({
                    "nome": regra["nome"],
                    "execucoes": regra["execucoes"],
                    "sucessos": regra["sucessos"],
                    "taxa_sucesso": taxa_sucesso,
                    "ultima_execucao": regra["ultima_execucao"],
                    "prioridade": regra["prioridade"]
                })
            
            # Análise do histórico recente
            recentes = list(self.historico_execucoes)[-100:]
            regras_recentes = set(e["regra"] for e in recentes)
            
            analise_recente = {
                "total_execucoes": len(recentes),
                "regras_ativas": len(regras_recentes),
                "taxa_sucesso_global": sum(1 for e in recentes if e["resultado"]) / len(recentes) if recentes else 0
            }
            
            return {
                "estatisticas_regras": estatisticas,
                "analise_recente": analise_recente,
                "total_regras": len(self.regras)
            }
    
    def otimizar_prioridades(self):
        """
        Ajusta as prioridades das regras com base no desempenho histórico.
        Regras com maior taxa de sucesso recebem prioridade mais alta.
        """
        with self.lock:
            # Calcula novas prioridades
            for regra in self.regras:
                if regra["execucoes"] > 10:  # Só ajusta regras com histórico suficiente
                    taxa_sucesso = regra["sucessos"] / regra["execucoes"]
                    # Ajusta prioridade mantendo a ordem relativa original
                    nova_prioridade = regra["prioridade"] * (0.8 + 0.4 * taxa_sucesso)
                    regra["prioridade"] = nova_prioridade
            
            # Reordena regras
            self.regras.sort(key=lambda r: r["prioridade"], reverse=True)
            
            logger.info("Prioridades das regras otimizadas com base no desempenho histórico")


class RedeNeuralHierarquica:
    """
    Implementa uma rede neural hierárquica para análise de padrões em múltiplos níveis.
    
    Como uma teia de neurônios artificiais que se estende em dimensões aninhadas,
    cada camada percebe o mundo em uma escala diferente de abstração,
    tecendo significados complexos a partir de sinais elementares.
    """
    def __init__(self, dimensoes_entrada: List[str], camadas_ocultas: List[int] = None):
        self.dimensoes_entrada = dimensoes_entrada
        self.camadas_ocultas = camadas_ocultas or [64, 32, 16]
        self.modelos = {}
        self.preprocessadores = {}
        self.historico_treinamento = {}
        self.lock = threading.Lock()
        
        logger.info(f"RedeNeuralHierarquica inicializada com dimensões: {dimensoes_entrada}")
    
    def _criar_modelo(self, nome: str, dim_entrada: int) -> keras.Model:
        """Cria um modelo de rede neural para uma dimensão específica."""
        modelo = keras.Sequential([
            keras.layers.Dense(self.camadas_ocultas[0], activation='relu', input_shape=(dim_entrada,)),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3)
        ])
        
        # Adiciona camadas ocultas
        for unidades in self.camadas_ocultas[1:]:
            modelo.add(keras.layers.Dense(unidades, activation='relu'))
            modelo.add(keras.layers.BatchNormalization())
            modelo.add(keras.layers.Dropout(0.3))
        
        # Camada de saída para classificação de anomalias
        modelo.add(keras.layers.Dense(1, activation='sigmoid'))
        
        modelo.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(), keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        return modelo
    
    def adicionar_modelo(self, nome: str, colunas_entrada: List[str]):
        """
        Adiciona um novo modelo para uma dimensão específica.
        
        Args:
            nome: Nome identificador do modelo
            colunas_entrada: Lista de nomes de colunas/métricas usadas como entrada
        """
        with self.lock:
            if nome in self.modelos:
                logger.warning(f"Modelo '{nome}' já existe e será substituído")
            
            # Cria modelo
            modelo = self._criar_modelo(nome, len(colunas_entrada))
            
            # Armazena modelo e metadados
            self.modelos[nome] = {
                "modelo": modelo,
                "colunas": colunas_entrada,
                "treinado": False,
                "criado_em": time.time()
            }
            
            # Inicializa histórico de treinamento
            self.historico_treinamento[nome] = []
            
            logger.info(f"Modelo '{nome}' adicionado com {len(colunas_entrada)} entradas")
    
    def treinar(self, nome: str, dados_x: np.ndarray, dados_y: np.ndarray, 
               validacao: float = 0.2, epocas: int = 50, batch_size: int = 32):
        """
        Treina um modelo específico com dados fornecidos.
        
        Args:
            nome: Nome do modelo a ser treinado
            dados_x: Matriz de features de entrada
            dados_y: Vetor de labels (0 = normal, 1 = anomalia)
            validacao: Fração dos dados a ser usada para validação
            epocas: Número de épocas de treinamento
            batch_size: Tamanho do batch para treinamento
        
        Returns:
            Histórico de treinamento
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return None
            
            # Treina modelo
            historico = self.modelos[nome]["modelo"].fit(
                dados_x, dados_y,
                validation_split=validacao,
                epochs=epocas,
                batch_size=batch_size,
                verbose=0
            )
            
            # Atualiza metadados
            self.modelos[nome]["treinado"] = True
            self.modelos[nome]["ultima_atualizacao"] = time.time()
            
            # Registra histórico
            self.historico_treinamento[nome].append({
                "timestamp": time.time(),
                "epocas": epocas,
                "tamanho_dados": len(dados_x),
                "acuracia_final": float(historico.history['accuracy'][-1]),
                "acuracia_validacao": float(historico.history['val_accuracy'][-1]),
                "perda_final": float(historico.history['loss'][-1]),
                "perda_validacao": float(historico.history['val_loss'][-1])
            })
            
            logger.info(f"Modelo '{nome}' treinado com {len(dados_x)} amostras, acurácia: {historico.history['val_accuracy'][-1]:.4f}")
            
            return historico
    
    def prever(self, nome: str, dados: np.ndarray) -> np.ndarray:
        """
        Realiza previsões com um modelo específico.
        
        Args:
            nome: Nome do modelo
            dados: Matriz de features de entrada
            
        Returns:
            Array de previsões (probabilidades de anomalia)
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return np.array([])
            
            if not self.modelos[nome]["treinado"]:
                logger.warning(f"Modelo '{nome}' não foi treinado")
                return np.array([0.5] * len(dados))  # Valor neutro
            
            # Realiza previsão
            previsoes = self.modelos[nome]["modelo"].predict(dados, verbose=0)
            
            return previsoes.flatten()
    
    def avaliar(self, nome: str, dados_x: np.ndarray, dados_y: np.ndarray) -> Dict[str, float]:
        """
        Avalia o desempenho de um modelo específico.
        
        Args:
            nome: Nome do modelo
            dados_x: Matriz de features de entrada
            dados_y: Vetor de labels (0 = normal, 1 = anomalia)
            
        Returns:
            Dicionário com métricas de avaliação
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return {}
            
            if not self.modelos[nome]["treinado"]:
                logger.warning(f"Modelo '{nome}' não foi treinado")
                return {}
            
            # Avalia modelo
            resultados = self.modelos[nome]["modelo"].evaluate(dados_x, dados_y, verbose=0)
            
            # Cria dicionário de métricas
            metricas = {}
            for i, metrica in enumerate(self.modelos[nome]["modelo"].metrics_names):
                metricas[metrica] = float(resultados[i])
            
            # Calcula métricas adicionais
            previsoes = self.prever(nome, dados_x)
            previsoes_bin = (previsoes > 0.5).astype(int)
            
            # Matriz de confusão
            tp = np.sum((previsoes_bin == 1) & (dados_y == 1))
            tn = np.sum((previsoes_bin == 0) & (dados_y == 0))
            fp = np.sum((previsoes_bin == 1) & (dados_y == 0))
            fn = np.sum((previsoes_bin == 0) & (dados_y == 1))
            
            # Métricas derivadas
            metricas["precisao"] = tp / (tp + fp) if (tp + fp) > 0 else 0
            metricas["recall"] = tp / (tp + fn) if (tp + fn) > 0 else 0
            metricas["f1"] = 2 * (metricas["precisao"] * metricas["recall"]) / (metricas["precisao"] + metricas["recall"]) if (metricas["precisao"] + metricas["recall"]) > 0 else 0
            metricas["especificidade"] = tn / (tn + fp) if (tn + fp) > 0 else 0
            
            logger.info(f"Modelo '{nome}' avaliado com {len(dados_x)} amostras, F1: {metricas['f1']:.4f}")
            
            return metricas
    
    def salvar_modelo(self, nome: str, diretorio: str):
        """
        Salva um modelo em disco.
        
        Args:
            nome: Nome do modelo
            diretorio: Diretório onde o modelo será salvo
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return
            
            # Cria diretório se não existir
            os.makedirs(diretorio, exist_ok=True)
            
            # Salva modelo
            caminho_modelo = os.path.join(diretorio, f"{nome}_modelo")
            self.modelos[nome]["modelo"].save(caminho_modelo)
            
            # Salva metadados
            metadados = {
                "colunas": self.modelos[nome]["colunas"],
                "treinado": self.modelos[nome]["treinado"],
                "criado_em": self.modelos[nome]["criado_em"],
                "ultima_atualizacao": self.modelos[nome].get("ultima_atualizacao"),
                "historico": self.historico_treinamento[nome]
            }
            
            caminho_metadados = os.path.join(diretorio, f"{nome}_metadados.json")
            with open(caminho_metadados, 'w') as f:
                json.dump(metadados, f, indent=2)
            
            logger.info(f"Modelo '{nome}' salvo em {diretorio}")
    
    def carregar_modelo(self, nome: str, diretorio: str):
        """
        Carrega um modelo do disco.
        
        Args:
            nome: Nome do modelo
            diretorio: Diretório onde o modelo está salvo
        """
        with self.lock:
            # Verifica se arquivos existem
            caminho_modelo = os.path.join(diretorio, f"{nome}_modelo")
            caminho_metadados = os.path.join(diretorio, f"{nome}_metadados.json")
            
            if not os.path.exists(caminho_modelo) or not os.path.exists(caminho_metadados):
                logger.error(f"Arquivos do modelo '{nome}' não encontrados em {diretorio}")
                return
            
            # Carrega metadados
            with open(caminho_metadados, 'r') as f:
                metadados = json.load(f)
            
            # Carrega modelo
            modelo = keras.models.load_model(caminho_modelo)
            
            # Armazena modelo e metadados
            self.modelos[nome] = {
                "modelo": modelo,
                "colunas": metadados["colunas"],
                "treinado": metadados["treinado"],
                "criado_em": metadados["criado_em"],
                "ultima_atualizacao": metadados.get("ultima_atualizacao")
            }
            
            # Carrega histórico
            self.historico_treinamento[nome] = metadados.get("historico", [])
            
            logger.info(f"Modelo '{nome}' carregado de {diretorio}")


class DetectorAnomaliasCaoticas:
    """
    Identifica comportamentos não-lineares indicativos de problemas.
    
    Como um observador do caos que percebe padrões na aleatoriedade,
    detecta as assinaturas sutis de sistemas complexos em desequilíbrio,
    revelando ordem oculta nas flutuações aparentemente aleatórias.
    """
    def __init__(self, janela_analise: int = 100, dimensao_embedding: int = 3, delay: int = 1):
        self.janela_analise = janela_analise
        self.dimensao_embedding = dimensao_embedding
        self.delay = delay
        self.series_temporais = {}
        self.estatisticas_referencia = {}
        self.lock = threading.Lock()
        logger.info(f"DetectorAnomaliasCaoticas inicializado com dimensão de embedding {dimensao_embedding}")
    
    def adicionar_ponto(self, nome: str, valor: float, timestamp: float):
        """
        Adiciona um ponto a uma série temporal.
        
        Args:
            nome: Nome da série temporal
            valor: Valor do ponto
            timestamp: Timestamp do ponto
        """
        with self.lock:
            if nome not in self.series_temporais:
                self.series_temporais[nome] = []
            
            self.series_temporais[nome].append((timestamp, valor))
            
            # Mantém apenas os pontos mais recentes
            if len(self.series_temporais[nome]) > self.janela_analise * 2:
                self.series_temporais[nome] = self.series_temporais[nome][-self.janela_analise * 2:]
    
    def _reconstruir_espaco_fase(self, serie: List[float]) -> np.ndarray:
        """
        Reconstrói o espaço de fase de uma série temporal usando embedding por atraso.
        
        Args:
            serie: Lista de valores da série temporal
            
        Returns:
            Array 2D com pontos no espaço de fase
        """
        if len(serie) < self.dimensao_embedding * self.delay:
            return np.array([])
        
        # Cria pontos no espaço de fase
        pontos = []
        for i in range(len(serie) - (self.dimensao_embedding - 1) * self.delay):
            ponto = [serie[i + j * self.delay] for j in range(self.dimensao_embedding)]
            pontos.append(ponto)
        
        return np.array(pontos)
    
    def _calcular_entropia_aproximada(self, serie: List[float], m: int = 2, r: float = 0.2) -> float:
        """
        Calcula a entropia aproximada de uma série temporal.
        
        Args:
            serie: Lista de valores da série temporal
            m: Dimensão de embedding
            r: Tolerância (como fração do desvio padrão)
            
        Returns:
            Valor de entropia aproximada
        """
        if len(serie) < 100:  # Mínimo de pontos para cálculo confiável
            return 0.0
        
        # Normaliza série
        serie_norm = np.array(serie)
        std = np.std(serie_norm)
        if std == 0:
            return 0.0
        
        serie_norm = (serie_norm - np.mean(serie_norm)) / std
        
        # Calcula tolerância absoluta
        r_abs = r * std
        
        # Função para contar padrões semelhantes
        def _contar_padroes(m_val):
            padroes = []
            for i in range(len(serie_norm) - m_val + 1):
                padroes.append(serie_norm[i:i+m_val])
            
            # Conta padrões semelhantes
            contagens = []
            for i, padrao_i in enumerate(padroes):
                count = 0
                for j, padrao_j in enumerate(padroes):
                    if i != j and np.max(np.abs(padrao_i - padrao_j)) <= r_abs:
                        count += 1
                contagens.append(count / (len(padroes) - 1))
            
            return np.mean(np.log(contagens)) if contagens else 0
        
        # Calcula entropia aproximada
        return abs(_contar_padroes(m) - _contar_padroes(m + 1))
    
    def _calcular_expoente_lyapunov(self, serie: List[float]) -> float:
        """
        Calcula uma aproximação do expoente de Lyapunov de uma série temporal.
        
        Args:
            serie: Lista de valores da série temporal
            
        Returns:
            Aproximação do expoente de Lyapunov
        """
        if len(serie) < 100:  # Mínimo de pontos para cálculo confiável
            return 0.0
        
        # Reconstrói espaço de fase
        pontos = self._reconstruir_espaco_fase(serie)
        if len(pontos) < 10:
            return 0.0
        
        # Calcula divergência entre pontos próximos
        divergencias = []
        num_pares = min(50, len(pontos) // 2)
        
        for _ in range(num_pares):
            # Seleciona ponto aleatório
            i = random.randint(0, len(pontos) - 2)
            
            # Encontra vizinho mais próximo
            distancias = np.linalg.norm(pontos - pontos[i], axis=1)
            distancias[i] = np.inf  # Exclui o próprio ponto
            j = np.argmin(distancias)
            
            # Calcula divergência após alguns passos
            passos = min(10, len(pontos) - max(i, j))
            if passos <= 0:
                continue
            
            d0 = distancias[j]
            if d0 == 0:
                continue
            
            d1 = np.linalg.norm(pontos[i + passos] - pontos[j + passos])
            
            # Evita divisão por zero
            if d0 > 1e-10:
                divergencia = np.log(d1 / d0) / passos
                divergencias.append(divergencia)
        
        # Retorna média das divergências
        return np.mean(divergencias) if divergencias else 0.0
    
    def calcular_estatisticas_caoticas(self, nome: str) -> Dict[str, float]:
        """
        Calcula estatísticas caóticas para uma série temporal.
        
        Args:
            nome: Nome da série temporal
            
        Returns:
            Dicionário com estatísticas caóticas
        """
        with self.lock:
            if nome not in self.series_temporais or len(self.series_temporais[nome]) < self.janela_analise:
                return {}
            
            # Extrai valores mais recentes
            pontos = self.series_temporais[nome][-self.janela_analise:]
            valores = [p[1] for p in pontos]
            
            # Calcula estatísticas
            entropia = self._calcular_entropia_aproximada(valores)
            expoente = self._calcular_expoente_lyapunov(valores)
            
            # Reconstrói espaço de fase
            pontos_fase = self._reconstruir_espaco_fase(valores)
            
            # Calcula dimensão de correlação (aproximação)
            dim_correlacao = 0.0
            if len(pontos_fase) > 10:
                # Calcula distâncias entre pontos
                distancias = []
                for i in range(len(pontos_fase)):
                    for j in range(i + 1, len(pontos_fase)):
                        distancias.append(np.linalg.norm(pontos_fase[i] - pontos_fase[j]))
                
                # Estima dimensão de correlação
                if distancias:
                    # Usa método de contagem de caixas
                    raios = np.logspace(-2, 0, 10) * np.std(valores)
                    contagens = []
                    
                    for r in raios:
                        count = sum(1 for d in distancias if d < r)
                        contagens.append(count / len(distancias))
                    
                    # Regressão log-log
                    valid_idx = [i for i, c in enumerate(contagens) if c > 0]
                    if len(valid_idx) > 1:
                        log_raios = np.log(raios[valid_idx])
                        log_contagens = np.log(np.array(contagens)[valid_idx])
                        slope, _ = np.polyfit(log_raios, log_contagens, 1)
                        dim_correlacao = abs(slope)
            
            # Calcula estatísticas adicionais
            estatisticas = {
                "entropia_aproximada": entropia,
                "expoente_lyapunov": expoente,
                "dimensao_correlacao": dim_correlacao,
                "desvio_padrao": np.std(valores),
                "curtose": stats.kurtosis(valores),
                "assimetria": stats.skew(valores)
            }
            
            return estatisticas
    
    def definir_referencia(self, nome: str):
        """
        Define as estatísticas atuais como referência para uma série temporal.
        
        Args:
            nome: Nome da série temporal
        """
        with self.lock:
            estatisticas = self.calcular_estatisticas_caoticas(nome)
            if estatisticas:
                self.estatisticas_referencia[nome] = estatisticas
                logger.info(f"Estatísticas de referência definidas para série '{nome}'")
    
    def detectar_anomalia(self, nome: str, limiar: float = 2.0) -> Tuple[bool, Dict[str, float]]:
        """
        Detecta anomalias comparando estatísticas atuais com referência.
        
        Args:
            nome: Nome da série temporal
            limiar: Limiar de desvio para considerar anomalia
            
        Returns:
            Tuple (anomalia_detectada, desvios)
        """
        with self.lock:
            if nome not in self.series_temporais or len(self.series_temporais[nome]) < self.janela_analise:
                return False, {}
            
            # Se não há referência, define a atual
            if nome not in self.estatisticas_referencia:
                self.definir_referencia(nome)
                return False, {}
            
            # Calcula estatísticas atuais
            estatisticas_atuais = self.calcular_estatisticas_caoticas(nome)
            if not estatisticas_atuais:
                return False, {}
            
            # Compara com referência
            desvios = {}
            for chave in estatisticas_atuais:
                if chave in self.estatisticas_referencia[nome] and self.estatisticas_referencia[nome][chave] != 0:
                    desvio = abs(estatisticas_atuais[chave] - self.estatisticas_referencia[nome][chave]) / abs(self.estatisticas_referencia[nome][chave])
                    desvios[chave] = desvio
            
            # Verifica se algum desvio excede o limiar
            anomalia = any(desvio > limiar for desvio in desvios.values())
            
            return anomalia, desvios


class AnalisadorGradientes:
    """
    Monitora mudanças incrementais no comportamento do sistema.
    
    Como um sismógrafo cognitivo que detecta tremores sutis,
    mapeia o relevo das variações graduais no comportamento do sistema,
    revelando tendências emergentes antes que se tornem evidentes.
    """
    def __init__(self, janela_analise: int = 50, sobreposicao: int = 10):
        self.janela_analise = janela_analise
        self.sobreposicao = sobreposicao
        self.series_temporais = {}
        self.gradientes_historicos = {}
        self.lock = threading.Lock()
        logger.info(f"AnalisadorGradientes inicializado com janela de {janela_analise} e sobreposição de {sobreposicao}")
    
    def adicionar_ponto(self, nome: str, valor: float, timestamp: float):
        """
        Adiciona um ponto a uma série temporal.
        
        Args:
            nome: Nome da série temporal
            valor: Valor do ponto
            timestamp: Timestamp do ponto
        """
        with self.lock:
            if nome not in self.series_temporais:
                self.series_temporais[nome] = []
            
            self.series_temporais[nome].append((timestamp, valor))
            
            # Mantém apenas os pontos mais recentes
            max_pontos = self.janela_analise * 10  # Mantém histórico para análise de longo prazo
            if len(self.series_temporais[nome]) > max_pontos:
                self.series_temporais[nome] = self.series_temporais[nome][-max_pontos:]
    
    def _calcular_gradiente(self, pontos: List[Tuple[float, float]]) -> Dict[str, float]:
        """
        Calcula o gradiente de uma série de pontos.
        
        Args:
            pontos: Lista de tuplas (timestamp, valor)
            
        Returns:
            Dicionário com informações do gradiente
        """
        if len(pontos) < 2:
            return {
                "inclinacao": 0.0,
                "r2": 0.0,
                "erro_padrao": 0.0,
                "p_valor": 1.0
            }
        
        # Extrai timestamps e valores
        timestamps = np.array([p[0] for p in pontos])
        valores = np.array([p[1] for p in pontos])
        
        # Normaliza timestamps para começar de 0
        timestamps = timestamps - timestamps[0]
        
        # Regressão linear
        slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, valores)
        
        return {
            "inclinacao": slope,
            "r2": r_value ** 2,
            "erro_padrao": std_err,
            "p_valor": p_value
        }
    
    def calcular_gradientes(self, nome: str) -> Dict[str, Dict[str, float]]:
        """
        Calcula gradientes em diferentes escalas temporais.
        
        Args:
            nome: Nome da série temporal
            
        Returns:
            Dicionário com gradientes em diferentes escalas
        """
        with self.lock:
            if nome not in self.series_temporais or len(self.series_temporais[nome]) < self.janela_analise:
                return {}
            
            # Ordena pontos por timestamp
            pontos = sorted(self.series_temporais[nome], key=lambda p: p[0])
            
            # Calcula gradientes em diferentes janelas
            gradientes = {}
            
            # Curto prazo: janela mais recente
            curto_prazo = pontos[-self.janela_analise:]
            gradientes["curto_prazo"] = self._calcular_gradiente(curto_prazo)
            
            # Médio prazo: 3 janelas
            if len(pontos) >= self.janela_analise * 3:
                medio_prazo = pontos[-self.janela_analise * 3:]
                gradientes["medio_prazo"] = self._calcular_gradiente(medio_prazo)
            
            # Longo prazo: todos os pontos disponíveis
            gradientes["longo_prazo"] = self._calcular_gradiente(pontos)
            
            # Calcula gradientes em janelas deslizantes
            janelas_deslizantes = []
            for i in range(0, len(pontos) - self.janela_analise + 1, self.sobreposicao):
                janela = pontos[i:i + self.janela_analise]
                janelas_deslizantes.append(janela)
            
            # Calcula gradiente para cada janela
            gradientes_deslizantes = []
            for janela in janelas_deslizantes:
                gradiente = self._calcular_gradiente(janela)
                timestamp_medio = sum(p[0] for p in janela) / len(janela)
                gradientes_deslizantes.append((timestamp_medio, gradiente))
            
            # Armazena histórico de gradientes
            if nome not in self.gradientes_historicos:
                self.gradientes_historicos[nome] = []
            
            # Adiciona gradiente atual ao histórico
            if gradientes_deslizantes:
                self.gradientes_historicos[nome].append(gradientes_deslizantes[-1])
            
            # Mantém apenas os gradientes mais recentes
            max_historico = 100
            if len(self.gradientes_historicos[nome]) > max_historico:
                self.gradientes_historicos[nome] = self.gradientes_historicos[nome][-max_historico:]
            
            # Adiciona informações de aceleração
            if len(self.gradientes_historicos[nome]) >= 2:
                # Calcula aceleração (mudança na inclinação)
                ultimo_gradiente = self.gradientes_historicos[nome][-1][1]["inclinacao"]
                penultimo_gradiente = self.gradientes_historicos[nome][-2][1]["inclinacao"]
                delta_t = self.gradientes_historicos[nome][-1][0] - self.gradientes_historicos[nome][-2][0]
                
                if delta_t > 0:
                    aceleracao = (ultimo_gradiente - penultimo_gradiente) / delta_t
                    gradientes["aceleracao"] = aceleracao
            
            return gradientes
    
    def detectar_mudanca_tendencia(self, nome: str, limiar_confianca: float = 0.7) -> Tuple[bool, str, float]:
        """
        Detecta mudanças significativas na tendência.
        
        Args:
            nome: Nome da série temporal
            limiar_confianca: Limiar de confiança (R²) para considerar tendência significativa
            
        Returns:
            Tuple (mudanca_detectada, direcao, confianca)
        """
        with self.lock:
            if nome not in self.gradientes_historicos or len(self.gradientes_historicos[nome]) < 2:
                return False, "estavel", 0.0
            
            # Obtém gradientes recentes
            ultimo_gradiente = self.gradientes_historicos[nome][-1][1]
            penultimo_gradiente = self.gradientes_historicos[nome][-2][1]
            
            # Verifica se ambos são significativos
            if ultimo_gradiente["r2"] < limiar_confianca or penultimo_gradiente["r2"] < limiar_confianca:
                return False, "estavel", max(ultimo_gradiente["r2"], penultimo_gradiente["r2"])
            
            # Verifica mudança de direção
            if (ultimo_gradiente["inclinacao"] > 0 and penultimo_gradiente["inclinacao"] < 0) or \
               (ultimo_gradiente["inclinacao"] < 0 and penultimo_gradiente["inclinacao"] > 0):
                # Mudança de direção
                direcao = "crescente" if ultimo_gradiente["inclinacao"] > 0 else "decrescente"
                return True, direcao, ultimo_gradiente["r2"]
            
            # Verifica aceleração significativa
            delta_inclinacao = abs(ultimo_gradiente["inclinacao"] - penultimo_gradiente["inclinacao"])
            inclinacao_media = (abs(ultimo_gradiente["inclinacao"]) + abs(penultimo_gradiente["inclinacao"])) / 2
            
            if inclinacao_media > 0 and delta_inclinacao / inclinacao_media > 0.5:
                # Aceleração significativa
                direcao = "acelerando" if abs(ultimo_gradiente["inclinacao"]) > abs(penultimo_gradiente["inclinacao"]) else "desacelerando"
                return True, direcao, ultimo_gradiente["r2"]
            
            return False, "estavel", ultimo_gradiente["r2"]


class DiagnosticadorCognitivo:
    """
    Coordena os diferentes componentes de diagnóstico para produzir análises integradas.
    
    Como um maestro que rege a orquestra de análises,
    harmoniza os insights de diferentes instrumentos analíticos,
    compondo uma sinfonia de compreensão que transcende as partes individuais.
    """
    def __init__(self):
        self.motor_regras = MotorRegrasEspecialistas()
        self.rede_neural = None
        self.detector_anomalias = DetectorAnomaliasCaoticas()
        self.analisador_gradientes = AnalisadorGradientes()
        self.catalogo_anomalias = {}
        self.diagnosticos_recentes = deque(maxlen=100)
        self.lock = threading.Lock()
        logger.info("DiagnosticadorCognitivo inicializado")
    
    def inicializar_rede_neural(self, dimensoes_entrada: List[str], camadas_ocultas: List[int] = None):
        """
        Inicializa a rede neural hierárquica.
        
        Args:
            dimensoes_entrada: Lista de dimensões de entrada
            camadas_ocultas: Lista de tamanhos das camadas ocultas
        """
        self.rede_neural = RedeNeuralHierarquica(dimensoes_entrada, camadas_ocultas)
        logger.info("Rede neural hierárquica inicializada")
    
    def registrar_padrao_anomalia(self, padrao: PadraoAnomalia):
        """
        Registra um padrão de anomalia no catálogo.
        
        Args:
            padrao: Padrão de anomalia a ser registrado
        """
        with self.lock:
            self.catalogo_anomalias[padrao.id] = padrao
            logger.info(f"Padrão de anomalia '{padrao.id}' registrado")
    
    def processar_metricas(self, metricas: List[MetricaDimensional]) -> Diagnostico:
        """
        Processa um conjunto de métricas e gera um diagnóstico.
        
        Args:
            metricas: Lista de métricas para análise
            
        Returns:
            Diagnóstico gerado
        """
        with self.lock:
            # Gera ID único para o diagnóstico
            diagnostico_id = f"diag_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Contexto inicial
            contexto = {
                "timestamp": time.time(),
                "num_metricas": len(metricas)
            }
            
            # Processa métricas por dimensão
            metricas_por_dimensao = {}
            for metrica in metricas:
                if metrica.dimensao not in metricas_por_dimensao:
                    metricas_por_dimensao[metrica.dimensao] = []
                metricas_por_dimensao[metrica.dimensao].append(metrica)
            
            # Atualiza séries temporais para análise de gradientes e caos
            for metrica in metricas:
                nome_serie = f"{metrica.dimensao}:{metrica.nome}"
                self.detector_anomalias.adicionar_ponto(nome_serie, metrica.valor, metrica.timestamp)
                self.analisador_gradientes.adicionar_ponto(nome_serie, metrica.valor, metrica.timestamp)
            
            # Executa motor de regras
            resultados_regras = self.motor_regras.executar(metricas, contexto)
            
            # Detecta anomalias
            anomalias_detectadas = []
            
            # Verifica cada padrão de anomalia
            for padrao_id, padrao in self.catalogo_anomalias.items():
                corresponde, confianca = padrao.corresponde(metricas, contexto)
                if corresponde:
                    anomalias_detectadas.append((padrao, confianca))
            
            # Ordena anomalias por confiança
            anomalias_detectadas.sort(key=lambda x: x[1], reverse=True)
            
            # Analisa gradientes para métricas relevantes
            gradientes = {}
            for metrica in metricas:
                nome_serie = f"{metrica.dimensao}:{metrica.nome}"
                grad = self.analisador_gradientes.calcular_gradientes(nome_serie)
                if grad:
                    gradientes[nome_serie] = grad
            
            # Detecta comportamentos caóticos
            caos = {}
            for metrica in metricas:
                nome_serie = f"{metrica.dimensao}:{metrica.nome}"
                anomalia, desvios = self.detector_anomalias.detectar_anomalia(nome_serie)
                if anomalia:
                    caos[nome_serie] = desvios
            
            # Enriquece contexto com análises adicionais
            contexto["gradientes"] = gradientes
            contexto["caos"] = caos
            
            # Identifica causa raiz (implementação simplificada)
            causa_raiz = None
            confianca_causa = 0.0
            
            if anomalias_detectadas:
                # Usa a anomalia mais confiável como causa raiz
                causa_raiz = f"Anomalia detectada: {anomalias_detectadas[0][0].nome}"
                confianca_causa = anomalias_detectadas[0][1]
            
            # Gera recomendações (implementação simplificada)
            recomendacoes = []
            
            if anomalias_detectadas:
                for anomalia, conf in anomalias_detectadas[:3]:  # Top 3 anomalias
                    recomendacoes.append(f"Investigar {anomalia.nome} (confiança: {conf:.2f})")
            
            # Cria diagnóstico
            diagnostico = Diagnostico(
                id=diagnostico_id,
                timestamp=time.time(),
                anomalias_detectadas=anomalias_detectadas,
                metricas_analisadas=metricas,
                causa_raiz=causa_raiz,
                confianca=confianca_causa,
                recomendacoes=recomendacoes,
                contexto=contexto
            )
            
            # Armazena diagnóstico no histórico
            self.diagnosticos_recentes.append(diagnostico)
            
            logger.info(f"Diagnóstico {diagnostico_id} gerado com {len(anomalias_detectadas)} anomalias detectadas")
            
            return diagnostico
    
    def obter_diagnostico(self, diagnostico_id: str) -> Optional[Diagnostico]:
        """
        Obtém um diagnóstico pelo ID.
        
        Args:
            diagnostico_id: ID do diagnóstico
            
        Returns:
            Diagnóstico ou None se não encontrado
        """
        with self.lock:
            for diagnostico in self.diagnosticos_recentes:
                if diagnostico.id == diagnostico_id:
                    return diagnostico
            
            return None
    
    def salvar_diagnostico(self, diagnostico: Diagnostico, caminho: str):
        """
        Salva um diagnóstico em arquivo.
        
        Args:
            diagnostico: Diagnóstico a ser salvo
            caminho: Caminho do arquivo
        """
        with open(caminho, 'w') as f:
            json.dump(diagnostico.to_dict(), f, indent=2)
        
        logger.info(f"Diagnóstico {diagnostico.id} salvo em {caminho}")
    
    def carregar_diagnostico(self, caminho: str) -> Optional[Diagnostico]:
        """
        Carrega um diagnóstico de arquivo.
        
        Args:
            caminho: Caminho do arquivo
            
        Returns:
            Diagnóstico carregado ou None se falhar
        """
        try:
            with open(caminho, 'r') as f:
                dados = json.load(f)
            
            diagnostico = Diagnostico.from_dict(dados, self.catalogo_anomalias)
            logger.info(f"Diagnóstico {diagnostico.id} carregado de {caminho}")
            
            return diagnostico
        
        except Exception as e:
            logger.error(f"Erro ao carregar diagnóstico: {str(e)}")
            return None


# Exemplo de uso
if __name__ == "__main__":
    # Cria diagnosticador
    diagnosticador = DiagnosticadorCognitivo()
    
    # Inicializa rede neural
    diagnosticador.inicializar_rede_neural(["throughput", "erros", "latencia", "recursos"])
    
    # Registra padrões de anomalia
    padrao_latencia = PadraoAnomalia(
        id="latencia_alta",
        nome="Latência elevada",
        dimensoes=["latencia"],
        metricas_relacionadas=["api_latencia_p95", "api_latencia_media"],
        limiar_confianca=0.7,
        descricao="Padrão de latência elevada nas APIs"
    )
    
    padrao_erros = PadraoAnomalia(
        id="erros_http",
        nome="Taxa de erros HTTP elevada",
        dimensoes=["erros"],
        metricas_relacionadas=["api_errors_http"],
        limiar_confianca=0.6,
        descricao="Padrão de erros HTTP acima do normal"
    )
    
    diagnosticador.registrar_padrao_anomalia(padrao_latencia)
    diagnosticador.registrar_padrao_anomalia(padrao_erros)
    
    # Simula métricas
    metricas = [
        MetricaDimensional(
            nome="api_latencia_p95",
            valor=450.0,  # Valor alto
            timestamp=time.time(),
            contexto={"endpoint": "/api/data"},
            dimensao="latencia",
            unidade="ms"
        ),
        MetricaDimensional(
            nome="api_latencia_media",
            valor=120.0,
            timestamp=time.time(),
            contexto={"endpoint": "/api/data"},
            dimensao="latencia",
            unidade="ms"
        ),
        MetricaDimensional(
            nome="api_errors_http",
            valor=15,
            timestamp=time.time(),
            contexto={"categoria": "http"},
            dimensao="erros",
            unidade="contagem"
        ),
        MetricaDimensional(
            nome="api_requests_media_movel",
            valor=250.0,
            timestamp=time.time(),
            contexto={"tipo": "media_movel", "janela": 10},
            dimensao="throughput",
            unidade="ops/s"
        )
    ]
    
    # Gera diagnóstico
    diagnostico = diagnosticador.processar_metricas(metricas)
    
    # Imprime resultado
    print(f"Diagnóstico: {diagnostico.id}")
    print(f"Anomalias detectadas: {len(diagnostico.anomalias_detectadas)}")
    
    for anomalia, confianca in diagnostico.anomalias_detectadas:
        print(f"- {anomalia.nome}: {confianca:.2f}")
    
    print(f"Causa raiz: {diagnostico.causa_raiz} (confiança: {diagnostico.confianca:.2f})")
    print("Recomendações:")
    for rec in diagnostico.recomendacoes:
        print(f"- {rec}")
