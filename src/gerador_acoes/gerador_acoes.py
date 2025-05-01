# Módulo de Gerador de Ações Emergentes

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union, Callable, Set
from dataclasses import dataclass, field
import logging
import json
import time
import threading
from collections import deque, defaultdict
import random
import math
from datetime import datetime
import copy
import uuid
from enum import Enum, auto
import requests
import os
from functools import wraps

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("GeradorAcoesEmergentes")

# Configurações do sistema
class Config:
    """Configurações do sistema carregadas do ConfigMap."""
    def __init__(self):
        self.score_minimo = float(os.getenv('SCORE_MINIMO', '0.3'))
        self.timeout_api = int(os.getenv('TIMEOUT_API', '5'))
        self.api_token = os.getenv('API_TOKEN', '')
        self.max_acoes_redesign = int(os.getenv('MAX_ACOES_REDESIGN', '2'))
        self.prioridade_hotfix = float(os.getenv('PRIORIDADE_HOTFIX', '0.8'))
        self.prioridade_refatoracao = float(os.getenv('PRIORIDADE_REFATORACAO', '0.5'))
        self.prioridade_redesign = float(os.getenv('PRIORIDADE_REDESIGN', '0.3'))

config = Config()

# Decorator para logging de operações críticas
def log_operacao_critica(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Iniciando operação crítica: {func.__name__}")
        try:
            resultado = func(*args, **kwargs)
            logger.info(f"Operação {func.__name__} concluída com sucesso")
            return resultado
        except Exception as e:
            logger.error(f"Erro na operação {func.__name__}: {str(e)}")
            raise
    return wrapper

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
    
    def __post_init__(self):
        if not 0 <= self.severidade <= 1:
            raise ValueError("Severidade deve estar entre 0 e 1")

@dataclass
class Diagnostico:
    """Classe local que substitui a importação de diagnostico.diagnostico.Diagnostico"""
    id: str
    timestamp: float
    anomalias_detectadas: List[Tuple[PadraoAnomalia, float]]
    metricas_analisadas: List[str]
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        for _, confianca in self.anomalias_detectadas:
            if not 0 <= confianca <= 1:
                raise ValueError("Confiança deve estar entre 0 e 1")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Diagnostico':
        """Cria uma instância de Diagnostico a partir de um dicionário."""
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
            
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            anomalias_detectadas=anomalias,
            metricas_analisadas=data.get("metricas_analisadas", []),
            contexto=data.get("contexto", {})
        )

# Funções para comunicação com outros serviços
@log_operacao_critica
def obter_metricas_do_monitoramento(metrica_id=None):
    """
    Obtém métricas do serviço de monitoramento via API REST.
    
    Args:
        metrica_id: ID opcional da métrica específica
        
    Returns:
        Lista de métricas ou uma métrica específica
        
    Raises:
        ValueError: Se os dados retornados forem inválidos
        requests.exceptions.RequestException: Em caso de erro na requisição
    """
    try:
        base_url = "http://monitoramento:8080/api/metricas"
        if metrica_id:
            url = f"{base_url}/{metrica_id}"
        else:
            url = base_url
            
        headers = {
            "Authorization": f"Bearer {config.api_token}"
        }
        
        response = requests.get(url, headers=headers, timeout=config.timeout_api)
        response.raise_for_status()
        
        data = response.json()
        
        if metrica_id:
            # Valida dados da métrica
            if not all(k in data for k in ["id", "nome", "valor", "timestamp", "dimensao", "unidade"]):
                raise ValueError("Dados da métrica incompletos")
                
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
            # Valida lista de métricas
            if not isinstance(data, list):
                raise ValueError("Dados retornados não são uma lista de métricas")
                
            metricas = []
            for item in data:
                if not all(k in item for k in ["id", "nome", "valor", "timestamp", "dimensao", "unidade"]):
                    logger.warning(f"Métrica inválida encontrada: {item}")
                    continue
                    
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
            
    except requests.Timeout:
        logger.error("Timeout ao obter métricas do monitoramento")
        return []
    except requests.ConnectionError:
        logger.error("Erro de conexão ao obter métricas do monitoramento")
        return []
    except requests.HTTPError as e:
        logger.error(f"Erro HTTP ao obter métricas: {e.response.status_code}")
        return []
    except ValueError as e:
        logger.error(f"Erro de validação de dados: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro inesperado ao obter métricas: {e}")
        return []

