@echo off
echo Criando cluster Kind...

kind create cluster --name healing-cluster --config=config/kind-config.yaml

echo Configurando o registry local...
kubectl apply -f config/registry.yaml

echo Aguardando o registry estar pronto...
kubectl wait --for=condition=ready pod -l app=registry -n registry --timeout=60s

echo Configurando o Docker para usar o registry local...
docker network connect kind registry-registry

echo Cluster Kind configurado com sucesso! 