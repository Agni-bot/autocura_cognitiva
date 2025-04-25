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

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("GeradorAcoesEmergentes")

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
def obter_metricas_do_monitoramento(metrica_id=None):
    """
    Obtém métricas do serviço de monitoramento via API REST.
    
    Args:
        metrica_id: ID opcional da métrica específica
        
    Returns:
        Lista de métricas ou uma métrica específica
    """
    try:
        base_url = "http://monitoramento:8080/api/metricas"
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
        url = f"http://diagnostico:8080/api/diagnosticos/{diagnostico_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return Diagnostico.from_dict(data)
        
    except Exception as e:
        logger.error(f"Erro ao obter diagnóstico: {e}")
        return None

class TipoAcao(Enum):
    """
    Enumeração dos tipos de ações corretivas.
    """
    HOTFIX = auto()  # Ação imediata para estabilização
    REFATORACAO = auto()  # Solução estrutural de médio prazo
    REDESIGN = auto()  # Evolução preventiva de longo prazo


@dataclass
class AcaoCorretiva:
    """
    Representa uma ação corretiva gerada pelo sistema.
    
    Como uma semente de transformação plantada no solo da adversidade,
    cada ação é um potencial de mudança que aguarda o momento
    de florescer em uma nova realidade operacional.
    """
    id: str
    tipo: TipoAcao
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]  # Impacto em diferentes dimensões
    tempo_estimado: float  # Em segundos
    recursos_necessarios: Dict[str, Any]
    prioridade: float = 0.0
    dependencias: List[str] = field(default_factory=list)
    risco: float = 0.5  # 0 = sem risco, 1 = risco máximo
    reversivel: bool = True
    contexto: Dict[str, Any] = field(default_factory=dict)
    
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
    Gera soluções imediatas para estabilização do sistema.
    
    Como um médico de emergência no pronto-socorro digital,
    aplica intervenções rápidas para estabilizar o paciente,
    tratando os sintomas enquanto a causa raiz é investigada.
    """
    def __init__(self):
        self.templates = {}
        self.historico_eficacia = {}
        self.lock = threading.Lock()
        logger.info("GeradorHotfix inicializado")
    
    def registrar_template(self, padrao_anomalia_id: str, template: Dict[str, Any]):
        """
        Registra um template de hotfix para um padrão de anomalia específico.
        
        Args:
            padrao_anomalia_id: ID do padrão de anomalia
            template: Dicionário com informações do template
        """
        with self.lock:
            if padrao_anomalia_id not in self.templates:
                self.templates[padrao_anomalia_id] = []
            
            self.templates[padrao_anomalia_id].append(template)
            logger.info(f"Template de hotfix registrado para anomalia '{padrao_anomalia_id}'")
    
    def registrar_eficacia(self, acao_id: str, eficacia: float):
        """
        Registra a eficácia de um hotfix aplicado.
        
        Args:
            acao_id: ID da ação corretiva
            eficacia: Valor de eficácia (0-1)
        """
        with self.lock:
            self.historico_eficacia[acao_id] = {
                "eficacia": eficacia,
                "timestamp": time.time()
            }
    
    def _selecionar_template(self, padrao_anomalia_id: str, contexto: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Seleciona o melhor template para o contexto atual.
        
        Args:
            padrao_anomalia_id: ID do padrão de anomalia
            contexto: Contexto atual do sistema
            
        Returns:
            Template selecionado ou None se não houver templates disponíveis
        """
        with self.lock:
            if padrao_anomalia_id not in self.templates or not self.templates[padrao_anomalia_id]:
                return None
            
            templates = self.templates[padrao_anomalia_id]
            
            # Se houver apenas um template, retorna ele
            if len(templates) == 1:
                return templates[0]
            
            # Calcula score para cada template com base no histórico de eficácia
            scores = []
            
            for template in templates:
                # Verifica condições de aplicabilidade
                if "condicoes" in template:
                    aplicavel = True
                    for chave, valor in template["condicoes"].items():
                        if chave not in contexto or contexto[chave] != valor:
                            aplicavel = False
                            break
                    
                    if not aplicavel:
                        scores.append(-1)  # Template não aplicável
                        continue
                
                # Calcula score baseado em eficácia histórica
                if "acoes_relacionadas" in template:
                    eficacias = []
                    for acao_id in template["acoes_relacionadas"]:
                        if acao_id in self.historico_eficacia:
                            eficacias.append(self.historico_eficacia[acao_id]["eficacia"])
                    
                    if eficacias:
                        score = sum(eficacias) / len(eficacias)
                    else:
                        score = 0.5  # Valor padrão para templates sem histórico
                else:
                    score = 0.5
                
                scores.append(score)
            
            # Seleciona o template com maior score
            max_score = max(scores)
            if max_score < 0:
                return None  # Nenhum template aplicável
            
            indices_max = [i for i, s in enumerate(scores) if s == max_score]
            indice_selecionado = random.choice(indices_max)
            
            return templates[indice_selecionado]
    
    def _preencher_template(self, template: Dict[str, Any], diagnostico: Diagnostico) -> AcaoCorretiva:
        """
        Preenche um template com informações do diagnóstico atual.
        
        Args:
            template: Template de hotfix
            diagnostico: Diagnóstico atual
            
        Returns:
            Ação corretiva gerada
        """
        # Gera ID único para a ação
        acao_id = f"hotfix_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Copia comandos do template
        comandos = copy.deepcopy(template.get("comandos", []))
        
        # Substitui variáveis nos comandos
        for i, cmd in enumerate(comandos):
            # Substitui variáveis do diagnóstico
            for anomalia, conf in diagnostico.anomalias_detectadas:
                cmd = cmd.replace("{anomalia_id}", anomalia.id)
                cmd = cmd.replace("{anomalia_nome}", anomalia.nome)
                cmd = cmd.replace("{confianca}", str(conf))
            
            # Substitui variáveis de contexto
            for chave, valor in diagnostico.contexto.items():
                if isinstance(valor, (str, int, float, bool)):
                    cmd = cmd.replace(f"{{{chave}}}", str(valor))
            
            comandos[i] = cmd
        
        # Cria ação corretiva
        acao = AcaoCorretiva(
            id=acao_id,
            tipo=TipoAcao.HOTFIX,
            descricao=template.get("descricao", "Ação de estabilização imediata"),
            comandos=comandos,
            impacto_estimado=template.get("impacto_estimado", {}),
            tempo_estimado=template.get("tempo_estimado", 60),
            recursos_necessarios=template.get("recursos_necessarios", {}),
            prioridade=template.get("prioridade", 0.8),  # Hotfixes têm prioridade alta por padrão
            dependencias=template.get("dependencias", []),
            risco=template.get("risco", 0.3),
            reversivel=template.get("reversivel", True),
            contexto={
                "diagnostico_id": diagnostico.id,
                "template_id": template.get("id", "desconhecido"),
                "timestamp": time.time()
            }
        )
        
        return acao
    
    def gerar_acoes(self, diagnostico: Diagnostico) -> List[AcaoCorretiva]:
        """
        Gera ações de hotfix com base no diagnóstico atual.
        
        Args:
            diagnostico: Diagnóstico atual
            
        Returns:
            Lista de ações corretivas geradas
        """
        acoes = []
        
        # Gera ações para cada anomalia detectada
        for anomalia, confianca in diagnostico.anomalias_detectadas:
            # Seleciona template
            template = self._selecionar_template(anomalia.id, diagnostico.contexto)
            
            if template:
                # Preenche template
                acao = self._preencher_template(template, diagnostico)
                acoes.append(acao)
            else:
                # Gera ação genérica se não houver template
                acao_id = f"hotfix_gen_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Gera descrição e comandos genéricos baseados na dimensão da anomalia
                descricao = f"Estabilização imediata para {anomalia.nome}"
                comandos = []
                impacto = {}
                
                for dim in anomalia.dimensoes:
                    if dim == "throughput":
                        comandos.append("kubectl scale deployment app-service --replicas=3")
                        impacto["throughput"] = 0.3
                    elif dim == "erros":
                        comandos.append("kubectl rollout restart deployment error-handler")
                        impacto["erros"] = 0.4
                    elif dim == "latencia":
                        comandos.append("redis-cli CONFIG SET maxmemory-policy allkeys-lru")
                        impacto["latencia"] = 0.3
                    elif dim == "recursos":
                        comandos.append("kubectl set resources deployment resource-intensive-app --limits=cpu=2,memory=4Gi")
                        impacto["recursos"] = 0.5
                
                if not comandos:
                    comandos = ["echo 'Ação genérica: monitorar sistema'"]
                
                acao = AcaoCorretiva(
                    id=acao_id,
                    tipo=TipoAcao.HOTFIX,
                    descricao=descricao,
                    comandos=comandos,
                    impacto_estimado=impacto,
                    tempo_estimado=30,
                    recursos_necessarios={},
                    prioridade=0.7,
                    dependencias=[],
                    risco=0.4,
                    reversivel=True,
                    contexto={
                        "diagnostico_id": diagnostico.id,
                        "anomalia_id": anomalia.id,
                        "confianca": confianca,
                        "timestamp": time.time(),
                        "generica": True
                    }
                )
                
                acoes.append(acao)
        
        return acoes


