#!/bin/bash

# Construir a imagem do servidor WebSocket
cd src/observabilidade
docker build -t observabilidade-websocket:latest .
cd ../..

# Construir o frontend
cd src/observabilidade/frontend
npm install
npm run build
cd ../../..

# Aplicar as configurações do Kubernetes
kubectl apply -f k8s/observabilidade/websocket-deployment.yaml
kubectl apply -f k8s/observabilidade/websocket-service.yaml

# Expor o serviço do WebSocket
kubectl port-forward -n monitoring svc/observabilidade-websocket 3001:3001 &

echo "Sistema de observabilidade implantado!"
echo "Acesse o frontend em: http://localhost:3000"
echo "WebSocket disponível em: ws://localhost:3001" 