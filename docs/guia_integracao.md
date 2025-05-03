# Guia de Integração do Sistema de Autocura Cognitiva

## APIs

### 1. API REST
```yaml
# api-rest.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-rest
  namespace: autocura-cognitiva
spec:
  ports:
    - port: 8080
      targetPort: 8080
  selector:
    app: api-rest
```

### 2. API GraphQL
```yaml
# api-graphql.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-graphql
  namespace: autocura-cognitiva
spec:
  ports:
    - port: 8081
      targetPort: 8081
  selector:
    app: api-graphql
```

### 3. API WebSocket
```yaml
# api-websocket.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-websocket
  namespace: autocura-cognitiva
spec:
  ports:
    - port: 8082
      targetPort: 8082
  selector:
    app: api-websocket
```

## Integrações Externas

### 1. API Gemini
```yaml
# api-gemini.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-gemini
  namespace: autocura-cognitiva
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

### 2. Prometheus
```yaml
# prometheus-integration.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: autocura-service-monitor
  namespace: autocura-cognitiva
spec:
  selector:
    matchLabels:
      app: autocura-cognitiva
  endpoints:
    - port: metrics
      interval: 30s
```

### 3. Elasticsearch
```yaml
# elasticsearch-integration.yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: autocura-cognitiva
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

## Webhooks

### 1. Configuração de Webhooks
```yaml
# webhooks.yaml
apiVersion: v1
kind: Service
metadata:
  name: webhooks
  namespace: autocura-cognitiva
spec:
  ports:
    - port: 8083
      targetPort: 8083
  selector:
    app: webhooks
```

### 2. Webhook de Alertas
```yaml
# alert-webhook.yaml
apiVersion: monitoring.coreos.com/v1
kind: AlertmanagerConfig
metadata:
  name: alert-webhook
  namespace: autocura-cognitiva
spec:
  receivers:
    - name: 'webhook'
      webhook_configs:
        - url: 'http://webhooks:8083/alerts'
```

### 3. Webhook de Eventos
```yaml
# event-webhook.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: event-webhook
  namespace: autocura-cognitiva
data:
  webhook-url: 'http://webhooks:8083/events'
```

## Mensageria

### 1. Kafka
```yaml
# kafka.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka
  namespace: autocura-cognitiva
spec:
  kafka:
    version: 3.1.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      log.message.format.version: "3.1"
```

### 2. RabbitMQ
```yaml
# rabbitmq.yaml
apiVersion: rabbitmq.com/v1beta1
kind: RabbitmqCluster
metadata:
  name: rabbitmq
  namespace: autocura-cognitiva
spec:
  replicas: 3
  resources:
    requests:
      cpu: 500m
      memory: 500Mi
    limits:
      cpu: 1000m
      memory: 1Gi
```

### 3. Redis
```yaml
# redis.yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: Redis
metadata:
  name: redis
  namespace: autocura-cognitiva
spec:
  kubernetesConfig:
    image: redis:6.2.5
    imagePullPolicy: IfNotPresent
  redisExporter:
    enabled: true
    image: oliver006/redis_exporter:v1.45.0
  storage:
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

## Autenticação

### 1. OAuth2
```yaml
# oauth2.yaml
apiVersion: v1
kind: Secret
metadata:
  name: oauth2
  namespace: autocura-cognitiva
type: Opaque
data:
  client-id: <base64-encoded-client-id>
  client-secret: <base64-encoded-client-secret>
```

### 2. JWT
```yaml
# jwt.yaml
apiVersion: v1
kind: Secret
metadata:
  name: jwt
  namespace: autocura-cognitiva
type: Opaque
data:
  secret: <base64-encoded-secret>
```

### 3. API Keys
```yaml
# api-keys.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: autocura-cognitiva
type: Opaque
data:
  api-key-1: <base64-encoded-api-key-1>
  api-key-2: <base64-encoded-api-key-2>
```

## Testes de Integração

### 1. Testes de API
```powershell
# Executar testes de API
kubectl exec -it pod/api-test -n $env:NAMESPACE -- npm test

# Verificar logs dos testes
kubectl logs -l app=api-test -n $env:NAMESPACE
```

### 2. Testes de Webhook
```powershell
# Executar testes de webhook
kubectl exec -it pod/webhook-test -n $env:NAMESPACE -- npm test

# Verificar logs dos testes
kubectl logs -l app=webhook-test -n $env:NAMESPACE
```

### 3. Testes de Mensageria
```powershell
# Executar testes de mensageria
kubectl exec -it pod/messaging-test -n $env:NAMESPACE -- npm test

# Verificar logs dos testes
kubectl logs -l app=messaging-test -n $env:NAMESPACE
```

## Monitoramento de Integrações

### 1. Métricas de API
```powershell
# Verificar métricas de API
kubectl port-forward svc/prometheus -n $env:NAMESPACE 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=api_requests_total'
```

### 2. Métricas de Webhook
```powershell
# Verificar métricas de webhook
kubectl port-forward svc/prometheus -n $env:NAMESPACE 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=webhook_requests_total'
```

### 3. Métricas de Mensageria
```powershell
# Verificar métricas de mensageria
kubectl port-forward svc/prometheus -n $env:NAMESPACE 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=messaging_messages_total'
``` 