@echo off
echo Removendo o operador...
kubectl delete -f config/manager/manager.yaml

echo Removendo o RBAC...
kubectl delete -f config/rbac/role_binding.yaml
kubectl delete -f config/rbac/role.yaml
kubectl delete -f config/rbac/service_account.yaml

echo Removendo os CRDs...
kubectl delete -f config/crd/bases/healing.autocura-cognitiva.io_healings.yaml

echo Removendo o namespace...
kubectl delete namespace healing-operator-system

echo Removendo o registry...
kubectl delete -f config/registry.yaml

echo Removendo o cluster Kind...
kind delete cluster --name healing-cluster

echo Ambiente limpo com sucesso! 