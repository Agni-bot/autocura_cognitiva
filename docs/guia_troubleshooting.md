# Guia de Troubleshooting do Sistema de Autocura Cognitiva

## Problemas Comuns

### 1. Pods em Estado Pending
```powershell
# Verificar eventos
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pods -n $env:NAMESPACE

# Verificar recursos
kubectl describe nodes
kubectl top nodes
kubectl top pods -n $env:NAMESPACE

# Verificar PVCs
kubectl get pvc -n $env:NAMESPACE
kubectl describe pvc -n $env:NAMESPACE
```

### 2. Problemas com Registry
```powershell
# Verificar status do registry
docker ps | findstr registry
docker logs registry

# Verificar conexão
kubectl get pods -n $env:NAMESPACE -o wide
kubectl describe pods -n $env:NAMESPACE

# Verificar imagens
docker images | findstr $env:REGISTRY
```

### 3. Problemas de RBAC
```powershell
# Verificar permissões
kubectl auth can-i --list
kubectl get roles -n $env:NAMESPACE
kubectl get rolebindings -n $env:NAMESPACE

# Verificar service accounts
kubectl get serviceaccounts -n $env:NAMESPACE
kubectl describe serviceaccounts -n $env:NAMESPACE
```

## Problemas de Rede

### 1. Conectividade entre Pods
```powershell
# Verificar network policies
kubectl get networkpolicies -n $env:NAMESPACE
kubectl describe networkpolicies -n $env:NAMESPACE

# Verificar serviços
kubectl get services -n $env:NAMESPACE
kubectl describe services -n $env:NAMESPACE

# Verificar endpoints
kubectl get endpoints -n $env:NAMESPACE
kubectl describe endpoints -n $env:NAMESPACE
```

### 2. Problemas de DNS
```powershell
# Verificar CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns

# Verificar resolução
kubectl run -it --rm --restart=Never busybox --image=busybox -- nslookup kubernetes.default
```

### 3. Problemas de Ingress
```powershell
# Verificar ingress
kubectl get ingress -n $env:NAMESPACE
kubectl describe ingress -n $env:NAMESPACE

# Verificar ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Problemas de Armazenamento

### 1. Problemas com PVCs
```powershell
# Verificar PVCs
kubectl get pvc -n $env:NAMESPACE
kubectl describe pvc -n $env:NAMESPACE

# Verificar PVs
kubectl get pv
kubectl describe pv

# Verificar storage classes
kubectl get storageclasses
kubectl describe storageclasses
```

### 2. Problemas de Backup
```powershell
# Verificar jobs de backup
kubectl get jobs -n $env:NAMESPACE
kubectl describe jobs -n $env:NAMESPACE

# Verificar logs
kubectl logs -n $env:NAMESPACE -l app=backup-job

# Verificar volumes
kubectl get volumesnapshots -n $env:NAMESPACE
kubectl describe volumesnapshots -n $env:NAMESPACE
```

### 3. Problemas de Restauração
```powershell
# Verificar jobs de restauração
kubectl get jobs -n $env:NAMESPACE
kubectl describe jobs -n $env:NAMESPACE

# Verificar logs
kubectl logs -n $env:NAMESPACE -l app=restore-job

# Verificar volumes
kubectl get pvc -n $env:NAMESPACE
kubectl describe pvc -n $env:NAMESPACE
```

## Problemas de Performance

### 1. Uso de Recursos
```powershell
# Verificar uso de CPU
kubectl top nodes
kubectl top pods -n $env:NAMESPACE

# Verificar uso de memória
kubectl top nodes --no-headers | Sort-Object -Property CPU -Descending
kubectl top pods -n $env:NAMESPACE --no-headers | Sort-Object -Property CPU -Descending
```

### 2. Problemas de Escala
```powershell
# Verificar HPA
kubectl get hpa -n $env:NAMESPACE
kubectl describe hpa -n $env:NAMESPACE

# Verificar métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=scaling_metrics'
```

### 3. Problemas de Latência
```powershell
# Verificar métricas
kubectl port-forward svc/prometheus 9090:9090
curl -G 'http://localhost:9090/api/v1/query' --data-urlencode 'query=latency_metrics'

# Verificar logs
kubectl logs -n $env:NAMESPACE -l app=healing-operator
kubectl logs -n $env:NAMESPACE -l app=rollback-operator
```

## Problemas de Segurança

### 1. Problemas de Autenticação
```powershell
# Verificar service accounts
kubectl get serviceaccounts -n $env:NAMESPACE
kubectl describe serviceaccounts -n $env:NAMESPACE

# Verificar tokens
kubectl get secrets -n $env:NAMESPACE
kubectl describe secrets -n $env:NAMESPACE
```

### 2. Problemas de Autorização
```powershell
# Verificar roles
kubectl get roles -n $env:NAMESPACE
kubectl describe roles -n $env:NAMESPACE

# Verificar role bindings
kubectl get rolebindings -n $env:NAMESPACE
kubectl describe rolebindings -n $env:NAMESPACE
```

### 3. Problemas de Criptografia
```powershell
# Verificar certificados
kubectl get certificates -n $env:NAMESPACE
kubectl describe certificates -n $env:NAMESPACE

# Verificar secrets
kubectl get secrets -n $env:NAMESPACE
kubectl describe secrets -n $env:NAMESPACE
```

## Problemas de Monitoramento

### 1. Problemas com Prometheus
```powershell
# Verificar status
kubectl get pods -n monitoring
kubectl describe pods -n monitoring

# Verificar logs
kubectl logs -n monitoring -l app=prometheus
```

### 2. Problemas com Grafana
```powershell
# Verificar status
kubectl get pods -n monitoring
kubectl describe pods -n monitoring

# Verificar logs
kubectl logs -n monitoring -l app=grafana
```

### 3. Problemas com Alertmanager
```powershell
# Verificar status
kubectl get pods -n monitoring
kubectl describe pods -n monitoring

# Verificar logs
kubectl logs -n monitoring -l app=alertmanager
```

## Problemas com Operadores

### 1. Problemas com Healing Operator
```powershell
# Verificar status
kubectl get pods -n $env:NAMESPACE -l app=healing-operator
kubectl describe pods -n $env:NAMESPACE -l app=healing-operator

# Verificar logs
kubectl logs -n $env:NAMESPACE -l app=healing-operator
```

### 2. Problemas com Rollback Operator
```powershell
# Verificar status
kubectl get pods -n $env:NAMESPACE -l app=rollback-operator
kubectl describe pods -n $env:NAMESPACE -l app=rollback-operator

# Verificar logs
kubectl logs -n $env:NAMESPACE -l app=rollback-operator
```

### 3. Problemas com CRDs
```powershell
# Verificar CRDs
kubectl get crds
kubectl describe crds

# Verificar recursos
kubectl get healing -n $env:NAMESPACE
kubectl get rollback -n $env:NAMESPACE
```

## Problemas com Logs

### 1. Problemas com Fluentd
```powershell
# Verificar status
kubectl get pods -n logging
kubectl describe pods -n logging

# Verificar logs
kubectl logs -n logging -l app=fluentd
```

### 2. Problemas com Elasticsearch
```powershell
# Verificar status
kubectl get pods -n logging
kubectl describe pods -n logging

# Verificar logs
kubectl logs -n logging -l app=elasticsearch
```

### 3. Problemas com Kibana
```powershell
# Verificar status
kubectl get pods -n logging
kubectl describe pods -n logging

# Verificar logs
kubectl logs -n logging -l app=kibana
``` 