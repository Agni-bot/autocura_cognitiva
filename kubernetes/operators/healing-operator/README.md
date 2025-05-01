# Operador Healing - Autocura Cognitiva

Este operador Kubernetes implementa funcionalidades de autocura para aplicações em execução no cluster.

## Pré-requisitos

- Kubernetes cluster (versão 1.16+)
- kubectl configurado para acessar o cluster
- Docker instalado
- Go 1.18+ instalado
- Kind instalado (para ambiente de desenvolvimento)

## Instalação

### 1. Configuração do Ambiente de Desenvolvimento

```bash
# Criar cluster local com Kind
./setup-kind.cmd

# Configurar o Docker Registry local
kubectl apply -f config/registry.yaml
```

### 2. Compilação e Implantação do Operador

```bash
# Compilar o operador
go build -o healing-operator main.go

# Construir a imagem Docker
docker build -t localhost:5000/autocura-cognitiva/healing-operator:dev .

# Fazer push da imagem para o registry local
docker push localhost:5000/autocura-cognitiva/healing-operator:dev
```

### 3. Implantação no Cluster

```bash
# Aplicar os CRDs
kubectl apply -f config/crd/bases/healing.autocura-cognitiva.io_healings.yaml

# Implantar o operador
kubectl apply -f config/manager/manager.yaml
```

## Uso

### Criando um Recurso Healing

1. Crie um arquivo YAML com a configuração do Healing:

```yaml
apiVersion: healing.autocura-cognitiva.io/v1
kind: Healing
metadata:
  name: exemplo-healing
spec:
  checkInterval: 300  # Intervalo de verificação em segundos
```

2. Aplique a configuração:

```bash
kubectl apply -f exemplo-healing.yaml
```

### Verificando o Status

```bash
# Listar todos os recursos Healing
kubectl get healings

# Verificar detalhes de um recurso específico
kubectl describe healing exemplo-healing
```

## Funcionalidades

O operador Healing implementa as seguintes funcionalidades:

1. Monitoramento periódico de recursos
2. Detecção automática de problemas
3. Aplicação de ações corretivas
4. Registro de eventos e status

## Monitoramento

O operador expõe métricas em:
- `:8080/metrics` - Métricas do operador
- `:8081/healthz` - Endpoint de health check

## Troubleshooting

### Verificar Logs do Operador

```bash
kubectl logs -n healing-operator-system deployment/healing-operator-controller-manager
```

### Verificar Status do Operador

```bash
kubectl get pods -n healing-operator-system
```

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das suas mudanças
4. Envie um pull request

## Licença

Este projeto está licenciado sob a Apache License 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes. 