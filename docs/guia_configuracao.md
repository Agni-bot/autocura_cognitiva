# Guia de Configuração

## Visão Geral

Este guia descreve as configurações disponíveis no Sistema de Autocura Cognitiva.

## Configurações do Sistema

### 1. Configurações Gerais

#### Estrutura
```json
{
    "system": {
        "name": "Autocura Cognitiva",
        "version": "1.0.0",
        "environment": "production",
        "timezone": "America/Sao_Paulo",
        "language": "pt_BR"
    }
}
```

#### Implementação
```python
from pydantic import BaseSettings

class SystemSettings(BaseSettings):
    name: str
    version: str
    environment: str
    timezone: str
    language: str
    
    class Config:
        env_prefix = "SYSTEM_"
```

### 2. Configurações de Banco de Dados

#### MongoDB
```python
class DatabaseSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str
    
    class Config:
        env_prefix = "DB_"
```

#### Redis
```python
class CacheSettings(BaseSettings):
    host: str
    port: int
    password: str
    db: int
    
    class Config:
        env_prefix = "REDIS_"
```

### 3. Configurações de API

#### FastAPI
```python
class APISettings(BaseSettings):
    title: str
    description: str
    version: str
    docs_url: str
    redoc_url: str
    
    class Config:
        env_prefix = "API_"
```

#### CORS
```python
class CORSSettings(BaseSettings):
    allow_origins: list[str]
    allow_methods: list[str]
    allow_headers: list[str]
    allow_credentials: bool
    
    class Config:
        env_prefix = "CORS_"
```

## Configurações de Usuário

### 1. Perfil

#### Estrutura
```json
{
    "profile": {
        "name": "João Silva",
        "email": "joao@exemplo.com",
        "role": "admin",
        "preferences": {
            "notifications": true,
            "theme": "dark",
            "language": "pt_BR"
        }
    }
}
```

#### Implementação
```python
class UserProfile(BaseModel):
    name: str
    email: str
    role: str
    preferences: dict
```

### 2. Preferências

#### Notificações
```python
class NotificationPreferences(BaseModel):
    email: bool
    push: bool
    sms: bool
    frequency: str
    channels: list[str]
```

#### Interface
```python
class InterfacePreferences(BaseModel):
    theme: str
    language: str
    timezone: str
    date_format: str
    time_format: str
```

## Configurações de Segurança

### 1. Autenticação

#### JWT
```python
class JWTSettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    
    class Config:
        env_prefix = "JWT_"
```

#### OAuth
```python
class OAuthSettings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    facebook_client_id: str
    facebook_client_secret: str
    
    class Config:
        env_prefix = "OAUTH_"
```

### 2. Criptografia

#### Chaves
```python
class EncryptionSettings(BaseSettings):
    key: str
    algorithm: str
    salt: str
    
    class Config:
        env_prefix = "ENCRYPTION_"
```

## Configurações de Monitoramento

### 1. Logs

#### Estrutura
```python
class LogSettings(BaseSettings):
    level: str
    format: str
    file: str
    max_size: int
    backup_count: int
    
    class Config:
        env_prefix = "LOG_"
```

### 2. Métricas

#### Prometheus
```python
class MetricsSettings(BaseSettings):
    enabled: bool
    port: int
    path: str
    
    class Config:
        env_prefix = "METRICS_"
```

## Configurações de Notificações

### 1. Email

#### SMTP
```python
class EmailSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    from_email: str
    tls: bool
    
    class Config:
        env_prefix = "EMAIL_"
```

### 2. Push

#### Firebase
```python
class PushSettings(BaseSettings):
    project_id: str
    private_key: str
    client_email: str
    
    class Config:
        env_prefix = "PUSH_"
```

## Configurações de Exportação

### 1. Formatos

#### Estrutura
```python
class ExportSettings(BaseSettings):
    formats: list[str]
    compression: bool
    encryption: bool
    max_size: int
    
    class Config:
        env_prefix = "EXPORT_"
```

