# Protocolo de Emergência Contra Degeneração Cognitiva

## Visão Geral

Este documento define o protocolo de emergência para detecção, contenção e recuperação de estados de degeneração cognitiva no Sistema de Autocura Cognitiva. O protocolo estabelece mecanismos de segurança independentes que operam fora do ciclo principal de autocura, garantindo a integridade do sistema mesmo quando seus componentes primários apresentam comportamentos anômalos.

## Definição de Degeneração Cognitiva

A degeneração cognitiva é caracterizada pela deterioração progressiva das capacidades de diagnóstico, análise causal e tomada de decisão do sistema, manifestando-se através de padrões específicos de comportamento disfuncional.

### Sintomas Primários

1. **Oscilação Terapêutica**: Alternância rápida entre estratégias de correção sem convergência para soluções estáveis.
   - *Indicadores*: Frequência de mudanças de estratégia > 3 por minuto, duração média de estratégia < 30 segundos.

2. **Paralisia Analítica**: Coleta excessiva de dados sem ações corretivas correspondentes.
   - *Indicadores*: Razão dados/ações > 100:1, tempo médio para decisão > 5x linha de base.

3. **Miopia Causal**: Foco em correlações superficiais com negligência de causas raiz.
   - *Indicadores*: Profundidade média de árvore causal < 2, taxa de recorrência de problemas > 70%.

4. **Amnésia Contextual**: Incapacidade de relacionar eventos atuais com experiências passadas relevantes.
   - *Indicadores*: Taxa de reutilização de conhecimento < 20%, similaridade contextual não reconhecida > 80%.

5. **Hiperatividade Corretiva**: Implementação de correções desnecessárias ou desproporcionais.
   - *Indicadores*: Volume de ações > 3x linha de base, impacto negativo de ações > 40%.

## Níveis de Alerta e Respostas

### Nível 1: Anomalia Cognitiva

**Critérios de Ativação**:
- Presença de 1-2 sintomas primários em intensidade leve a moderada
- Duração dos sintomas: 5-15 minutos
- Impacto operacional: Mínimo a moderado

**Respostas Automáticas**:
1. Ativação de diagnóstico secundário independente com arquitetura neural alternativa
2. Redução temporária do escopo de monitoramento para métricas essenciais (30% das dimensões)
3. Aumento da frequência de validação de ações (3x normal)
4. Registro detalhado de estados internos para análise posterior
5. Notificação de nível informativo para equipe de operações

**Objetivo**: Contenção precoce e auto-correção sem interrupção de serviço.

### Nível 2: Deterioração Cognitiva

**Critérios de Ativação**:
- Presença de 3-4 sintomas primários em intensidade moderada a severa
- Persistência de Nível 1 por > 30 minutos sem melhoria
- Impacto operacional: Moderado a significativo

**Respostas Automáticas**:
1. Ativação de modo de operação restrito (apenas ações de baixo risco)
2. Rollback para versão estável conhecida dos modelos neurais
3. Notificação de alerta para intervenção humana supervisionada
4. Inicialização de recalibração neural com dados de referência
5. Isolamento parcial do sistema (redução de 50% na capacidade de ação)
6. Ativação de logs de depuração em todos os componentes

**Objetivo**: Estabilização do sistema com intervenção humana limitada.

### Nível 3: Colapso Cognitivo

**Critérios de Ativação**:
- Presença de todos os 5 sintomas primários em intensidade severa
- Escalação de Nível 2 para Nível 3 em < 15 minutos
- Falha de respostas de Nível 2
- Impacto operacional: Severo a crítico

**Respostas Automáticas**:
1. Ativação de modo de segurança (failsafe) com desativação de todos os componentes autônomos
2. Transferência para controle humano direto com interface de emergência
3. Snapshot completo do estado do sistema para análise forense
4. Inicialização de procedimento de recuperação completa com reinicialização controlada
5. Notificação de emergência para equipe de resposta a incidentes
6. Ativação de sistema de contenção de danos para limitar impacto em sistemas dependentes

**Objetivo**: Prevenção de danos maiores e preservação de dados para recuperação.

## Mecanismo de Detecção

O sistema utiliza um componente independente chamado "Guardião Cognitivo" que opera fora do ciclo principal de autocura e monitora continuamente três dimensões de saúde cognitiva:

### 1. Coerência de Diagnósticos

