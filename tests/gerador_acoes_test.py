import unittest
import time
from src.gerador_acoes.gerador_acoes import (
    MetricaDimensional,
    PadraoAnomalia,
    Diagnostico,
    TipoAcao,
    AcaoCorretiva,
    PlanoAcao,
    GeradorHotfix,
    MotorRefatoracao,
    ProjetorRedesign,
    OrquestradorAcoes
)

class TestGeradorAcoes(unittest.TestCase):
    def setUp(self):
        # Configuração inicial para os testes
        self.metrica = MetricaDimensional(
            id="metrica_1",
            nome="cpu_usage",
            valor=0.85,
            timestamp=time.time(),
            dimensao="recursos",
            unidade="percent"
        )
        
        self.anomalia = PadraoAnomalia(
            id="anomalia_1",
            nome="Alto uso de CPU",
            dimensoes=["recursos"],
            descricao="Uso de CPU acima de 80%",
            severidade=0.8
        )
        
        self.diagnostico = Diagnostico(
            id="diagnostico_1",
            timestamp=time.time(),
            anomalias_detectadas=[(self.anomalia, 0.9)],
            metricas_analisadas=["metrica_1"]
        )
    
    def test_metrica_dimensional(self):
        """Testa a criação e validação de métricas dimensionais."""
        # Teste de criação válida
        metrica = MetricaDimensional(
            id="test_1",
            nome="test",
            valor=0.5,
            timestamp=time.time(),
            dimensao="test",
            unidade="test"
        )
        self.assertEqual(metrica.nome, "test")
        
        # Teste de valor inválido
        with self.assertRaises(ValueError):
            MetricaDimensional(
                id="test_2",
                nome="test",
                valor=-1,  # Valor inválido
                timestamp=time.time(),
                dimensao="test",
                unidade="test"
            )
    
    def test_padrao_anomalia(self):
        """Testa a criação e validação de padrões de anomalia."""
        # Teste de criação válida
        anomalia = PadraoAnomalia(
            id="test_1",
            nome="Test",
            dimensoes=["test"],
            descricao="Test",
            severidade=0.5
        )
        self.assertEqual(anomalia.nome, "Test")
        
        # Teste de severidade inválida
        with self.assertRaises(ValueError):
            PadraoAnomalia(
                id="test_2",
                nome="Test",
                dimensoes=["test"],
                descricao="Test",
                severidade=1.5  # Severidade inválida
            )
    
    def test_diagnostico(self):
        """Teste a criação e validação de diagnósticos."""
        # Teste de criação válida
        diagnostico = Diagnostico(
            id="test_1",
            timestamp=time.time(),
            anomalias_detectadas=[(self.anomalia, 0.5)],
            metricas_analisadas=["test"]
        )
        self.assertEqual(diagnostico.id, "test_1")
        
        # Teste de confiança inválida
        with self.assertRaises(ValueError):
            Diagnostico(
                id="test_2",
                timestamp=time.time(),
                anomalias_detectadas=[(self.anomalia, 1.5)],  # Confiança inválida
                metricas_analisadas=["test"]
            )
    
    def test_acao_corretiva(self):
        """Testa a criação e validação de ações corretivas."""
        # Teste de criação válida
        acao = AcaoCorretiva(
            id="test_1",
            tipo=TipoAcao.HOTFIX,
            descricao="Test",
            comandos=["test"],
            impacto_estimado={"test": 0.5},
            tempo_estimado=60,
            recursos_necessarios={}
        )
        self.assertEqual(acao.id, "test_1")
        
        # Teste de risco inválido
        with self.assertRaises(ValueError):
            AcaoCorretiva(
                id="test_2",
                tipo=TipoAcao.HOTFIX,
                descricao="Test",
                comandos=["test"],
                impacto_estimado={"test": 0.5},
                tempo_estimado=60,
                recursos_necessarios={},
                risco=1.5  # Risco inválido
            )
        
        # Teste de tempo estimado inválido
        with self.assertRaises(ValueError):
            AcaoCorretiva(
                id="test_3",
                tipo=TipoAcao.HOTFIX,
                descricao="Test",
                comandos=["test"],
                impacto_estimado={"test": 0.5},
                tempo_estimado=-60,  # Tempo inválido
                recursos_necessarios={}
            )
    
    def test_gerador_hotfix(self):
        """Testa o gerador de hotfixes."""
        gerador = GeradorHotfix()
        
        # Teste de registro de template
        template = {
            "descricao": "Test",
            "comandos": ["test"],
            "impacto_estimado": {"test": 0.5}
        }
        gerador.registrar_template("test_1", template)
        
        # Teste de template inválido
        with self.assertRaises(ValueError):
            gerador.registrar_template("test_2", {})  # Template inválido
        
        # Teste de registro de eficácia
        gerador.registrar_eficacia("test_1", 0.8)
        
        # Teste de eficácia inválida
        with self.assertRaises(ValueError):
            gerador.registrar_eficacia("test_2", 1.5)  # Eficácia inválida
    
    def test_motor_refatoracao(self):
        """Testa o motor de refatoração."""
        motor = MotorRefatoracao()
        
        # Teste de registro de padrão
        padrao = {
            "descricao": "Test",
            "comandos": ["test"],
            "impacto_estimado": {"test": 0.5}
        }
        motor.registrar_padrao("test_1", padrao)
        
        # Teste de padrão inválido
        with self.assertRaises(ValueError):
            motor.registrar_padrao("test_2", {})  # Padrão inválido
        
        # Teste de registro de aplicação
        motor.registrar_aplicacao("test_1", {"resultado": "sucesso"})
        
        # Teste de padrão não encontrado
        with self.assertRaises(ValueError):
            motor.registrar_aplicacao("test_3", {"resultado": "sucesso"})
    
    def test_projetor_redesign(self):
        """Testa o projetor de redesign."""
        projetor = ProjetorRedesign()
        
        # Teste de registro de modelo
        modelo = {
            "descricao": "Test",
            "comandos": ["test"],
            "impacto_estimado": {"test": 0.5}
        }
        projetor.registrar_modelo("test_1", modelo)
        
        # Teste de modelo inválido
        with self.assertRaises(ValueError):
            projetor.registrar_modelo("test_2", {})  # Modelo inválido
        
        # Teste de registro de projeto
        projetor.registrar_projeto("test_1", {"resultado": "sucesso"})
        
        # Teste de modelo não encontrado
        with self.assertRaises(ValueError):
            projetor.registrar_projeto("test_3", {"resultado": "sucesso"})
    
    def test_orquestrador_acoes(self):
        """Testa o orquestrador de ações."""
        orquestrador = OrquestradorAcoes()
        
        # Teste de geração de plano válido
        plano = orquestrador.gerar_plano_acao(self.diagnostico)
        self.assertIsInstance(plano, PlanoAcao)
        
        # Teste de diagnóstico inválido
        diagnostico_invalido = Diagnostico(
            id="test_1",
            timestamp=time.time(),
            anomalias_detectadas=[],  # Sem anomalias
            metricas_analisadas=["test"]
        )
        with self.assertRaises(ValueError):
            orquestrador.gerar_plano_acao(diagnostico_invalido)

if __name__ == '__main__':
    unittest.main() 