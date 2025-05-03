# Guia de Instalação do Sistema de Autocura Cognitiva

## Pré-requisitos

### Requisitos Mínimos do Sistema
- Windows 10 ou superior
- Docker Desktop 20.10.0 ou superior
- Kind 0.11.0 ou superior
- kubectl 1.21.0 ou superior
- 8GB de RAM
- 20GB de espaço em disco

### Verificação de Pré-requisitos
```powershell
# Verificar versão do Docker
docker --version

# Verificar versão do Kind
kind version

# Verificar versão do kubectl
kubectl version --client

# Verificar recursos do sistema
systeminfo | findstr "Total Physical Memory"
```

## Instalação

### 1. Configuração do Ambiente
1. Clone o repositório:
```powershell
git clone https://github.com/seu-usuario/autocura-cognitiva.git
cd autocura-cognitiva
```

2. Configure as variáveis de ambiente:
```powershell
$env:NAMESPACE="autocura-cognitiva"
$env:REGISTRY="localhost:5000"
$env:TAG="latest"
```

### 2. Inicialização do Cluster
1. Execute o script de inicialização:
```powershell
.\scripts\00-start_all.cmd
```

2. Verifique o status do cluster:
```powershell
kubectl cluster-info
kubectl get nodes
```

### 3. Configuração do Registry
1. Inicie o registry local:
```powershell
docker run -d -p 5000:5000 --name registry registry:2
```

2. Verifique o status do registry:
```powershell
docker ps | findstr registry
```

### 4. Construção e Push das Imagens
1. Construa as imagens:
```powershell
docker build -t $env:REGISTRY/monitoramento:$env:TAG -f docker/monitoramento/Dockerfile .
docker build -t $env:REGISTRY/diagnostico:$env:TAG -f docker/diagnostico/Dockerfile .
docker build -t $env:REGISTRY/gerador-acoes:$env:TAG -f docker/gerador-acoes/Dockerfile .
docker build -t $env:REGISTRY/observabilidade:$env:TAG -f docker/observabilidade/Dockerfile .
docker build -t $env:REGISTRY/healing-operator:$env:TAG -f docker/healing-operator/Dockerfile .
docker build -t $env:REGISTRY/rollback-operator:$env:TAG -f docker/rollback-operator/Dockerfile .
```

2. Faça push das imagens:
```powershell
docker push $env:REGISTRY/monitoramento:$env:TAG
docker push $env:REGISTRY/diagnostico:$env:TAG
docker push $env:REGISTRY/gerador-acoes:$env:TAG
docker push $env:REGISTRY/observabilidade:$env:TAG
docker push $env:REGISTRY/healing-operator:$env:TAG
docker push $env:REGISTRY/rollback-operator:$env:TAG
```

### 5. Aplicação dos Recursos Kubernetes
1. Crie o namespace:
```powershell
kubectl apply -f k8s/00-namespace.yaml
```

2. Aplique os CRDs:
```powershell
kubectl apply -f k8s/01-crds/
```

3. Aplique os operadores:
```powershell
kubectl apply -f k8s/02-operators/
```

4. Aplique os componentes:
```powershell
kubectl apply -f k8s/03-components/
```

5. Aplique o armazenamento:
```powershell
kubectl apply -f k8s/04-storage/
```

6. Aplique o ambiente de desenvolvimento:
```powershell
kubectl apply -f k8s/05-dev/
```

### 6. Verificação da Instalação
1. Verifique o status dos pods:
```powershell
kubectl get pods -n $env:NAMESPACE
```

2. Verifique os serviços:
```powershell
kubectl get svc -n $env:NAMESPACE
```

3. Verifique os deployments:
```powershell
kubectl get deployments -n $env:NAMESPACE
```

## Pós-Instalação

### 1. Configuração de Logs
Os logs são armazenados em:
- `logs/install.log`: Logs da instalação
- `logs/operator.log`: Logs dos operadores
- `logs/application.log`: Logs da aplicação

### 2. Configuração de Monitoramento
1. Acesse o dashboard do Grafana:
```powershell
kubectl port-forward svc/grafana -n $env:NAMESPACE 3000:3000
```

2. Acesse em: http://localhost:3000

### 3. Configuração de Backup
Os backups são executados automaticamente:
- Diariamente às 2:00 AM
- Armazenados em: `/backups/autocura`
- Retenção: 7 dias

## Solução de Problemas

### 1. Pods em Estado Pending
```powershell
# Verificar eventos
kubectl describe pod <pod-name> -n $env:NAMESPACE

# Verificar logs
kubectl logs <pod-name> -n $env:NAMESPACE
```

### 2. Problemas com Registry
```powershell
# Verificar status do registry
docker ps | findstr registry

# Reiniciar registry
docker restart registry
```

### 3. Problemas de RBAC
```powershell
# Verificar permissões
kubectl auth can-i --list -n $env:NAMESPACE

# Verificar service account
kubectl get serviceaccount -n $env:NAMESPACE
```

## Atualização do Sistema

### 1. Atualização de Imagens
```powershell
# Reconstruir e push das imagens
.\scripts\00-start_all.cmd --build-images

# Atualizar deployments
kubectl rollout restart deployment -n $env:NAMESPACE
```

### 2. Atualização de Configurações
```powershell
# Aplicar novas configurações
kubectl apply -f k8s/

# Verificar status
kubectl get pods -n $env:NAMESPACE
```

## Segurança

### 1. Configuração de Secrets
```powershell
# Criar secrets
kubectl create secret generic autocura-secrets -n $env:NAMESPACE \
  --from-literal=api-key=<api-key> \
  --from-literal=db-password=<password>
```

### 2. Configuração de Network Policies
```powershell
# Aplicar políticas de rede
kubectl apply -f k8s/security/network-policies.yaml
```

### 3. Configuração de RBAC
```powershell
# Aplicar configurações RBAC
kubectl apply -f k8s/security/rbac.yaml
```

## Recursos de Segurança

### Registry Local
- O registry local é configurado com restart automático
- Executa na porta 5000
- Nome do container: `registry`

### Namespace
- Nome: `autocura-cognitiva`
- Isolado de outros namespaces
- Configurações de RBAC aplicadas

## Suporte

### Logs
- Logs do script: `logs/startup_*.log`
- Logs dos pods: `kubectl logs`
- Logs do cluster: `kubectl get events`

### Diagnóstico
Para diagnóstico detalhado:
1. Execute o script de diagnóstico:
```bash
.\scripts\diagnostico.cmd
```

2. Verifique os logs gerados em:
```
logs/diagnostico_*.log
```

## Notas de Versão

### Versão 2.0.0
- Adicionado sistema de retry para operações críticas
- Implementado logging detalhado
- Melhor tratamento de erros
- Verificação de versões dos componentes
- Verificação automática do estado dos pods
- Modularização do código
- Melhor organização e documentação 