Avalia a consistência interna e temporal dos diagnósticos produzidos pelo sistema.

```python
def calcular_coerencia_diagnosticos(self, janela_diagnosticos):
    """
    Calcula a coerência interna dos diagnósticos recentes.
    
    Retorna valor entre 0.0 (incoerente) e 1.0 (perfeitamente coerente).
    """
    if len(janela_diagnosticos) < 2:
        return 1.0  # Não há incoerência com apenas um diagnóstico
        
    # Extrai causas identificadas de cada diagnóstico
    causas_por_diagnostico = [
        set(d.causas_potenciais) for d in janela_diagnosticos
    ]
    
    # Calcula similaridade entre diagnósticos consecutivos
    similaridades = []
    for i in range(1, len(causas_por_diagnostico)):
        causas_anterior = causas_por_diagnostico[i-1]
        causas_atual = causas_por_diagnostico[i]
        
        # Índice de Jaccard para similaridade de conjuntos
        if not causas_anterior or not causas_atual:
            similaridade = 0.0 if (causas_anterior or causas_atual) else 1.0
        else:
            intersecao = len(causas_anterior.intersection(causas_atual))
            uniao = len(causas_anterior.union(causas_atual))
            similaridade = intersecao / uniao
            
        similaridades.append(similaridade)
    
    # Calcula variância das similaridades (alta variância = baixa coerência)
    if not similaridades:
        return 1.0
        
    media_similaridade = sum(similaridades) / len(similaridades)
    variancia = sum((s - media_similaridade) ** 2 for s in similaridades) / len(similaridades)
    
    # Converte variância para medida de coerência (0.0-1.0)
    coerencia = max(0.0, 1.0 - min(1.0, variancia * 5.0))
    
    return coerencia
```

### 2. Eficácia de Ações

Avalia o impacto das ações corretivas nas métricas-alvo do sistema.

```python
def calcular_eficacia_acoes(self, acoes_recentes, metricas_antes, metricas_depois):
    """
    Avalia a eficácia das ações corretivas recentes.
    
    Retorna valor entre -1.0 (prejudicial) e 1.0 (totalmente eficaz).
    """
    if not acoes_recentes:
        return 0.0  # Sem ações, eficácia neutra
        
    # Mapeia ações para métricas-alvo que deveriam melhorar
    metricas_alvo = set()
    for acao in acoes_recentes:
        metricas_alvo.update(acao.metricas_alvo)
    
    # Calcula mudança relativa em cada métrica-alvo
    mudancas_relativas = []
    for metrica in metricas_alvo:
        if metrica not in metricas_antes or metrica not in metricas_depois:
            continue
            
        valor_antes = metricas_antes[metrica]
        valor_depois = metricas_depois[metrica]
        
        # Evita divisão por zero
        if abs(valor_antes) < 1e-10:
            continue
            
        # Calcula mudança relativa, considerando se menor é melhor
        if metrica.menor_eh_melhor:
            mudanca = (valor_antes - valor_depois) / abs(valor_antes)
        else:
            mudanca = (valor_depois - valor_antes) / abs(valor_antes)
            
        mudancas_relativas.append(mudanca)
    
    # Sem métricas comparáveis, assume eficácia neutra
    if not mudancas_relativas:
        return 0.0
        
    # Média das mudanças relativas, limitada entre -1.0 e 1.0
    eficacia = sum(mudancas_relativas) / len(mudancas_relativas)
    eficacia = max(-1.0, min(1.0, eficacia))
    
    return eficacia
```

### 3. Estabilidade de Decisões

Avalia a consistência temporal das decisões do sistema e a presença de padrões oscilatórios.