class MotorRefatoracao:
    """
    Desenvolve planos de reestruturação de médio prazo.
    
    Como um arquiteto que redesenha as estruturas internas,
    propõe transformações que preservam a fachada mas renovam as fundações,
    equilibrando a estabilidade presente com a flexibilidade futura.
    """
    def __init__(self):
        self.padroes_refatoracao = {}
        self.historico_aplicacoes = deque(maxlen=100)
        self.lock = threading.Lock()
        logger.info("MotorRefatoracao inicializado")
    
    def registrar_padrao(self, nome: str, padrao: Dict[str, Any]):
        """
        Registra um padrão de refatoração.
        
        Args:
            nome: Nome identificador do padrão
            padrao: Dicionário com informações do padrão
        """
        with self.lock:
            self.padroes_refatoracao[nome] = padrao
            logger.info(f"Padrão de refatoração '{nome}' registrado")
    
    def registrar_aplicacao(self, nome_padrao: str, resultado: Dict[str, Any]):
        """
        Registra o resultado de uma aplicação de padrão.
        
        Args:
            nome_padrao: Nome do padrão aplicado
            resultado: Dicionário com informações do resultado
        """
        with self.lock:
            self.historico_aplicacoes.append({
                "padrao": nome_padrao,
                "resultado": resultado,
                "timestamp": time.time()
            })
    
    def _identificar_padroes_aplicaveis(self, diagnostico: Diagnostico) -> List[str]:
        """
        Identifica padrões de refatoração aplicáveis ao diagnóstico atual.
        
        Args:
            diagnostico: Diagnóstico atual
            
        Returns:
            Lista de nomes de padrões aplicáveis
        """
        aplicaveis = []
        
        with self.lock:
            for nome, padrao in self.padroes_refatoracao.items():
                # Verifica condições de aplicabilidade
                if "condicoes" in padrao:
                    aplicavel = True
                    
                    # Verifica condições de anomalias
                    if "anomalias" in padrao["condicoes"]:
                        anomalias_requeridas = set(padrao["condicoes"]["anomalias"])
                        anomalias_presentes = set(a.id for a, _ in diagnostico.anomalias_detectadas)
                        
                        if not anomalias_requeridas.issubset(anomalias_presentes):
                            aplicavel = False
                    
                    # Verifica condições de contexto
                    if "contexto" in padrao["condicoes"]:
                        for chave, valor in padrao["condicoes"]["contexto"].items():
                            if chave not in diagnostico.contexto or diagnostico.contexto[chave] != valor:
                                aplicavel = False
                                break
                    
                    if aplicavel:
                        aplicaveis.append(nome)
                else:
                    # Se não houver condições específicas, considera aplicável
                    aplicaveis.append(nome)
        
        return aplicaveis
    
    def _gerar_acao_refatoracao(self, nome_padrao: str, diagnostico: Diagnostico) -> AcaoCorretiva:
        """
        Gera uma ação de refatoração com base em um padrão.
        
        Args:
            nome_padrao: Nome do padrão de refatoração
            diagnostico: Diagnóstico atual
            
        Returns:
            Ação corretiva gerada
        """
        with self.lock:
            padrao = self.padroes_refatoracao[nome_padrao]
            
            # Gera ID único para a ação
            acao_id = f"refat_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Copia comandos do padrão
            comandos = copy.deepcopy(padrao.get("comandos", []))
            
            # Substitui variáveis nos comandos
            for i, cmd in enumerate(comandos):
                # Substitui variáveis do diagnóstico
                for anomalia, conf in diagnostico.anomalias_detectadas:
                    cmd = cmd.replace("{anomalia_id}", anomalia.id)
                    cmd = cmd.replace("{anomalia_nome}", anomalia.nome)
                
                # Substitui variáveis de contexto
                for chave, valor in diagnostico.contexto.items():
                    if isinstance(valor, (str, int, float, bool)):
                        cmd = cmd.replace(f"{{{chave}}}", str(valor))
                
                comandos[i] = cmd
            
            # Cria ação corretiva
            acao = AcaoCorretiva(
                id=acao_id,
                tipo=TipoAcao.REFATORACAO,
                descricao=padrao.get("descricao", f"Refatoração usando padrão {nome_padrao}"),
                comandos=comandos,
                impacto_estimado=padrao.get("impacto_estimado", {}),
                tempo_estimado=padrao.get("tempo_estimado", 300),  # Refatorações geralmente levam mais tempo
                recursos_necessarios=padrao.get("recursos_necessarios", {}),
                prioridade=padrao.get("prioridade", 0.5),  # Prioridade média por padrão
                dependencias=padrao.get("dependencias", []),
                risco=padrao.get("risco", 0.5),
                reversivel=padrao.get("reversivel", True),
                contexto={
                    "diagnostico_id": diagnostico.id,
                    "padrao": nome_padrao,
                    "timestamp": time.time()
                }
            )
            
            return acao
    
    def gerar_acoes(self, diagnostico: Diagnostico) -> List[AcaoCorretiva]:
        """
        Gera ações de refatoração com base no diagnóstico atual.
        
        Args:
            diagnostico: Diagnóstico atual
            
        Returns:
            Lista de ações corretivas geradas
        """
        acoes = []
        
        # Identifica padrões aplicáveis
        padroes_aplicaveis = self._identificar_padroes_aplicaveis(diagnostico)
        
        # Gera ações para cada padrão aplicável
        for nome_padrao in padroes_aplicaveis:
            acao = self._gerar_acao_refatoracao(nome_padrao, diagnostico)
            acoes.append(acao)
        
        return acoes


