# Guia de Contribuição

## Introdução

Obrigado por seu interesse em contribuir para o Sistema de Autocura Cognitiva! Este guia irá ajudá-lo a entender como contribuir de forma eficaz.

## Como Contribuir

### 1. Reportando Problemas

Antes de criar um novo issue:
1. Verifique se o problema já foi reportado
2. Use o template de issue apropriado
3. Inclua informações detalhadas:
   - Versão do sistema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Logs relevantes

### 2. Sugerindo Melhorias

Para sugerir melhorias:
1. Descreva o problema ou oportunidade
2. Explique a solução proposta
3. Inclua exemplos de uso
4. Liste benefícios e impactos

### 3. Enviando Pull Requests

Para enviar um PR:
1. Crie um branch a partir de `main`
2. Faça commits atômicos
3. Escreva mensagens claras
4. Atualize a documentação
5. Adicione testes

## Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.8+
- Docker
- Git
- Editor de código (VS Code recomendado)

### Configuração

1. Fork o repositório
2. Clone seu fork:
   ```bash
   git clone https://github.com/seu-usuario/autocura-cognitiva.git
   cd autocura-cognitiva
   ```

3. Configure o ambiente:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

4. Configure pre-commit:
   ```bash
   pre-commit install
   ```

## Padrões de Código

### Python

- Siga PEP 8
- Use type hints
- Documente funções e classes
- Escreva docstrings

Exemplo:
```python
def process_metric(metric: Metric) -> ProcessedMetric:
    """
    Processa uma métrica do sistema.

    Args:
        metric: Objeto Metric a ser processado

    Returns:
        ProcessedMetric: Métrica processada

    Raises:
        ValueError: Se a métrica for inválida
    """
    if not metric.is_valid():
        raise ValueError("Métrica inválida")
    
    return ProcessedMetric(metric)
```

### JavaScript/TypeScript

- Use ESLint
- Siga Airbnb Style Guide
- Use TypeScript quando possível
- Documente componentes

Exemplo:
```typescript
interface MetricProps {
  value: number;
  unit: string;
}

const MetricDisplay: React.FC<MetricProps> = ({ value, unit }) => {
  return (
    <div className="metric">
      <span className="value">{value}</span>
      <span className="unit">{unit}</span>
    </div>
  );
};
```

## Testes

### Backend

1. Execute testes:
   ```bash
   pytest
   ```

2. Verifique cobertura:
   ```bash
   pytest --cov=src tests/
   ```

### Frontend

1. Execute testes:
   ```bash
   npm test
   ```

2. Verifique cobertura:
   ```bash
   npm run test:coverage
   ```

## Documentação

### Atualizando Documentação

1. Use Markdown
2. Siga o guia de estilo
3. Inclua exemplos
4. Atualize índices

### Adicionando Novos Arquivos

1. Crie em `docs/`
2. Atualize `README.md`
3. Adicione ao índice
4. Siga convenções de nome

## Processo de Revisão

### Revisando PRs

1. Verifique:
   - Código limpo
   - Testes adequados
   - Documentação atualizada
   - Conformidade com padrões

2. Comente:
   - Sugestões de melhoria
   - Perguntas
   - Aprovação/rejeição

### Respondendo a Comentários

1. Responda todos os comentários
2. Faça alterações necessárias
3. Atualize o PR
4. Notifique revisores

## Comunicação

### Canais

- Issues do GitHub
- Pull Requests
- Discussões
- Slack (canal #autocura)

### Boas Práticas

1. Seja respeitoso
2. Seja claro e conciso
3. Use emojis com moderação
4. Mantenha discussões relevantes

## Reconhecimento

### Tipos de Contribuição

- Código
- Documentação
- Testes
- Revisões
- Traduções
- Design

### Como é Reconhecido

- Menção em releases
- Badges no perfil
- Agradecimentos especiais
- Convites para eventos

## Dúvidas?

- Consulte a documentação
- Abra uma discussão
- Entre em contato com mantenedores
- Participe de reuniões da comunidade 