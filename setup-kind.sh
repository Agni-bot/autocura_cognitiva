#!/bin/bash

# Script para configurar um ambiente Kubernetes local usando kind
# para o Sistema Autocura Cognitiva

set -e

echo "=== Configurando ambiente Kubernetes local com kind ==="

# Verificar se o kind está instalado
if ! command -v kind &> /dev/null; then
    echo "kind não está instalado. Por favor, instale-o seguindo as instruções em:"
    echo "https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Verificar se o kubectl está instalado
if ! command -v kubectl &> /dev/null; then
    echo "kubectl não está instalado. Por favor, instale-o seguindo as instruções em:"
    echo "https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
fi

# Verificar se o Docker está instalado e em execução
if ! docker info &> /dev/null; then
    echo "Docker não está instalado ou não está em execução."
    echo "Por favor, instale o Docker e inicie-o antes de continuar."
    exit 1
fi

# Criar arquivo de configuração do kind
cat > kind-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: autocura_cognitiva
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
    protocol: TCP
  - containerPort: 30001
    hostPort: 30001
    protocol: TCP
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:5000"]
    endpoint = ["http://registry:5000"]
EOF

# Verificar se o cluster já existe
if kind get clusters | grep -q "autocura_cognitiva"; then
    echo "Cluster 'autocura_cognitiva' já existe. Deseja excluí-lo e criar um novo? (s/n)"
    read -r resposta
    if [[ "$resposta" =~ ^[Ss]$ ]]; then
        echo "Excluindo cluster existente..."
        kind delete cluster --name autocura_cognitiva
    else
        echo "Mantendo cluster existente. Configuração concluída!"
        rm kind-config.yaml
        exit 0
    fi
fi

# Iniciar o registro local se ainda não estiver em execução
if ! docker ps | grep -q registry:2; then
    echo "Iniciando registro Docker local na porta 5000..."
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
else
    echo "Registro local já está em execução."
fi

# Criar uma rede Docker para o kind e o registro se não existir
if ! docker network ls | grep -q "kind"; then
    echo "Criando rede Docker 'kind'..."
    docker network create kind
fi

# Conectar o registro à rede kind
if ! docker network inspect kind | grep -q "registry"; then
    echo "Conectando o registro à rede kind..."
    docker network connect kind registry
fi

# Criar cluster kind com a configuração personalizada
echo "Criando cluster kind 'autocura_cognitiva'..."
kind create cluster --config kind-config.yaml

# Verificar se o cluster foi criado com sucesso
if ! kind get clusters | grep -q "autocura_cognitiva"; then
    echo "Falha ao criar o cluster kind."
    exit 1
fi

echo "Cluster kind 'autocura_cognitiva' criado com sucesso!"

# Configurar kubectl para usar o contexto do kind
kubectl cluster-info --context kind-autocura_cognitiva

# Limpar arquivo de configuração temporário
rm kind-config.yaml

echo "=== Ambiente Kubernetes local configurado com sucesso! ==="
echo "Agora você pode executar './build.sh' para construir as imagens e"
echo "em seguida 'kubectl apply -k kubernetes/environments/development' para implantar o sistema."