### 2. Armazenamento

#### S3
```python
class StorageSettings(BaseSettings):
    bucket: str
    region: str
    access_key: str
    secret_key: str
    
    class Config:
        env_prefix = "STORAGE_"
```

## Configurações de Relatórios

### 1. Agendamento

#### Estrutura
```python
class ReportSettings(BaseSettings):
    schedule: str
    format: str
    recipients: list[str]
    retention_days: int
    
    class Config:
        env_prefix = "REPORT_"
```

### 2. Templates

#### Implementação
```python
class TemplateSettings(BaseSettings):
    path: str
    default: str
    custom: list[str]
    
    class Config:
        env_prefix = "TEMPLATE_"
```

## Configurações de Dashboard

### 1. Layout

#### Estrutura
```python
class DashboardSettings(BaseSettings):
    default_layout: dict
    widgets: list[str]
    refresh_interval: int
    
    class Config:
        env_prefix = "DASHBOARD_"
```

### 2. Widgets

#### Implementação
```python
class WidgetSettings(BaseSettings):
    enabled: list[str]
    position: dict
    size: dict
    
    class Config:
        env_prefix = "WIDGET_"
```

## Gerenciamento de Configurações

### 1. Carregamento

#### Implementação
```python
def load_settings():
    """
    Carrega todas as configurações do sistema.
    
    Returns:
        dict: Configurações carregadas
    """
    settings = {}
    
    # Carrega configurações do ambiente
    settings['system'] = SystemSettings()
    settings['database'] = DatabaseSettings()
    settings['api'] = APISettings()
    settings['cors'] = CORSSettings()
    settings['jwt'] = JWTSettings()
    settings['oauth'] = OAuthSettings()
    settings['encryption'] = EncryptionSettings()
    settings['log'] = LogSettings()
    settings['metrics'] = MetricsSettings()
    settings['email'] = EmailSettings()
    settings['push'] = PushSettings()
    settings['export'] = ExportSettings()
    settings['storage'] = StorageSettings()
    settings['report'] = ReportSettings()
    settings['template'] = TemplateSettings()
    settings['dashboard'] = DashboardSettings()
    settings['widget'] = WidgetSettings()
    
    return settings
```

### 2. Atualização

#### Implementação
```python
async def update_settings(settings: dict):
    """
    Atualiza as configurações do sistema.
    
    Args:
        settings: Novas configurações
        
    Returns:
        dict: Configurações atualizadas
    """
    # Valida configurações
    validate_settings(settings)
    
    # Atualiza no banco
    await db.settings.update_one(
        {'_id': 'system'},
        {'$set': settings},
        upsert=True
    )
    
    # Atualiza cache
    await cache.set('settings', settings)
    
    return settings
```

### 3. Validação

#### Implementação
```python
def validate_settings(settings: dict):
    """
    Valida as configurações do sistema.
    
    Args:
        settings: Configurações a validar
        
    Raises:
        ValidationError: Se as configurações forem inválidas
    """
    # Valida estrutura
    if not isinstance(settings, dict):
        raise ValidationError("Configurações devem ser um dicionário")
    
    # Valida campos obrigatórios
    required_fields = [
        'system',
        'database',
        'api',
        'jwt'
    ]
    
    for field in required_fields:
        if field not in settings:
            raise ValidationError(f"Campo obrigatório ausente: {field}")
    
    # Valida valores
    for key, value in settings.items():
        if not isinstance(value, dict):
            raise ValidationError(f"Valor inválido para {key}")
        
        # Valida campos específicos
        if key == 'system':
            validate_system_settings(value)
        elif key == 'database':
            validate_database_settings(value)
        elif key == 'api':
            validate_api_settings(value)
        elif key == 'jwt':
            validate_jwt_settings(value)
```

## Configurações Globais

### Variáveis de Ambiente
O sistema utiliza as seguintes variáveis de ambiente:

