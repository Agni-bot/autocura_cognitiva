import time
import logging
from monitoramento import MonitoramentoMultidimensional
from diagnostico import RedeNeuralDiagnostico
from gerador_acoes import GeradorAcoes

class SistemaAutocuraCognitiva:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitor = MonitoramentoMultidimensional()
        self.diagnostico = RedeNeuralDiagnostico()
        self.gerador = GeradorAcoes()
        
    def executar_ciclo(self):
        """Executa um ciclo completo de monitoramento, diagnóstico e geração de ações"""
        try:
            # 1. Monitoramento
            self.logger.info("Iniciando coleta de métricas...")
            metricas = self.monitor.coletar_metricas()
            
            # 2. Diagnóstico
            self.logger.info("Realizando diagnóstico...")
            resultado_diagnostico = self.diagnostico.gerar_diagnostico(metricas)
            
            # 3. Geração de Ações
            self.logger.info("Gerando ações...")
            acoes = self.gerador.gerar_acoes(resultado_diagnostico, metricas)
            acoes_priorizadas = self.gerador.priorizar_acoes(acoes)
            
            # 4. Exibição de Resultados
            self._exibir_resultados(metricas, resultado_diagnostico, acoes_priorizadas)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante o ciclo de autocura: {str(e)}")
            return False
    
    def _exibir_resultados(self, metricas, diagnostico, acoes):
        """Exibe os resultados do ciclo de forma organizada"""
        print("\n" + "="*50)
        print("RESULTADOS DO CICLO DE AUTOCURA COGNITIVA")
        print("="*50)
        
        print("\nMÉTRICAS COLETADAS:")
        print(f"Throughput: {metricas.throughput:.2f} ops/s")
        print(f"Taxa de Erro: {metricas.taxa_erro:.2f}%")
        print(f"Latência: {metricas.latencia:.2f} ms")
        print("Uso de Recursos:")
        for recurso, valor in metricas.uso_recursos.items():
            print(f"  - {recurso}: {valor:.2f}%")
        
        print("\nDIAGNÓSTICO:")
        print(f"Anomalia Detectada: {diagnostico.anomalia_detectada}")
        print(f"Tipo de Anomalia: {diagnostico.tipo_anomalia}")
        print(f"Nível de Gravidade: {diagnostico.nivel_gravidade:.2f}")
        print("\nRecomendações do Diagnóstico:")
        for rec in diagnostico.recomendacoes:
            print(f"  - {rec}")
        
        print("\nAÇÕES PRIORIZADAS:")
        for acao in acoes:
            print(f"\nTipo: {acao.tipo.upper()}")
            print(f"Descrição: {acao.descricao}")
            print(f"Prioridade: {acao.prioridade}")
            print(f"Tempo Estimado: {acao.tempo_estimado}")
            print(f"Recursos Necessários: {', '.join(acao.recursos_necessarios)}")
        
        print("\n" + "="*50)

def main():
    # Configuração do logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicialização do sistema
    sistema = SistemaAutocuraCognitiva()
    
    # Simulação de ciclos contínuos
    while True:
        try:
            sistema.executar_ciclo()
            time.sleep(5)  # Intervalo entre ciclos
        except KeyboardInterrupt:
            print("\nSistema encerrado pelo usuário")
            break
        except Exception as e:
            logging.error(f"Erro fatal: {str(e)}")
            break

if __name__ == "__main__":
    main() 