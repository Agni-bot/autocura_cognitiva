# Guia de Monitoramento do Sistema de Autocura Cognitiva

## Configurações de Monitoramento

### 1. Prometheus
```yaml
# prometheus.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 2
  resources:
    requests:
      memory: 400Mi
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
  serviceAccountName: prometheus
  serviceMonitorSelector: {}
```

### 2. Grafana
```yaml
# grafana.yaml
apiVersion: monitoring.coreos.com/v1
kind: Grafana
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 2
  resources:
    requests:
      memory: 200Mi
  securityContext:
    runAsNonRoot: true
    runAsUser: 472
  serviceAccountName: grafana
```

### 3. Alertmanager
```yaml
# alertmanager.yaml
apiVersion: monitoring.coreos.com/v1
kind: Alertmanager
metadata:
  name: alertmanager
  namespace: monitoring
spec:
  replicas: 2
  resources:
    requests:
      memory: 200Mi
  securityContext:
    runAsNonRoot: true
    runAsUser: 65534
  serviceAccountName: alertmanager
```

## Métricas

### 1. Métricas do Sistema
```powershell
# Verificar métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=system_metrics'

# Exportar métricas
curl -G 'http://localhost:9090/api/v1/query_range' --data-urlencode 'query=system_metrics' --data-urlencode 'start=1h' --data-urlencode 'end=now' --data-urlencode 'step=1m' > metrics.json
```

### 2. Métricas da Aplicação
```powershell
# Verificar métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=application_metrics'

# Exportar métricas
curl -G 'http://localhost:9090/api/v1/query_range' --data-urlencode 'query=application_metrics' --data-urlencode 'start=1h' --data-urlencode 'end=now' --data-urlencode 'step=1m' > metrics.json
```

### 3. Métricas de Negócio
```powershell
# Verificar métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=business_metrics'

# Exportar métricas
curl -G 'http://localhost:9090/api/v1/query_range' --data-urlencode 'query=business_metrics' --data-urlencode 'start=1h' --data-urlencode 'end=now' --data-urlencode 'step=1m' > metrics.json
```

## Logs

### 1. Fluentd
```yaml
# fluentd.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
        - name: fluentd
          image: fluent/fluentd:latest
          resources:
            requests:
              memory: 200Mi
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
```

### 2. Elasticsearch
```yaml
# elasticsearch.yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: logging
spec:
  version: 7.17.0
  nodeSets:
    - name: default
      count: 3
      config:
        node.master: true
        node.data: true
        node.ingest: true
      resources:
        requests:
          memory: 4Gi
```

### 3. Kibana
```yaml
# kibana.yaml
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: kibana
  namespace: logging
spec:
  version: 7.17.0
  count: 1
  elasticsearchRef:
    name: elasticsearch
  resources:
    requests:
      memory: 1Gi
```

## Alertas

### 1. Configuração de Alertas
```yaml
# alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: alert-rules
  namespace: monitoring
spec:
  groups:
    - name: system
      rules:
        - alert: HighCPUUsage
          expr: node_cpu_seconds_total{mode="idle"} < 0.1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: High CPU usage
```

### 2. Notificações
```yaml
# alertmanager-config.yaml
apiVersion: monitoring.coreos.com/v1
kind: AlertmanagerConfig
metadata:
  name: alertmanager-config
  namespace: monitoring
spec:
  receivers:
    - name: email
      emailConfigs:
        - to: admin@example.com
          from: alertmanager@example.com
          smarthost: smtp.example.com:587
          authUsername: alertmanager
          authPassword:
            name: alertmanager-smtp
            key: password
```

### 3. Silenciamento
```powershell
# Criar silenciamento
kubectl port-forward svc/alertmanager 9093:9093
curl -X POST http://localhost:9093/api/v1/silences -d '{"matchers":[{"name":"alertname","value":"HighCPUUsage"}],"startsAt":"2024-01-01T00:00:00Z","endsAt":"2024-01-02T00:00:00Z"}'

# Listar silenciamentos
curl http://localhost:9093/api/v1/silences
```

