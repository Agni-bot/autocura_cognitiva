# Guia de Testes do Sistema de Autocura Cognitiva

## Testes Unitários

### 1. Configuração
```powershell
$env:TEST_ENV = "local"
$env:TEST_NAMESPACE = "autocura-test"
```

### 2. Execução
```powershell
go test ./pkg/... -v -coverprofile=coverage.out
go tool cover -html=coverage.out -o coverage.html
```

### 3. Verificação
```powershell
go vet ./pkg/...
golangci-lint run ./pkg/...
```

## Testes de Integração

### 1. Ambiente
```powershell
kind create cluster --config test/kind-config.yaml
kubectl create namespace $env:TEST_NAMESPACE
```

### 2. Implantação
```powershell
kubectl apply -f test/integration/operators.yaml
kubectl apply -f test/integration/monitoring.yaml
kubectl apply -f test/integration/logging.yaml
```

### 3. Execução
```powershell
go test ./test/integration/... -v -tags=integration
```

## Testes de Performance

### 1. Configuração
```powershell
$env:PERF_TEST_DURATION = "5m"
$env:PERF_TEST_RATE = "100"
```

### 2. Execução
```powershell
kubectl apply -f test/performance/load-generator.yaml
kubectl apply -f test/performance/metrics-collector.yaml
```

### 3. Análise
```powershell
kubectl port-forward svc/grafana 3000:3000
kubectl port-forward svc/prometheus 9090:9090
```

## Testes de Segurança

### 1. Análise de Vulnerabilidades
```powershell
trivy image $env:REGISTRY/healing-operator:latest
trivy image $env:REGISTRY/rollback-operator:latest
```

### 2. Testes de Penetração
```powershell
kubectl apply -f test/security/pen-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=pen-test
```

### 3. Verificação de Configurações
```powershell
kubectl apply -f test/security/config-audit.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=config-audit
```

## Testes de Resiliência

### 1. Testes de Falha
```powershell
kubectl apply -f test/resilience/failure-injection.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=failure-injection
```

### 2. Testes de Recuperação
```powershell
kubectl apply -f test/resilience/recovery-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=recovery-test
```

### 3. Testes de Disponibilidade
```powershell
kubectl apply -f test/resilience/availability-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=availability-test
```

## Testes de API

### 1. Testes REST
```powershell
kubectl apply -f test/api/rest-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=rest-test
```

### 2. Testes GraphQL
```powershell
kubectl apply -f test/api/graphql-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=graphql-test
```

### 3. Testes WebSocket
```powershell
kubectl apply -f test/api/websocket-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=websocket-test
```

## Testes de Monitoramento

### 1. Testes de Métricas
```powershell
kubectl apply -f test/monitoring/metrics-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=metrics-test
```

### 2. Testes de Logs
```powershell
kubectl apply -f test/monitoring/logs-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=logs-test
```

### 3. Testes de Alertas
```powershell
kubectl apply -f test/monitoring/alerts-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=alerts-test
```

## Testes de Backup e Restauração

### 1. Testes de Backup
```powershell
kubectl apply -f test/backup/backup-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=backup-test
```

### 2. Testes de Restauração
```powershell
kubectl apply -f test/backup/restore-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=restore-test
```

### 3. Verificação de Integridade
```powershell
kubectl apply -f test/backup/integrity-test.yaml
kubectl logs -n $env:TEST_NAMESPACE -l app=integrity-test
```

## Limpeza

### 1. Remoção de Recursos
```powershell
kubectl delete namespace $env:TEST_NAMESPACE
```

### 2. Remoção do Cluster
```powershell
kind delete cluster
```

### 3. Limpeza de Artefatos
```powershell
Remove-Item -Recurse -Force test/results/*
Remove-Item -Recurse -Force test/logs/*
``` 