```python
def calcular_estabilidade_decisoes(self, historico_acoes, janela_tempo=3600):
    """
    Avalia a estabilidade das decisões do sistema ao longo do tempo.
    
    Retorna valor entre 0.0 (instável) e 1.0 (estável).
    """
    # Filtra ações dentro da janela de tempo
    timestamp_atual = time.time()
    acoes_recentes = [
        a for a in historico_acoes 
        if timestamp_atual - a.timestamp <= janela_tempo
    ]
    
    if len(acoes_recentes) < 3:
        return 1.0  # Poucas ações para detectar instabilidade
    
    # Agrupa ações por tipo e alvo
    acoes_por_tipo_alvo = {}
    for acao in acoes_recentes:
        chave = (acao.tipo, acao.alvo_id)
        if chave not in acoes_por_tipo_alvo:
            acoes_por_tipo_alvo[chave] = []
        acoes_por_tipo_alvo[chave].append(acao)
    
    # Calcula oscilações para cada tipo/alvo
    oscilacoes_totais = 0
    for acoes in acoes_por_tipo_alvo.values():
        if len(acoes) < 3:
            continue
            
        # Ordena por timestamp
        acoes.sort(key=lambda a: a.timestamp)
        
        # Conta reversões de direção
        reversoes = 0
        for i in range(2, len(acoes)):
            # Compara direção da mudança entre ações consecutivas
            direcao_anterior = self._calcular_direcao(acoes[i-2], acoes[i-1])
            direcao_atual = self._calcular_direcao(acoes[i-1], acoes[i])
            
            # Se direções opostas, conta como reversão
            if direcao_anterior * direcao_atual < 0:
                reversoes += 1
                
        # Normaliza contagem de reversões
        taxa_reversao = reversoes / (len(acoes) - 2)
        oscilacoes_totais += taxa_reversao
    
    # Calcula média de oscilações
    if not acoes_por_tipo_alvo:
        return 1.0
        
    oscilacao_media = oscilacoes_totais / len(acoes_por_tipo_alvo)
    
    # Converte para medida de estabilidade (0.0-1.0)
    estabilidade = max(0.0, 1.0 - min(1.0, oscilacao_media * 2.0))
    
    return estabilidade
    
def _calcular_direcao(self, acao1, acao2):
    """Calcula a direção da mudança entre duas ações consecutivas."""
    # Implementação específica dependendo do tipo de ação
    # Retorna valor positivo ou negativo indicando direção
    pass
```

## Determinação de Nível de Alerta

O nível de alerta é determinado através de um algoritmo que combina as três métricas de saúde cognitiva:

```python
def determinar_nivel_alerta(self, coerencia, eficacia, estabilidade):
    """
    Determina o nível de alerta com base nas métricas cognitivas.
    
    Retorna nível de 0 (normal) a 3 (emergência).
    """
    # Pesos para cada métrica
    peso_coerencia = 0.4
    peso_eficacia = 0.3
    peso_estabilidade = 0.3
    
    # Calcula score composto (0.0 a 1.0, onde menor é pior)
    score = (
        coerencia * peso_coerencia +
        max(0, eficacia) * peso_eficacia +
        estabilidade * peso_estabilidade
    )
    
    # Determina nível com base no score
    if score >= 0.8:
        return 0  # Normal
    elif score >= 0.6:
        return 1  # Anomalia
    elif score >= 0.3:
        return 2  # Deterioração
    else:
        return 3  # Colapso
```

## Implementação do Guardião Cognitivo

O Guardião Cognitivo é implementado como um componente independente que opera em um processo separado, com seu próprio ciclo de vida e recursos dedicados.

## Procedimentos de Recuperação

### Recuperação de Nível 1

1. Validação cruzada de diagnósticos entre sistema primário e secundário
2. Recalibração de limiares de detecção de anomalias
3. Reinicialização seletiva de componentes afetados
4. Retorno gradual ao escopo completo de monitoramento

### Recuperação de Nível 2

1. Análise forense de padrões de degradação
2. Retreinamento de modelos com dados de referência
3. Validação humana de planos de ação antes da implementação
4. Monitoramento intensivo por 24 horas após estabilização

### Recuperação de Nível 3

1. Reinicialização completa do sistema com configuração de fábrica
2. Restauração de modelos a partir de backups verificados
3. Reintrodução gradual de funcionalidades autônomas
4. Análise de causa raiz com equipe multidisciplinar
5. Implementação de medidas preventivas contra recorrência

## Considerações Finais

O Protocolo de Emergência Contra Degeneração Cognitiva é um componente crítico do Sistema de Autocura Cognitiva, atuando como última linha de defesa contra falhas catastróficas. Sua implementação independente garante que mesmo em cenários de falha severa dos componentes primários, o sistema mantenha capacidade mínima de operação ou, no pior caso, realize um desligamento controlado que preserve dados e estados para recuperação posterior.

A eficácia deste protocolo deve ser testada regularmente através de simulações de falha e exercícios de recuperação, garantindo que todos os mecanismos de segurança funcionem conforme esperado quando necessários.