## Dashboards

### 1. Grafana
```yaml
# system-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: system-dashboard
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "System Dashboard",
        "panels": [
          {
            "title": "CPU Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "node_cpu_seconds_total"
              }
            ]
          }
        ]
      }
    }
```

### 2. Data Sources
```yaml
# prometheus-datasource.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDataSource
metadata:
  name: prometheus-datasource
  namespace: monitoring
spec:
  name: Prometheus
  type: prometheus
  url: http://prometheus:9090
  access: proxy
  isDefault: true
```

### 3. Visualização
```powershell
# Acessar Grafana
kubectl port-forward svc/grafana 3000:3000

# Acessar Kibana
kubectl port-forward svc/kibana 5601:5601

# Acessar Prometheus
kubectl port-forward svc/prometheus 9090:9090
```

## Exportação de Dados

### 1. Exportação de Métricas
```powershell
# Exportar métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query_range' --data-urlencode 'query=system_metrics' --data-urlencode 'start=1h' --data-urlencode 'end=now' --data-urlencode 'step=1m' > metrics.json

# Exportar logs
kubectl logs -n $env:NAMESPACE -l app=healing-operator > logs.txt
```

### 2. Exportação de Logs
```powershell
# Exportar logs
kubectl logs -n $env:NAMESPACE -l app=rollback-operator > logs.txt

# Exportar eventos
kubectl get events --sort-by='.lastTimestamp' > events.txt
```

### 3. Exportação de Dashboards
```powershell
# Exportar dashboards
kubectl get configmaps -n monitoring -l app=grafana-dashboard -o yaml > dashboards.yaml

# Exportar configurações
kubectl get configmaps -n monitoring -l app=grafana-datasource -o yaml > datasources.yaml
```

## Análise de Tendências

### 1. Métricas de Negócio

#### Growth
- Usuários ativos
- Receita
- Conversões
- Churn

#### Performance
- Tempo de carregamento
- Disponibilidade
- Satisfação
- NPS

### 2. Anomalias

#### Detecção
- Desvio padrão
- Machine learning
- Regras personalizadas
- Correlações

#### Ação
- Alertas automáticos
- Investigação manual
- Ajuste de thresholds
- Documentação

## Relatórios

### 1. Diário

#### Conteúdo
- Status geral
- Incidentes
- Métricas chave
- Tendências

#### Formato
- Dashboard
- Email
- PDF
- Slides

### 2. Semanal

#### Conteúdo
- Análise de tendências
- KPIs
- Melhorias
- Planejamento

#### Formato
- Reunião
- Documento
- Apresentação
- Gráficos

## Manutenção

### 1. Limpeza

#### Logs
- Rotação diária
- Compressão
- Retenção
- Backup

#### Métricas
- Agregação
- Downsampling
- Retenção
- Exportação

### 2. Atualização

#### Ferramentas
- Versões
- Plugins
- Configurações
- Integrações

#### Dashboards
- Layout
- Queries
- Alertas
- Documentação

## Troubleshooting

### 1. Problemas Comuns

#### Alta CPU
1. Verificar processos
2. Analisar threads
3. Checar queries
4. Otimizar código

#### Erros de Aplicação
1. Verificar logs
2. Analisar stack traces
3. Testar endpoints
4. Corrigir bugs

### 2. Procedimentos

#### Incidentes
1. Identificar problema
2. Isolar causa
3. Implementar solução
4. Documentar

#### Melhorias
1. Analisar métricas
2. Identificar gargalos
3. Propor soluções
4. Implementar

## Documentação

### 1. Dashboards

#### Estrutura
- Visão geral
- Detalhes
- Drill-down
- Exportação

#### Manutenção
- Atualizações
- Validação
- Backup
- Versionamento

### 2. Alertas

#### Documentação
- Descrição
- Severidade
- Ação
- Contato

#### Manutenção
- Revisão
- Ajuste
- Teste
- Validação 