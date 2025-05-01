@echo off
echo Compilando o módulo de observabilidade...
cd observability
go build -o observability-server main.go

echo Construindo a imagem Docker...
docker build -t localhost:5000/autocura-cognitiva/healing-observability:dev .

echo Enviando a imagem para o registry local...
docker push localhost:5000/autocura-cognitiva/healing-observability:dev

echo Implantando o módulo de observabilidade...
kubectl apply -f k8s/deployment.yaml

echo Aguardando o módulo estar pronto...
kubectl wait --for=condition=ready pod -l app=healing-observability -n healing-operator-system --timeout=60s

echo Configurando o port-forward para acesso local...
kubectl port-forward -n healing-operator-system service/healing-observability 8080:80

echo Módulo de observabilidade configurado com sucesso!
echo Acesse http://localhost:8080 para visualizar a interface 