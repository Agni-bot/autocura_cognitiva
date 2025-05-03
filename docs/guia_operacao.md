# Guia de Operação do Sistema de Autocura Cognitiva

## Procedimentos Diários

### 1. Verificação do Cluster
```powershell
# Status do cluster
kubectl get nodes
kubectl get pods -A
kubectl get services -A
kubectl get events --sort-by='.lastTimestamp'
```

### 2. Monitoramento
```powershell
# Métricas
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000

# Logs
kubectl port-forward svc/kibana 5601:5601

# Alertas
kubectl port-forward svc/alertmanager 9093:9093
```

### 3. Backup
```powershell
# Backup de configurações
kubectl get all -n $env:NAMESPACE -o yaml > backup.yaml

# Backup de dados
kubectl apply -f backup/backup-job.yaml
kubectl logs -n $env:NAMESPACE -l app=backup-job
```

## Manutenção

### 1. Atualizações
```powershell
# Atualização de imagens
kubectl set image deployment/healing-operator healing-operator=$env:REGISTRY/healing-operator:latest
kubectl set image deployment/rollback-operator rollback-operator=$env:REGISTRY/rollback-operator:latest

# Verificação
kubectl rollout status deployment/healing-operator
kubectl rollout status deployment/rollback-operator
```

### 2. Limpeza
```powershell
# Limpeza de pods
kubectl delete pods --field-selector status.phase=Succeeded
kubectl delete jobs --field-selector status.successful=1

# Limpeza de recursos
kubectl delete pvc --field-selector status.phase=Released
kubectl delete pv --field-selector status.phase=Released
```

### 3. Escalabilidade
```powershell
# Escalabilidade horizontal
kubectl scale deployment healing-operator --replicas=3
kubectl scale deployment rollback-operator --replicas=3

# Escalabilidade vertical
kubectl set resources deployment healing-operator --limits=cpu=1,memory=1Gi
kubectl set resources deployment rollback-operator --limits=cpu=1,memory=1Gi
```

## Recuperação

### 1. Recuperação de Pods
```powershell
# Verificação de status
kubectl get pods -n $env:NAMESPACE
kubectl describe pods -n $env:NAMESPACE

# Reinicialização
kubectl rollout restart deployment/healing-operator
kubectl rollout restart deployment/rollback-operator

# Verificação de logs
kubectl logs -n $env:NAMESPACE -l app=healing-operator
kubectl logs -n $env:NAMESPACE -l app=rollback-operator
```

### 2. Recuperação de Dados
```powershell
# Lista de backups
kubectl get backups -n $env:NAMESPACE

# Restauração
kubectl apply -f backup/restore-job.yaml
kubectl logs -n $env:NAMESPACE -l app=restore-job
```

### 3. Recuperação de Configurações
```powershell
# Restauração de configurações
kubectl apply -f backup/restore-config.yaml

# Verificação
kubectl get configmaps -n $env:NAMESPACE
kubectl get secrets -n $env:NAMESPACE
```

## Segurança

### 1. Rotação de Secrets
```powershell
# Criação de novos secrets
kubectl create secret generic new-api-key --from-literal=key=value
kubectl create secret tls new-tls-cert --cert=cert.pem --key=key.pem

# Atualização de referências
kubectl set env deployment/healing-operator API_KEY=new-api-key
kubectl set env deployment/rollback-operator API_KEY=new-api-key
```

### 2. Atualização de Certificados
```powershell
# Verificação de certificados
kubectl get certificates -n $env:NAMESPACE
kubectl describe certificates -n $env:NAMESPACE

# Rotação
kubectl apply -f security/cert-rotation.yaml
```

### 3. Auditoria de Acesso
```powershell
# Verificação de logs
kubectl get events --sort-by='.lastTimestamp'
kubectl get auditlogs

# Verificação de permissões
kubectl auth can-i --list
```

## Monitoramento

### 1. Configuração de Alertas
```powershell
# Verificação de regras
kubectl get prometheusrules -n $env:NAMESPACE
kubectl describe prometheusrules -n $env:NAMESPACE

# Teste de alertas
kubectl port-forward svc/alertmanager 9093:9093
curl -X POST http://localhost:9093/api/v1/alerts
```

### 2. Análise de Métricas
```powershell
# Consulta de métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=system_metrics'

# Exportação
kubectl port-forward svc/grafana 3000:3000
```

### 3. Geração de Relatórios
```powershell
# Status do sistema
kubectl get all -n $env:NAMESPACE
kubectl get events --sort-by='.lastTimestamp'

# Exportação de métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query_range' --data-urlencode 'query=system_metrics' --data-urlencode 'start=1h' --data-urlencode 'end=now' --data-urlencode 'step=1m'
```

## Troubleshooting

### 1. Diagnóstico de Problemas
```powershell
# Verificação de eventos
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pods -n $env:NAMESPACE

# Verificação de logs
kubectl logs -n $env:NAMESPACE -l app=healing-operator
kubectl logs -n $env:NAMESPACE -l app=rollback-operator
```

### 2. Análise de Performance
```powershell
# Uso de recursos
kubectl top nodes
kubectl top pods -n $env:NAMESPACE

# Métricas detalhadas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=performance_metrics'
```

### 3. Resolução de Problemas
```powershell
# Reinicialização de componentes
kubectl rollout restart deployment/healing-operator
kubectl rollout restart deployment/rollback-operator

# Verificação de status
kubectl rollout status deployment/healing-operator
kubectl rollout status deployment/rollback-operator
```

## Backup e Restauração

### 1. Backup de Configurações
```powershell
# Exportação de configurações
kubectl get all -n $env:NAMESPACE -o yaml > backup.yaml
kubectl get configmaps -n $env:NAMESPACE -o yaml > configmaps.yaml
kubectl get secrets -n $env:NAMESPACE -o yaml > secrets.yaml
```

### 2. Backup de Dados
```powershell
# Execução de backup
kubectl apply -f backup/backup-job.yaml
kubectl logs -n $env:NAMESPACE -l app=backup-job

# Verificação de status
kubectl get backups -n $env:NAMESPACE
```

### 3. Restauração de Dados
```powershell
# Restauração de configurações
kubectl apply -f backup/restore-config.yaml

# Restauração de dados
kubectl apply -f backup/restore-job.yaml
kubectl logs -n $env:NAMESPACE -l app=restore-job
```

## Atualizações

### 1. Atualização de Versões
```powershell
# Atualização de imagens
kubectl set image deployment/healing-operator healing-operator=$env:REGISTRY/healing-operator:v2.0.0
kubectl set image deployment/rollback-operator rollback-operator=$env:REGISTRY/rollback-operator:v2.0.0

# Verificação
kubectl rollout status deployment/healing-operator
kubectl rollout status deployment/rollback-operator
```

### 2. Rollback
```powershell
# Rollback de atualizações
kubectl rollout undo deployment/healing-operator
kubectl rollout undo deployment/rollback-operator

# Verificação
kubectl rollout status deployment/healing-operator
kubectl rollout status deployment/rollback-operator
```

### 3. Verificação de Compatibilidade
```powershell
# Verificação de versões
kubectl version
kubectl api-versions

# Verificação de recursos
kubectl api-resources
``` 