# Guia de Desenvolvimento do Sistema de Autocura Cognitiva

## Ambiente de Desenvolvimento

### 1. Pré-requisitos
```powershell
$env:GO_VERSION = "1.21"
$env:DOCKER_VERSION = "24.0"
$env:KIND_VERSION = "0.20"
$env:KUBECTL_VERSION = "1.28"
$env:HELM_VERSION = "3.12"
```

### 2. Configuração
```powershell
$env:GOPATH = "$env:USERPROFILE\go"
$env:GOBIN = "$env:GOPATH\bin"
$env:PATH = "$env:GOBIN;$env:PATH"
$env:REGISTRY = "localhost:5000"
$env:NAMESPACE = "autocura"
```

### 3. Estrutura do Projeto
```
autocura_cognitiva/
├── cmd/
│   ├── healing-operator/
│   └── rollback-operator/
├── pkg/
│   ├── api/
│   ├── controllers/
│   ├── models/
│   └── utils/
├── config/
│   ├── crds/
│   ├── rbac/
│   └── samples/
├── deploy/
│   ├── operators/
│   ├── monitoring/
│   └── logging/
├── test/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/
```

## Desenvolvimento de Componentes

### 1. Operadores
```powershell
# Construção
docker build -t $env:REGISTRY/healing-operator:latest -f cmd/healing-operator/Dockerfile .
docker build -t $env:REGISTRY/rollback-operator:latest -f cmd/rollback-operator/Dockerfile .

# Push
docker push $env:REGISTRY/healing-operator:latest
docker push $env:REGISTRY/rollback-operator:latest

# Implantação
kubectl apply -f deploy/operators/healing-operator.yaml
kubectl apply -f deploy/operators/rollback-operator.yaml
```

### 2. APIs
```powershell
# Construção
docker build -t $env:REGISTRY/rest-api:latest -f cmd/rest-api/Dockerfile .
docker build -t $env:REGISTRY/graphql-api:latest -f cmd/graphql-api/Dockerfile .
docker build -t $env:REGISTRY/websocket-api:latest -f cmd/websocket-api/Dockerfile .

# Push
docker push $env:REGISTRY/rest-api:latest
docker push $env:REGISTRY/graphql-api:latest
docker push $env:REGISTRY/websocket-api:latest

# Implantação
kubectl apply -f deploy/apis/rest-api.yaml
kubectl apply -f deploy/apis/graphql-api.yaml
kubectl apply -f deploy/apis/websocket-api.yaml
```

### 3. Monitoramento
```powershell
# Implantação
helm install prometheus prometheus-community/kube-prometheus-stack
helm install grafana grafana/grafana
helm install elasticsearch elastic/elasticsearch
helm install kibana elastic/kibana
helm install fluentd fluent/fluentd
```

## Testes

### 1. Testes Unitários
```powershell
go test ./pkg/... -v -coverprofile=coverage.out
go tool cover -html=coverage.out -o coverage.html
```

### 2. Testes de Integração
```powershell
go test ./test/integration/... -v -tags=integration
```

### 3. Testes de Performance
```powershell
kubectl apply -f test/performance/load-generator.yaml
kubectl apply -f test/performance/metrics-collector.yaml
```

## CI/CD

### 1. GitHub Actions
```yaml
name: CI/CD
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Build
        run: go build ./...
      - name: Test
        run: go test ./... -v
      - name: Lint
        run: golangci-lint run
```

### 2. ArgoCD
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: autocura
spec:
  project: default
  source:
    repoURL: https://github.com/autocura/autocura_cognitiva.git
    targetRevision: HEAD
    path: deploy
  destination:
    server: https://kubernetes.default.svc
    namespace: autocura
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### 3. Tekton
```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: autocura-pipeline
spec:
  tasks:
    - name: build
      taskRef:
        name: build-task
    - name: test
      taskRef:
        name: test-task
    - name: deploy
      taskRef:
        name: deploy-task
```

## Documentação

### 1. Documentação de Código
```powershell
godoc -http=:6060
```

### 2. Documentação de API
```powershell
swagger generate spec -o swagger.json
```

### 3. Documentação de Configuração
```powershell
kubectl explain --recursive=true
```

## Versionamento

### 1. Versionamento de Imagens
```powershell
docker tag $env:REGISTRY/healing-operator:latest $env:REGISTRY/healing-operator:v1.0.0
docker tag $env:REGISTRY/rollback-operator:latest $env:REGISTRY/rollback-operator:v1.0.0
```

### 2. Versionamento de APIs
```powershell
kubectl apply -f deploy/apis/rest-api-v1.yaml
kubectl apply -f deploy/apis/graphql-api-v1.yaml
kubectl apply -f deploy/apis/websocket-api-v1.yaml
```

### 3. Versionamento de Configurações
```powershell
kubectl apply -f config/crds/v1/
kubectl apply -f config/rbac/v1/
kubectl apply -f config/samples/v1/
```

## Segurança

### 1. Análise de Segurança
```powershell
trivy image $env:REGISTRY/healing-operator:latest
trivy image $env:REGISTRY/rollback-operator:latest
```

### 2. Gerenciamento de Secrets
```powershell
kubectl create secret generic api-key --from-literal=key=value
kubectl create secret tls tls-cert --cert=cert.pem --key=key.pem
```

### 3. Auditoria
```powershell
kubectl get events --sort-by='.lastTimestamp'
kubectl get auditlogs
```

## Monitoramento

### 1. Métricas
```powershell
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
```

### 2. Logs
```powershell
kubectl port-forward svc/kibana 5601:5601
```

### 3. Alertas
```powershell
kubectl port-forward svc/alertmanager 9093:9093
``` 