@log_operacao_critica
def obter_diagnostico(diagnostico_id):
    """
    Obtém um diagnóstico do serviço de diagnóstico via API REST.
    
    Args:
        diagnostico_id: ID do diagnóstico
        
    Returns:
        Objeto Diagnostico ou None se ocorrer erro
        
    Raises:
        ValueError: Se os dados retornados forem inválidos
        requests.exceptions.RequestException: Em caso de erro na requisição
    """
    try:
        url = f"http://diagnostico:8080/api/diagnosticos/{diagnostico_id}"
        headers = {
            "Authorization": f"Bearer {config.api_token}"
        }
        
        response = requests.get(url, headers=headers, timeout=config.timeout_api)
        response.raise_for_status()
        
        data = response.json()
        
        # Valida dados do diagnóstico
        if not all(k in data for k in ["id", "timestamp", "anomalias_detectadas"]):
            raise ValueError("Dados do diagnóstico incompletos")
            
        return Diagnostico.from_dict(data)
        
    except requests.Timeout:
        logger.error("Timeout ao obter diagnóstico")
        return None
    except requests.ConnectionError:
        logger.error("Erro de conexão ao obter diagnóstico")
        return None
    except requests.HTTPError as e:
        logger.error(f"Erro HTTP ao obter diagnóstico: {e.response.status_code}")
        return None
    except ValueError as e:
        logger.error(f"Erro de validação de dados: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao obter diagnóstico: {e}")
        return None

class TipoAcao(Enum):
    """
    Enumeração dos tipos de ações corretivas.
    
    HOTFIX: Ação imediata para estabilização
    REFATORACAO: Solução estrutural de médio prazo
    REDESIGN: Evolução preventiva de longo prazo
    """
    HOTFIX = auto()
    REFATORACAO = auto()
    REDESIGN = auto()

