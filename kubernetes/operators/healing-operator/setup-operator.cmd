@echo off
echo Compilando o operador...
go build -o healing-operator main.go

echo Construindo a imagem Docker...
docker build -t localhost:5000/autocura-cognitiva/healing-operator:dev .

echo Enviando a imagem para o registry local...
docker push localhost:5000/autocura-cognitiva/healing-operator:dev

echo Aplicando os CRDs...
kubectl apply -f config/crd/bases/healing.autocura-cognitiva.io_healings.yaml

echo Aplicando o RBAC...
kubectl apply -f config/rbac/role.yaml
kubectl apply -f config/rbac/role_binding.yaml
kubectl apply -f config/rbac/service_account.yaml

echo Implantando o operador...
kubectl apply -f config/manager/manager.yaml

echo Operador configurado com sucesso! 