class ProjetorRedesign:
    """
    Projeta transformações profundas para evolução do sistema.
    
    Como um visionário que enxerga além do horizonte do presente,
    concebe futuros alternativos onde as limitações atuais são transcendidas,
    traçando caminhos evolutivos que conduzem a novos patamares de capacidade.
    """
    def __init__(self):
        self.modelos_redesign = {}
        self.historico_projetos = []
        self.lock = threading.Lock()
        logger.info("ProjetorRedesign inicializado")
    
    def registrar_modelo(self, nome: str, modelo: Dict[str, Any]):
        """
        Registra um modelo de redesign.
        
        Args:
            nome: Nome identificador do modelo
            modelo: Dicionário com informações do modelo
        """
        with self.lock:
            self.modelos_redesign[nome] = modelo
            logger.info(f"Modelo de redesign '{nome}' registrado")
    
    def registrar_projeto(self, nome_modelo: str, resultado: Dict[str, Any]):
        """
        Registra o resultado de um projeto de redesign.
        
        Args:
            nome_modelo: Nome do modelo aplicado
            resultado: Dicionário com informações do resultado
        """
        with self.lock:
            self.historico_projetos.append({
                "modelo": nome_modelo,
                "resultado": resultado,
                "timestamp": time.time()
            })
    
    def _avaliar_aplicabilidade(self, modelo: Dict[str, Any], diagnostico: Diagnostico) -> Tuple[bool, float]:
        """
        Avalia a aplicabilidade de um modelo de redesign ao diagnóstico atual.
        
        Args:
            modelo: Modelo de redesign
            diagnostico: Diagnóstico atual
            
        Returns:
            Tuple (aplicável, score)
        """
        # Verifica condições de aplicabilidade
        if "condicoes" in modelo:
            # Verifica padrões de anomalias recorrentes
            if "anomalias_recorrentes" in modelo["condicoes"]:
                # Em um sistema real, verificaria o histórico de anomalias
                # Aqui, simplificamos assumindo que todas as anomalias no diagnóstico são recorrentes
                anomalias_requeridas = set(modelo["condicoes"]["anomalias_recorrentes"])
                anomalias_presentes = set(a.id for a, _ in diagnostico.anomalias_detectadas)
                
                if not anomalias_requeridas.issubset(anomalias_presentes):
                    return False, 0.0
            
            # Verifica condições de contexto
            if "contexto" in modelo["condicoes"]:
                for chave, valor in modelo["condicoes"]["contexto"].items():
                    if chave not in diagnostico.contexto or diagnostico.contexto[chave] != valor:
                        return False, 0.0
        
        # Calcula score de aplicabilidade
        score = 0.5  # Valor padrão
        
        # Ajusta score com base em fatores específicos
        if "fatores_score" in modelo:
            for fator in modelo["fatores_score"]:
                if fator["tipo"] == "anomalia_presente":
                    # Verifica se anomalia específica está presente
                    for anomalia, conf in diagnostico.anomalias_detectadas:
                        if anomalia.id == fator["anomalia_id"]:
                            score += fator.get("ajuste", 0.1) * conf
                            break
                
                elif fator["tipo"] == "contexto":
                    # Verifica valor de contexto
                    chave = fator["chave"]
                    if chave in diagnostico.contexto:
                        valor = diagnostico.contexto[chave]
                        valor_esperado = fator["valor"]
                        
                        if valor == valor_esperado:
                            score += fator.get("ajuste", 0.1)
        
        # Limita score entre 0 e 1
        score = max(0.0, min(1.0, score))
        
        return True, score
    
    def _gerar_acao_redesign(self, nome_modelo: str, diagnostico: Diagnostico, score: float) -> AcaoCorretiva:
        """
        Gera uma ação de redesign com base em um modelo.
        
        Args:
            nome_modelo: Nome do modelo de redesign
            diagnostico: Diagnóstico atual
            score: Score de aplicabilidade
            
        Returns:
            Ação corretiva gerada
        """
        with self.lock:
            modelo = self.modelos_redesign[nome_modelo]
            
            # Gera ID único para a ação
            acao_id = f"redesign_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Copia comandos do modelo
            comandos = copy.deepcopy(modelo.get("comandos", []))
            
            # Substitui variáveis nos comandos
            for i, cmd in enumerate(comandos):
                # Substitui variáveis do diagnóstico
                for anomalia, conf in diagnostico.anomalias_detectadas:
                    cmd = cmd.replace("{anomalia_id}", anomalia.id)
                    cmd = cmd.replace("{anomalia_nome}", anomalia.nome)
                
                # Substitui variáveis de contexto
                for chave, valor in diagnostico.contexto.items():
                    if isinstance(valor, (str, int, float, bool)):
                        cmd = cmd.replace(f"{{{chave}}}", str(valor))
                
                comandos[i] = cmd
            
            # Cria ação corretiva
            acao = AcaoCorretiva(
                id=acao_id,
                tipo=TipoAcao.REDESIGN,
                descricao=modelo.get("descricao", f"Redesign usando modelo {nome_modelo}"),
                comandos=comandos,
                impacto_estimado=modelo.get("impacto_estimado", {}),
                tempo_estimado=modelo.get("tempo_estimado", 1800),  # Redesigns geralmente levam mais tempo
                recursos_necessarios=modelo.get("recursos_necessarios", {}),
                prioridade=modelo.get("prioridade", 0.3) * score,  # Ajusta prioridade pelo score
                dependencias=modelo.get("dependencias", []),
                risco=modelo.get("risco", 0.7),  # Redesigns geralmente têm mais risco
                reversivel=modelo.get("reversivel", False),  # Redesigns geralmente não são facilmente reversíveis
                contexto={
                    "diagnostico_id": diagnostico.id,
                    "modelo": nome_modelo,
                    "score": score,
                    "timestamp": time.time()
                }
            )
            
            return acao
    
    def gerar_acoes(self, diagnostico: Diagnostico) -> List[AcaoCorretiva]:
        """
        Gera ações de redesign com base no diagnóstico atual.
        
        Args:
            diagnostico: Diagnóstico atual
            
        Returns:
            Lista de ações corretivas geradas
        """
        acoes = []
        
        # Avalia aplicabilidade de cada modelo
        with self.lock:
            for nome_modelo, modelo in self.modelos_redesign.items():
                aplicavel, score = self._avaliar_aplicabilidade(modelo, diagnostico)
                
                if aplicavel and score > 0.3:  # Só considera modelos com score mínimo
                    acao = self._gerar_acao_redesign(nome_modelo, diagnostico, score)
                    acoes.append(acao)
        
        # Ordena ações por prioridade
        acoes.sort(key=lambda a: a.prioridade, reverse=True)
        
        # Limita número de ações de redesign (são mais complexas)
        return acoes[:2]