@dataclass
class AcaoCorretiva:
    """
    Representa uma ação corretiva gerada pelo sistema.
    
    Como uma semente de transformação plantada no solo da adversidade,
    cada ação é um potencial de mudança que aguarda o momento
    de florescer em uma nova realidade operacional.
    
    Exemplo de uso:
        acao = AcaoCorretiva(
            id="acao_123",
            tipo=TipoAcao.HOTFIX,
            descricao="Aumentar recursos do serviço",
            comandos=["kubectl scale deployment app --replicas=3"],
            impacto_estimado={"performance": 0.8},
            tempo_estimado=300,
            recursos_necessarios={"cpu": "2", "memory": "4Gi"}
        )
    """
    id: str
    tipo: TipoAcao
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
    
    def __post_init__(self):
        # Validações
        if not 0 <= self.risco <= 1:
            raise ValueError("Risco deve estar entre 0 e 1")
        if not 0 <= self.prioridade <= 1:
            raise ValueError("Prioridade deve estar entre 0 e 1")
        if self.tempo_estimado <= 0:
            raise ValueError("Tempo estimado deve ser positivo")
        for impacto in self.impacto_estimado.values():
            if not 0 <= impacto <= 1:
                raise ValueError("Impacto estimado deve estar entre 0 e 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a ação para formato de dicionário."""
        return {
            "id": self.id,
            "tipo": self.tipo.name,
            "descricao": self.descricao,
            "comandos": self.comandos,
            "impacto_estimado": self.impacto_estimado,
            "tempo_estimado": self.tempo_estimado,
            "recursos_necessarios": self.recursos_necessarios,
            "prioridade": self.prioridade,
            "dependencias": self.dependencias,
            "risco": self.risco,
            "reversivel": self.reversivel,
            "contexto": self.contexto
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AcaoCorretiva':
        """Cria uma instância de ação a partir de um dicionário."""
        return cls(
            id=data["id"],
            tipo=TipoAcao[data["tipo"]],
            descricao=data["descricao"],
            comandos=data["comandos"],
            impacto_estimado=data["impacto_estimado"],
            tempo_estimado=data["tempo_estimado"],
            recursos_necessarios=data["recursos_necessarios"],
            prioridade=data.get("prioridade", 0.0),
            dependencias=data.get("dependencias", []),
            risco=data.get("risco", 0.5),
            reversivel=data.get("reversivel", True),
            contexto=data.get("contexto", {})
        )

@dataclass
class PlanoAcao:
    """
    Representa um plano de ação completo com múltiplas ações corretivas.
    
    Como uma partitura para a orquestra da autocura,
    cada plano é uma composição harmônica de intervenções
    que conduz o sistema de volta à estabilidade.
    """
    id: str
    diagnostico_id: str
    acoes: List[AcaoCorretiva]
    timestamp: float
    score: float = 0.0
    status: str = "criado"  # criado, em_execucao, concluido, falhou, cancelado
    resultado: Optional[Dict[str, Any]] = None
    metricas_impactadas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o plano para formato de dicionário."""
        return {
            "id": self.id,
            "diagnostico_id": self.diagnostico_id,
            "acoes": [a.to_dict() for a in self.acoes],
            "timestamp": self.timestamp,
            "score": self.score,
            "status": self.status,
            "resultado": self.resultado,
            "metricas_impactadas": self.metricas_impactadas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanoAcao':
        """Cria uma instância de plano a partir de um dicionário."""
        return cls(
            id=data["id"],
            diagnostico_id=data["diagnostico_id"],
            acoes=[AcaoCorretiva.from_dict(a) for a in data["acoes"]],
            timestamp=data["timestamp"],
            score=data.get("score", 0.0),
            status=data.get("status", "criado"),
            resultado=data.get("resultado"),
            metricas_impactadas=data.get("metricas_impactadas", [])
        )

class GeradorHotfix:
    """
    Gera ações de hotfix para estabilização imediata do sistema.
    
    Como um cirurgião de emergência, o GeradorHotfix identifica e implementa
    soluções rápidas para problemas críticos, priorizando a estabilidade
    do sistema acima de tudo.
    
    Exemplo de uso:
        gerador = GeradorHotfix()
        acoes = gerador.gerar_acoes(diagnostico)
    """
    def __init__(self):
        self.templates = {}
        self.eficacia_historica = {}
        self.lock = threading.Lock()
        logger.info("GeradorHotfix inicializado")
    
    @log_operacao_critica
    def registrar_template(self, padrao_anomalia_id: str, template: Dict[str, Any]):
        """
        Registra um novo template de hotfix.
        
        Args:
            padrao_anomalia_id: ID do padrão de anomalia
            template: Template de hotfix
            
        Raises:
            ValueError: Se o template for inválido
        """
        with self.lock:
            # Valida template
            if not all(k in template for k in ["descricao", "comandos"]):
                raise ValueError("Template inválido: campos obrigatórios ausentes")
                
            self.templates[padrao_anomalia_id] = template
            logger.info(f"Template registrado para padrão {padrao_anomalia_id}")
    
    @log_operacao_critica
    def registrar_eficacia(self, acao_id: str, eficacia: float):
        """
        Registra a eficácia de uma ação de hotfix.
        
        Args:
            acao_id: ID da ação
            eficacia: Valor entre 0 e 1 indicando a eficácia
            
        Raises:
            ValueError: Se a eficácia for inválida
        """
        if not 0 <= eficacia <= 1:
            raise ValueError("Eficácia deve estar entre 0 e 1")
            
        with self.lock:
            self.eficacia_historica[acao_id] = eficacia
            logger.info(f"Eficácia {eficacia} registrada para ação {acao_id}")

class MotorRefatoracao:
    """
    Gera ações de refatoração para melhorias estruturais do sistema.
    
    Como um arquiteto de software, o MotorRefatoracao identifica e implementa
    melhorias estruturais que aumentam a manutenibilidade e robustez do sistema,
    sem alterar seu comportamento externo.
    
    Exemplo de uso:
        motor = MotorRefatoracao()
        acoes = motor.gerar_acoes(diagnostico)
    """
    def __init__(self):
        self.padroes_refatoracao = {}
        self.historico_aplicacoes = {}
        self.lock = threading.Lock()
        logger.info("MotorRefatoracao inicializado")
    
    @log_operacao_critica
    def registrar_padrao(self, nome: str, padrao: Dict[str, Any]):
        """
        Registra um novo padrão de refatoração.
        
        Args:
            nome: Nome do padrão
            padrao: Definição do padrão
            
        Raises:
            ValueError: Se o padrão for inválido
        """
        with self.lock:
            # Valida padrão
            if not all(k in padrao for k in ["descricao", "comandos", "impacto_estimado"]):
                raise ValueError("Padrão inválido: campos obrigatórios ausentes")
                
            self.padroes_refatoracao[nome] = padrao
            logger.info(f"Padrão {nome} registrado")
    
    @log_operacao_critica
    def registrar_aplicacao(self, nome_padrao: str, resultado: Dict[str, Any]):
        """
        Registra o resultado da aplicação de um padrão.
        
        Args:
            nome_padrao: Nome do padrão aplicado
            resultado: Resultado da aplicação
            
        Raises:
            ValueError: Se o resultado for inválido
        """
        with self.lock:
            if nome_padrao not in self.padroes_refatoracao:
                raise ValueError(f"Padrão {nome_padrao} não encontrado")
                
            self.historico_aplicacoes[nome_padrao] = resultado
            logger.info(f"Resultado registrado para padrão {nome_padrao}")

class ProjetorRedesign:
    """
    Gera ações de redesign para evolução preventiva do sistema.
    
    Como um urbanista de software, o ProjetorRedesign identifica e propõe
    mudanças arquiteturais significativas que previnem problemas futuros
    e melhoram a escalabilidade do sistema.
    
    Exemplo de uso:
        projetor = ProjetorRedesign()
        acoes = projetor.gerar_acoes(diagnostico)
    """
    def __init__(self):
        self.modelos_redesign = {}
        self.historico_projetos = {}
        self.lock = threading.Lock()
        logger.info("ProjetorRedesign inicializado")
    
    @log_operacao_critica
    def registrar_modelo(self, nome: str, modelo: Dict[str, Any]):
        """
        Registra um novo modelo de redesign.
        
        Args:
            nome: Nome do modelo
            modelo: Definição do modelo
            
        Raises:
            ValueError: Se o modelo for inválido
        """
        with self.lock:
            # Valida modelo
            if not all(k in modelo for k in ["descricao", "comandos", "impacto_estimado"]):
                raise ValueError("Modelo inválido: campos obrigatórios ausentes")
                
            self.modelos_redesign[nome] = modelo
            logger.info(f"Modelo {nome} registrado")
    
    @log_operacao_critica
    def registrar_projeto(self, nome_modelo: str, resultado: Dict[str, Any]):
        """
        Registra o resultado da aplicação de um modelo.
        
        Args:
            nome_modelo: Nome do modelo aplicado
            resultado: Resultado da aplicação
            
        Raises:
            ValueError: Se o resultado for inválido
        """
        with self.lock:
            if nome_modelo not in self.modelos_redesign:
                raise ValueError(f"Modelo {nome_modelo} não encontrado")
                
            self.historico_projetos[nome_modelo] = resultado
            logger.info(f"Resultado registrado para modelo {nome_modelo}")

class OrquestradorAcoes:
    """
    Coordena a geração e execução de planos de ação.
    
    Como um maestro que rege a sinfonia da autocura,
    harmoniza as intervenções em diferentes escalas temporais,
    equilibrando a urgência do presente com a visão do futuro.
    
    Exemplo de uso:
        orquestrador = OrquestradorAcoes()
        plano = orquestrador.gerar_plano_acao(diagnostico)
        resultado = orquestrador.executar_plano(plano.id)
    """
    def __init__(self):
        self.gerador_hotfix = GeradorHotfix()
        self.motor_refatoracao = MotorRefatoracao()
        self.projetor_redesign = ProjetorRedesign()
        self.planos_acao = {}
        self.historico_execucoes = []
        self.lock = threading.Lock()
        logger.info("OrquestradorAcoes inicializado")
    
    @log_operacao_critica
    def gerar_plano_acao(self, diagnostico: Diagnostico) -> PlanoAcao:
        """
        Gera um plano de ação completo com base no diagnóstico.
        
        Args:
            diagnostico: Diagnóstico atual
            
        Returns:
            Plano de ação gerado
            
        Raises:
            ValueError: Se o diagnóstico for inválido
        """
        logger.info(f"Iniciando geração de plano para diagnóstico {diagnostico.id}")
        
        # Valida diagnóstico
        if not diagnostico.anomalias_detectadas:
            raise ValueError("Diagnóstico sem anomalias detectadas")
        
        # Gera ações de diferentes tipos
        acoes_hotfix = self.gerador_hotfix.gerar_acoes(diagnostico)
        acoes_refatoracao = self.motor_refatoracao.gerar_acoes(diagnostico)
        acoes_redesign = self.projetor_redesign.gerar_acoes(diagnostico)
        
        # Combina todas as ações
        todas_acoes = acoes_hotfix + acoes_refatoracao + acoes_redesign
        
        # Ordena ações por prioridade
        todas_acoes.sort(key=lambda a: a.prioridade, reverse=True)
        
        # Cria plano de ação
        plano_id = f"plano_{int(time.time())}_{random.randint(1000, 9999)}"
        
        plano = PlanoAcao(
            id=plano_id,
            diagnostico_id=diagnostico.id,
            acoes=todas_acoes,
            timestamp=time.time()
        )
        
        # Armazena plano
        with self.lock:
            self.planos_acao[plano_id] = plano
        
        logger.info(f"Plano {plano_id} gerado com {len(todas_acoes)} ações")
        return plano

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # Inicializa o orquestrador
    orquestrador = OrquestradorAcoes()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"})
    
    @app.route('/api/acoes/gerar', methods=['POST'])
    def gerar_acoes():
        try:
            data = request.json
            diagnostico_id = data.get('diagnostico_id')
            
            if not diagnostico_id:
                return jsonify({"error": "diagnostico_id é obrigatório"}), 400
            
            # Obtém o diagnóstico
            diagnostico = obter_diagnostico(diagnostico_id)
            
            if not diagnostico:
                return jsonify({"error": f"Diagnóstico {diagnostico_id} não encontrado"}), 404
            
            # Gera plano de ação
            plano = orquestrador.gerar_plano_acao(diagnostico)
            
            return jsonify(plano.to_dict()), 200
            
        except Exception as e:
            logger.error(f"Erro ao gerar ações: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/acoes/planos/<plano_id>', methods=['GET'])
    def obter_plano(plano_id):
        try:
            plano = orquestrador.obter_plano(plano_id)
            
            if not plano:
                return jsonify({"error": f"Plano {plano_id} não encontrado"}), 404
            
            return jsonify(plano.to_dict()), 200
            
        except Exception as e:
            logger.error(f"Erro ao obter plano: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/acoes/planos/<plano_id>/status', methods=['PUT'])
    def atualizar_status_plano(plano_id):
        try:
            data = request.json
            status = data.get('status')
            resultado = data.get('resultado')
            
            if not status:
                return jsonify({"error": "status é obrigatório"}), 400
            
            orquestrador.atualizar_status_plano(plano_id, status, resultado)
            
            return jsonify({"sucesso": True}), 200
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do plano: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080)
