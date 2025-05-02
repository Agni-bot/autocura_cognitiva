import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from monitoramento import MetricasSistema

@dataclass
class Diagnostico:
    anomalia_detectada: bool
    tipo_anomalia: str
    nivel_gravidade: float
    recomendacoes: List[str]

class RedeNeuralDiagnostico:
    def __init__(self):
        # Pesos iniciais da rede neural (simplificada)
        self.pesos = {
            'throughput': 0.3,
            'taxa_erro': 0.4,
            'latencia': 0.2,
            'recursos': 0.1
        }
        
    def normalizar_metricas(self, metricas: MetricasSistema) -> Dict[str, float]:
        """Normaliza as métricas para entrada na rede neural"""
        return {
            'throughput': metricas.throughput / 1000,  # Normaliza para 0-1
            'taxa_erro': metricas.taxa_erro / 100,    # Normaliza para 0-1
            'latencia': metricas.latencia / 100,       # Normaliza para 0-1
            'recursos': sum(metricas.uso_recursos.values()) / (3 * 100)  # Média normalizada
        }
    
    def processar_metricas(self, metricas: MetricasSistema) -> float:
        """Processa as métricas através da rede neural"""
        metricas_norm = self.normalizar_metricas(metricas)
        
        # Simulação de uma camada neural simples
        score = sum(
            valor * self.pesos[chave]
            for chave, valor in metricas_norm.items()
        )
        
        return score
    
    def gerar_diagnostico(self, metricas: MetricasSistema) -> Diagnostico:
        """Gera diagnóstico baseado nas métricas"""
        score = self.processar_metricas(metricas)
        
        # Determina se há anomalia
        anomalia = score > 0.7
        
        # Identifica o tipo de anomalia
        tipo_anomalia = self._identificar_tipo_anomalia(metricas)
        
        # Calcula nível de gravidade
        gravidade = min(1.0, score)
        
        # Gera recomendações
        recomendacoes = self._gerar_recomendacoes(metricas, tipo_anomalia)
        
        return Diagnostico(
            anomalia_detectada=anomalia,
            tipo_anomalia=tipo_anomalia,
            nivel_gravidade=gravidade,
            recomendacoes=recomendacoes
        )
    
    def _identificar_tipo_anomalia(self, metricas: MetricasSistema) -> str:
        """Identifica o tipo principal de anomalia"""
        if metricas.taxa_erro > 3:
            return "erro_sistema"
        elif metricas.latencia > 80:
            return "latencia_alta"
        elif metricas.throughput > 800:
            return "sobrecarga"
        elif any(v > 70 for v in metricas.uso_recursos.values()):
            return "recursos_insuficientes"
        return "normal"
    
    def _gerar_recomendacoes(self, metricas: MetricasSistema, tipo_anomalia: str) -> List[str]:
        """Gera recomendações baseadas no tipo de anomalia"""
        recomendacoes = []
        
        if tipo_anomalia == "erro_sistema":
            recomendacoes.extend([
                "Verificar logs de erro",
                "Avaliar integridade dos dados",
                "Considerar rollback da última atualização"
            ])
        elif tipo_anomalia == "latencia_alta":
            recomendacoes.extend([
                "Otimizar consultas ao banco de dados",
                "Avaliar necessidade de cache",
                "Considerar escalonamento horizontal"
            ])
        elif tipo_anomalia == "sobrecarga":
            recomendacoes.extend([
                "Implementar rate limiting",
                "Avaliar escalonamento automático",
                "Otimizar processamento em lote"
            ])
        elif tipo_anomalia == "recursos_insuficientes":
            recomendacoes.extend([
                "Avaliar alocação de recursos",
                "Considerar otimização de memória",
                "Verificar vazamentos de recursos"
            ])
        
        return recomendacoes

# Exemplo de uso
if __name__ == "__main__":
    from monitoramento import MonitoramentoMultidimensional
    
    monitor = MonitoramentoMultidimensional()
    diagnostico = RedeNeuralDiagnostico()
    
    # Simula coleta e diagnóstico
    metricas = monitor.coletar_metricas()
    resultado = diagnostico.gerar_diagnostico(metricas)
    
    print("\nResultado do Diagnóstico:")
    print(f"Anomalia detectada: {resultado.anomalia_detectada}")
    print(f"Tipo de anomalia: {resultado.tipo_anomalia}")
    print(f"Nível de gravidade: {resultado.nivel_gravidade:.2f}")
    print("\nRecomendações:")
    for rec in resultado.recomendacoes:
        print(f"- {rec}") 