class OrquestradorAcoes:
    """
    Coordena a geração e execução de planos de ação.
    
    Como um maestro que rege a sinfonia da autocura,
    harmoniza as intervenções em diferentes escalas temporais,
    equilibrando a urgência do presente com a visão do futuro.
    """
    def __init__(self):
        self.gerador_hotfix = GeradorHotfix()
        self.motor_refatoracao = MotorRefatoracao()
        self.projetor_redesign = ProjetorRedesign()
        self.planos_acao = {}
        self.historico_execucoes = []
        self.lock = threading.Lock()
        logger.info("OrquestradorAcoes inicializado")
    
    def gerar_plano_acao(self, diagnostico: Diagnostico) -> PlanoAcao:
        """
        Gera um plano de ação completo com base no diagnóstico.
        
        Args:
            diagnostico: Diagnóstico atual
            
        Returns:
            Plano de ação gerado
        """
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
        
        return plano
    
    def obter_plano(self, plano_id: str) -> Optional[PlanoAcao]:
        """
        Obtém um plano de ação pelo ID.
        
        Args:
            plano_id: ID do plano
            
        Returns:
            Plano de ação ou None se não encontrado
        """
        with self.lock:
            return self.planos_acao.get(plano_id)
    
    def atualizar_status_plano(self, plano_id: str, status: str, resultado: Dict[str, Any] = None):
        """
        Atualiza o status de um plano de ação.
        
        Args:
            plano_id: ID do plano
            status: Novo status
            resultado: Resultado opcional da execução
        """
        with self.lock:
            if plano_id in self.planos_acao:
                plano = self.planos_acao[plano_id]
                plano.status = status
                
                if resultado:
                    plano.resultado = resultado
                
                # Registra no histórico se concluído ou falhou
                if status in ["concluido", "falhou"]:
                    self.historico_execucoes.append({
                        "plano_id": plano_id,
                        "status": status,
                        "timestamp": time.time(),
                        "resultado": resultado
                    })
    
    def avaliar_eficacia_acoes(self, plano_id: str, metricas_antes: List[MetricaDimensional], 
                             metricas_depois: List[MetricaDimensional]) -> Dict[str, float]:
        """
        Avalia a eficácia das ações executadas comparando métricas antes e depois.
        
        Args:
            plano_id: ID do plano executado
            metricas_antes: Métricas antes da execução
            metricas_depois: Métricas depois da execução
            
        Returns:
            Dicionário com scores de eficácia por ação
        """
        with self.lock:
            if plano_id not in self.planos_acao:
                return {}
            
            plano = self.planos_acao[plano_id]
            
            # Agrupa métricas por nome
            metricas_antes_dict = {m.nome: m for m in metricas_antes}
            metricas_depois_dict = {m.nome: m for m in metricas_depois}
            
            # Calcula melhorias por métrica
            melhorias = {}
            
            for nome in set(metricas_antes_dict.keys()) & set(metricas_depois_dict.keys()):
                metrica_antes = metricas_antes_dict[nome]
                metrica_depois = metricas_depois_dict[nome]
                
                # Calcula melhoria relativa
                if metrica_antes.dimensao == "erros":
                    # Para erros, menor é melhor
                    if metrica_antes.valor > 0:
                        melhoria = max(0, (metrica_antes.valor - metrica_depois.valor) / metrica_antes.valor)
                    else:
                        melhoria = 0 if metrica_depois.valor > 0 else 1
                elif metrica_antes.dimensao == "latencia":
                    # Para latência, menor é melhor
                    if metrica_antes.valor > 0:
                        melhoria = max(0, (metrica_antes.valor - metrica_depois.valor) / metrica_antes.valor)
                    else:
                        melhoria = 0 if metrica_depois.valor > 0 else 1
                elif metrica_antes.dimensao == "throughput":
                    # Para throughput, maior é melhor
                    if metrica_antes.valor > 0:
                        melhoria = max(0, (metrica_depois.valor - metrica_antes.valor) / metrica_antes.valor)
                    else:
                        melhoria = 1 if metrica_depois.valor > 0 else 0
                else:
                    # Para outras dimensões, assume que menor é melhor
                    if metrica_antes.valor > 0:
                        melhoria = max(0, (metrica_antes.valor - metrica_depois.valor) / metrica_antes.valor)
                    else:
                        melhoria = 0 if metrica_depois.valor > 0 else 1
                
                melhorias[nome] = melhoria
            
            # Calcula eficácia por ação
            eficacia_acoes = {}
            
            for acao in plano.acoes:
                # Calcula eficácia com base no impacto estimado
                score_eficacia = 0.0
                peso_total = 0.0
                
                for metrica, impacto in acao.impacto_estimado.items():
                    if metrica in melhorias:
                        score_eficacia += melhorias[metrica] * impacto
                        peso_total += impacto
                
                if peso_total > 0:
                    eficacia_acoes[acao.id] = score_eficacia / peso_total
                else:
                    eficacia_acoes[acao.id] = 0.0
                
                # Registra eficácia para ações de hotfix
                if acao.tipo == TipoAcao.HOTFIX:
                    self.gerador_hotfix.registrar_eficacia(acao.id, eficacia_acoes[acao.id])
            
            return eficacia_acoes

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # Inicializa o orquestrador
    orquestrador = OrquestradorAcoes()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "timestamp": time.time()})
    
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
