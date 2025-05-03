# Guia de Observabilidade

## Visão Geral

Este guia descreve as práticas e ferramentas de observabilidade do Sistema de Autocura Cognitiva.

## Pilares da Observabilidade

### 1. Métricas

#### Tipos de Métricas
- **Counter**: Valores que só aumentam
- **Gauge**: Valores que podem subir ou descer
- **Histogram**: Distribuição de valores
- **Summary**: Estatísticas de valores

#### Exemplos
```python
from prometheus_client import Counter, Gauge, Histogram

# Counter
requests_total = Counter('http_requests_total', 'Total HTTP requests')

# Gauge
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage in percent')

# Histogram
request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency'
)
```

### 2. Logs

#### Estrutura
```json
{
    "timestamp": "2024-05-02T12:00:00Z",
    "level": "INFO",
    "service": "autocura",
    "trace_id": "abc123",
    "span_id": "def456",
    "message": "Operação concluída",
    "metadata": {
        "operation": "process_data",
        "duration_ms": 150,
        "status": "success"
    }
}
```

#### Configuração
```python
import logging
import json_log_formatter

formatter = json_log_formatter.JSONFormatter()

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger('autocura')
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 3. Traces

#### Instrumentação
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

# Configurar tracer
provider = TracerProvider(
    resource=Resource.create({"service.name": "autocura"})
)
trace.set_tracer_provider(provider)

# Criar span
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("operacao") as span:
    span.set_attribute("parametro", valor)
    # código da operação
```

## Ferramentas

### 1. Prometheus

#### Configuração
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'autocura'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scheme: 'http'
```

#### Alertas
```yaml
groups:
  - name: autocura
    rules:
      - alert: HighCPUUsage
        expr: rate(cpu_usage_percent[5m]) > 80
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CPU usage is high"
          description: "CPU usage is above 80% for 5 minutes"
```

### 2. Grafana

#### Dashboards
```json
{
  "dashboard": {
    "title": "Visão Geral do Sistema",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(cpu_usage_percent[5m])",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

### 3. ELK Stack

#### Configuração Logstash
```conf
input {
  beats {
    port => 5044
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "autocura-%{+YYYY.MM.dd}"
  }
}
```

## Análise de Dados

### 1. Correlação

#### Exemplo
```python
def correlate_events(events: list) -> dict:
    """
    Correlaciona eventos do sistema.
    
    Args:
        events: Lista de eventos
        
    Returns:
        dict: Correlações encontradas
    """
    correlations = {}
    
    # Agrupar por trace_id
    by_trace = groupby(events, key=lambda x: x['trace_id'])
    
    for trace_id, trace_events in by_trace:
        # Analisar sequência de eventos
        sequence = analyze_sequence(trace_events)
        
        # Identificar padrões
        patterns = find_patterns(sequence)
        
        correlations[trace_id] = {
            'sequence': sequence,
            'patterns': patterns
        }
    
    return correlations
```

### 2. Anomalias

#### Detecção
```python
from sklearn.ensemble import IsolationForest

def detect_anomalies(metrics: list) -> list:
    """
    Detecta anomalias em métricas.
    
    Args:
        metrics: Lista de métricas
        
    Returns:
        list: Anomalias detectadas
    """
    # Preparar dados
    X = prepare_metrics(metrics)
    
    # Treinar modelo
    model = IsolationForest(contamination=0.1)
    model.fit(X)
    
    # Detectar anomalias
    predictions = model.predict(X)
    
    return [
        metric for metric, pred in zip(metrics, predictions)
        if pred == -1
    ]
```

## Visualização

### 1. Dashboards

#### Layout
```yaml
dashboard:
  title: "Visão Geral"
  layout:
    - row:
        - panel: "CPU Usage"
          width: 6
        - panel: "Memory Usage"
          width: 6
    - row:
        - panel: "Request Rate"
          width: 12
```

#### Painéis
```json
{
  "panel": {
    "title": "Request Rate",
    "type": "graph",
    "datasource": "Prometheus",
    "targets": [
      {
        "expr": "rate(http_requests_total[5m])",
        "legendFormat": "{{method}} {{status}}"
      }
    ],
    "options": {
      "legend": {
        "show": true,
        "values": true
      }
    }
  }
}
```

### 2. Alertas

#### Configuração
```yaml
alert:
  name: "High Error Rate"
  condition: "rate(http_errors_total[5m]) > 10"
  duration: "2m"
  severity: "high"
  channels:
    - email
    - slack
  annotations:
    summary: "High error rate detected"
    description: "Error rate is above 10 per second"
```

## Manutenção

### 1. Limpeza

#### Rotação de Logs
```bash
# Configurar logrotate
cat > /etc/logrotate.d/autocura << EOF
/var/log/autocura/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
EOF
```

#### Retenção de Métricas
```yaml
retention:
  raw: 15d
  hourly: 30d
  daily: 90d
  weekly: 1y
```

### 2. Backup

#### Configuração
```bash
# Script de backup
cat > backup_metrics.sh << EOF
#!/bin/bash
BACKUP_DIR="/backup/metrics/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup Prometheus
promtool tsdb backup /prometheus/data $BACKUP_DIR/prometheus

# Backup Elasticsearch
elasticsearch-dump \
  --input=http://localhost:9200/autocura-* \
  --output=$BACKUP_DIR/elasticsearch.json
EOF
```

## Troubleshooting

### 1. Problemas Comuns

#### Alta Latência
1. Verificar métricas de rede
2. Analisar traces
3. Identificar gargalos
4. Otimizar código

#### Erros Intermitentes
1. Coletar logs de erro
2. Analisar padrões
3. Reproduzir cenário
4. Implementar correção

### 2. Procedimentos

#### Investigação
1. Coletar dados relevantes
2. Analisar correlações
3. Identificar causa raiz
4. Documentar achados

#### Resolução
1. Implementar correção
2. Monitorar impacto
3. Validar solução
4. Atualizar documentação 