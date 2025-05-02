#!/bin/bash

# Aplicar o namespace de monitoramento
kubectl apply -f namespace.yaml

# Aplicar as configurações de monitoramento
kubectl apply -k .

# Verificar o status dos pods
kubectl get pods -n monitoring

# Verificar os serviços
kubectl get svc -n monitoring 