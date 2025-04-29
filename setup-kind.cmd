@echo off
REM Script para configurar um ambiente Kubernetes local usando kind no Windows
REM para o Sistema Autocura Cognitiva

echo === Configurando ambiente Kubernetes local com kind ===

REM Verificar se o kind está instalado
where kind >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo kind não está instalado. Por favor, instale-o seguindo as instruções em:
    echo https://kind.sigs.k8s.io/docs/user/quick-start/#installation
    exit /b 1
)

REM Verificar se o kubectl está instalado
where kubectl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo kubectl não está instalado. Por favor, instale-o seguindo as instruções em:
    echo https://kubernetes.io/docs/tasks/tools/install-kubectl/
    exit /b 1
)

REM Verificar se o Docker está instalado e em execução
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker não está instalado ou não está em execução.
    echo Por favor, instale o Docker Desktop e inicie-o antes de continuar.
    exit /b 1
)

REM Criar arquivo de configuração do kind
echo kind: Cluster > kind-config.yaml
echo apiVersion: kind.x-k8s.io/v1alpha4 >> kind-config.yaml
echo name: autocura-cognitiva >> kind-config.yaml
echo nodes: >> kind-config.yaml
echo - role: control-plane >> kind-config.yaml
echo   extraPortMappings: >> kind-config.yaml
echo   - containerPort: 30000 >> kind-config.yaml
echo     hostPort: 30000 >> kind-config.yaml
echo     protocol: TCP >> kind-config.yaml
echo   - containerPort: 30001 >> kind-config.yaml
echo     hostPort: 30001 >> kind-config.yaml
echo     protocol: TCP >> kind-config.yaml
echo containerdConfigPatches: >> kind-config.yaml
echo - |- >> kind-config.yaml
echo   [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:5000"] >> kind-config.yaml
echo     endpoint = ["http://registry:5000"] >> kind-config.yaml

REM Verificar se o cluster já existe
kind get clusters | findstr "autocura-cognitiva" >nul
if %ERRORLEVEL% EQU 0 (
    echo Cluster 'autocura-cognitiva' já existe. Deseja excluí-lo e criar um novo? (s/n)
    set /p resposta=
    if /I "%resposta%"=="s" (
        echo Excluindo cluster existente...
        kind delete cluster --name autocura-cognitiva
    ) else (
        echo Mantendo cluster existente. Configuração concluída!
        del kind-config.yaml
        exit /b 0
    )
)

REM Iniciar o registro local se ainda não estiver em execução
docker ps | findstr "registry:2" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando registro Docker local na porta 5000...
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
) else (
    echo Registro local já está em execução.
)

REM Criar uma rede Docker para o kind e o registro se não existir
docker network ls | findstr "kind" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Criando rede Docker 'kind'...
    docker network create kind
)

REM Conectar o registro à rede kind
docker network inspect kind | findstr "registry" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Conectando o registro à rede kind...
    docker network connect kind registry
)

REM Criar cluster kind com a configuração personalizada
echo Criando cluster kind 'autocura-cognitiva'...
kind create cluster --config kind-config.yaml

REM Verificar se o cluster foi criado com sucesso
kind get clusters | findstr "autocura-cognitiva" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Falha ao criar o cluster kind.
    exit /b 1
)

echo Cluster kind 'autocura-cognitiva' criado com sucesso!

REM Configurar kubectl para usar o contexto do kind
kubectl cluster-info --context kind-autocura-cognitiva

REM Limpar arquivo de configuração temporário
del kind-config.yaml

echo === Ambiente Kubernetes local configurado com sucesso! ===
echo Agora você pode executar 'build.cmd' para construir as imagens e
echo em seguida 'kubectl apply -k kubernetes\environments\development' para implantar o sistema.
