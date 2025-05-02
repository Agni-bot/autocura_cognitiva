# Fase 2: Bulkhead e Isolamento

## Visão Geral
Esta fase implementa o padrão Bulkhead e isolamento de recursos para garantir que falhas em um serviço não afetem outros serviços do sistema.

## Estrutura de Diretórios
```
kubernetes/
└── istio/
    ├── bulkhead.yaml           # Configuração do Bulkhead
    ├── resource-isolation.yaml # Isolamento de recursos
    └── namespaces.yaml         # Namespaces dedicados
```

## Configurações Implementadas

### 1. Bulkhead (`bulkhead.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: autocura-cognitiva-bulkhead
  namespace: autocura-cognitiva
spec:
  host: "*.autocura-cognitiva.svc.cluster.local"
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1024
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 10
    portLevelSettings:
    - port:
        number: 8080
      connectionPool:
        tcp:
          maxConnections: 50
        http:
          http1MaxPendingRequests: 512
      outlierDetection:
        consecutive5xxErrors: 3
        interval: 15s
        baseEjectionTime: 15s
        maxEjectionPercent: 5
```

**Parâmetros Configurados:**
- Pool de conexões global:
  - `maxConnections`: 100 conexões TCP
  - `http1MaxPendingRequests`: 1024 requisições HTTP
  - `maxRequestsPerConnection`: 10 requisições por conexão
- Pool de conexões por porta (8080):
  - `maxConnections`: 50 conexões TCP
  - `http1MaxPendingRequests`: 512 requisições HTTP
- Detecção de outliers global:
  - `consecutive5xxErrors`: 5 erros
  - `interval`: 30 segundos
  - `baseEjectionTime`: 30 segundos
  - `maxEjectionPercent`: 10%
- Detecção de outliers por porta:
  - `consecutive5xxErrors`: 3 erros
  - `interval`: 15 segundos
  - `baseEjectionTime`: 15 segundos
  - `maxEjectionPercent`: 5%

### 2. Isolamento de Recursos (`resource-isolation.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: autocura-cognitiva-isolation
  namespace: autocura-cognitiva
spec:
  hosts:
  - monitoramento.autocura-cognitiva.svc.cluster.local
  - diagnostico.autocura-cognitiva.svc.cluster.local
  - gerador-acoes.autocura-cognitiva.svc.cluster.local
  - observabilidade.autocura-cognitiva.svc.cluster.local
  ports:
  - number: 8080
    name: http-monitoramento
    protocol: HTTP
    targetPort: 8080
  - number: 8081
    name: http-diagnostico
    protocol: HTTP
    targetPort: 8081
  - number: 8082
    name: http-gerador-acoes
    protocol: HTTP
    targetPort: 8082
  - number: 5000
    name: http-observabilidade
    protocol: HTTP
    targetPort: 5000
  resolution: STATIC
  location: MESH_INTERNAL
  workloadSelector:
    labels:
      app: autocura-cognitiva
```

**Configurações:**
- Isolamento por serviço:
  - Monitoramento: porta 8080
  - Diagnóstico: porta 8081
  - Gerador de Ações: porta 8082
  - Observabilidade: porta 5000
- Resolução estática de serviços
- Localização interna do mesh
- Seletor de workload para aplicação

### 3. Namespaces Dedicados (`namespaces.yaml`)
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoramento
  labels:
    istio-injection: enabled
    isolation: strict
---
apiVersion: v1
kind: Namespace
metadata:
  name: diagnostico
  labels:
    istio-injection: enabled
    isolation: strict
---
apiVersion: v1
kind: Namespace
metadata:
  name: gerador-acoes
  labels:
    istio-injection: enabled
    isolation: strict
---
apiVersion: v1
kind: Namespace
metadata:
  name: observabilidade
  labels:
    istio-injection: enabled
    isolation: strict
```

**Configurações:**
- Namespaces dedicados para cada serviço
- Injeção do Istio habilitada
- Isolamento estrito configurado
- Labels para controle de acesso

## Comandos de Implantação

1. Aplicar configurações do Bulkhead:
```bash
kubectl apply -f kubernetes/istio/bulkhead.yaml
```

2. Aplicar isolamento de recursos:
```bash
kubectl apply -f kubernetes/istio/resource-isolation.yaml
```

3. Criar namespaces dedicados:
```bash
kubectl apply -f kubernetes/istio/namespaces.yaml
```

## Benefícios da Implementação

1. **Isolamento de Falhas**:
   - Problemas em um serviço não afetam outros
   - Limites de recursos por serviço
   - Controle de tráfego granular

2. **Resiliência**:
   - Circuit breakers por serviço
   - Detecção de outliers específica
   - Recuperação automática

3. **Segurança**:
   - Isolamento de rede
   - Controle de acesso por namespace
   - Comunicação segura entre serviços

4. **Monitoramento**:
   - Métricas por serviço
   - Logs isolados
   - Rastreamento de tráfego

## Próximos Passos
1. Monitorar métricas de isolamento
2. Implementar testes de resiliência
3. Documentar procedimentos de troubleshooting
4. Preparar para a Fase 3 (CQRS e Otimização de Dados) 