```bash
# Configurações do Sistema
NAMESPACE=autocura-cognitiva
REGISTRY=localhost:5000
TAG=latest
MAX_RETRIES=3
TIMEOUT_SECONDS=300

# Configurações do Kubernetes
KUBECONFIG=~/.kube/config
KIND_CLUSTER_NAME=autocura-cognitiva

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DIR=logs
```

### Configurações do Registry
O registry local é configurado com:
- Porta: 5000
- Nome do container: `registry`
- Restart policy: `always`
- Versão: `registry:2`

## Configurações do Kubernetes

### Namespace
O namespace `autocura-cognitiva` é configurado com:
- RBAC granular
- Network policies
- Resource quotas
- Pod security policies

### RBAC
As configurações de RBAC incluem:
- ServiceAccount dedicado
- ClusterRole com permissões necessárias
- ClusterRoleBinding para o ServiceAccount
- Políticas de acesso granular

### Network Policies
As políticas de rede incluem:
- Isolamento de pods
- Controle de tráfego
- Regras de entrada/saída
- Proteção de serviços

## Configurações dos Operadores

### Healing Operator
```yaml
apiVersion: autocura-cognitiva.io/v1
kind: Healing
metadata:
  name: healing-config
spec:
  monitorInterval: 30s
  maxRetries: 3
  backoffSeconds: 5
  actions:
    - name: restart-pod
      threshold: 80
      cooldown: 300s
    - name: scale-up
      threshold: 90
      cooldown: 600s
```

### Rollback Operator
```yaml
apiVersion: autocura-cognitiva.io/v1
kind: Rollback
metadata:
  name: rollback-config
spec:
  monitorInterval: 60s
  maxHistory: 5
  probabilityThreshold: 0.8
  metrics:
    - name: error-rate
      weight: 0.4
    - name: latency
      weight: 0.3
    - name: resource-usage
      weight: 0.3
```

## Configurações de Monitoramento

### Prometheus
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: autocura-monitor
spec:
  selector:
    matchLabels:
      app: autocura-cognitiva
  endpoints:
    - port: metrics
      interval: 15s
```

### Grafana
```yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: autocura-dashboard
spec:
  json: |
    {
      "title": "Autocura Cognitiva",
      "panels": [
        {
          "title": "Métricas Principais",
          "type": "graph",
          "datasource": "Prometheus"
        }
      ]
    }
```

## Configurações de Armazenamento

### Persistent Volumes
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: autocura-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/autocura
```

### StatefulSets
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: autocura-sts
spec:
  serviceName: autocura
  replicas: 3
  template:
    spec:
      containers:
        - name: autocura
          image: localhost:5000/autocura-cognitiva:latest
```

## Configurações de Segurança

### Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: autocura-secrets
type: Opaque
data:
  api-key: <base64-encoded>
  db-password: <base64-encoded>
```

### ConfigMaps
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: autocura-config
data:
  log-level: INFO
  api-endpoint: https://api.autocura
  monitoring-interval: "30"
```

## Configurações de Logging

### Fluentd
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_key time
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
```

### Elasticsearch
```yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: autocura-es
spec:
  version: 7.10.0
  nodeSets:
    - name: default
      count: 3
      config:
        node.master: true
        node.data: true
        node.ingest: true
```

## Configurações de Backup

### CronJob para Backup
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: autocura-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: localhost:5000/backup-tool:latest
              command: ["/bin/sh", "-c", "backup.sh"]
```

## Configurações de Atualização

### Deployment Strategy
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autocura-deployment
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## Configurações de Diagnóstico

### Health Checks
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: autocura-pod
spec:
  containers:
    - name: autocura
      livenessProbe:
        httpGet:
          path: /health
          port: 8080
        initialDelaySeconds: 30
        periodSeconds: 10
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
```

## Configurações de Escalabilidade

### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: autocura-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: autocura-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
``` 