import time
import random
import logging
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class MetricasSistema:
    throughput: float  # Operações por segundo
    taxa_erro: float   # Porcentagem de erros
    latencia: float    # Milissegundos
    uso_recursos: Dict[str, float]  # CPU, Memória, etc.

class MonitoramentoMultidimensional:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historico: List[MetricasSistema] = []
        
    def coletar_metricas(self) -> MetricasSistema:
        """Coleta métricas multidimensionais do sistema"""
        try:
            # Simulação de coleta de métricas
            metricas = MetricasSistema(
                throughput=random.uniform(100, 1000),  # ops/s
                taxa_erro=random.uniform(0, 5),       # %
                latencia=random.uniform(10, 100),     # ms
                uso_recursos={
                    'cpu': random.uniform(20, 80),    # %
                    'memoria': random.uniform(30, 70), # %
                    'disco': random.uniform(10, 50)   # %
                }
            )
            
            self.historico.append(metricas)
            self.logger.info(f"Métricas coletadas: {metricas}")
            return metricas
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {str(e)}")
            raise

    def analisar_tendencia(self, janela: int = 5) -> Dict[str, float]:
        """Analisa tendências nas métricas coletadas"""
        if len(self.historico) < janela:
            return {}
            
        ultimas_metricas = self.historico[-janela:]
        
        tendencias = {
            'throughput': sum(m.throughput for m in ultimas_metricas) / janela,
            'taxa_erro': sum(m.taxa_erro for m in ultimas_metricas) / janela,
            'latencia': sum(m.latencia for m in ultimas_metricas) / janela
        }
        
        return tendencias

    def detectar_anomalias(self) -> Dict[str, bool]:
        """Detecta anomalias nas métricas atuais"""
        if not self.historico:
            return {}
            
        ultima_metrica = self.historico[-1]
        anomalias = {
            'throughput_alto': ultima_metrica.throughput > 800,
            'taxa_erro_alta': ultima_metrica.taxa_erro > 3,
            'latencia_alta': ultima_metrica.latencia > 80,
            'recursos_altos': any(v > 70 for v in ultima_metrica.uso_recursos.values())
        }
        
        return anomalias

# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = MonitoramentoMultidimensional()
    
    # Simulação de coleta contínua
    for _ in range(10):
        metricas = monitor.coletar_metricas()
        tendencias = monitor.analisar_tendencia()
        anomalias = monitor.detectar_anomalias()
        
        print(f"\nMétricas coletadas: {metricas}")
        print(f"Tendências: {tendencias}")
        print(f"Anomalias detectadas: {anomalias}")
        
        time.sleep(1)  # Simula intervalo entre coletas 