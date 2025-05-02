@echo off
echo Criando um recurso Healing de exemplo...
kubectl apply -f config/samples/healing_v1_healing.yaml

echo Verificando o status do recurso...
kubectl get healings

echo Verificando os logs do operador...
kubectl logs -n healing-operator-system deployment/healing-operator-controller-manager

echo Teste concluído! 