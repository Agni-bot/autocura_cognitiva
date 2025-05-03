@echo off
REM Script para inicializar todo o Sistema de Autocura Cognitiva no Kubernetes local (Kind)

REM 1. Verificar se Docker está rodando
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Docker não está instalado. Instale o Docker Desktop e tente novamente.
    pause
    exit /b 1
)
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O Docker Desktop não está rodando. Por favor, inicie o Docker e tente novamente.
    pause
    exit /b 1
)

REM 1.1. Verificar se o registro local está rodando
REM Procura por um container chamado 'registry' rodando na porta 5000
for /f "tokens=*" %%i in ('docker ps --format "{{.Names}}"') do (
    echo %%i | findstr /C:"registry" >nul 2>&1 && set REGISTRY_RUNNING=1
)
if not defined REGISTRY_RUNNING (
    echo [INFO] Registro local na porta 5000 não está rodando. Iniciando registry local...
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao iniciar o registro local Docker na porta 5000.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Registro local já está rodando.
)

REM 2. Verificar se kind está instalado
where kind >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Kind não está instalado. Instale o Kind e tente novamente.
    pause
    exit /b 1
)

REM 3. Verificar se kubectl está instalado
where kubectl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] kubectl não está instalado. Instale o kubectl e tente novamente.
    pause
    exit /b 1
)

REM 4. Criar o cluster Kind se necessário
cd ..\kind-config
call setup-kind.cmd
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao criar/configurar o cluster Kind.
    pause
    exit /b 1
)
cd ..\scripts

REM 5. Criar o namespace antes de aplicar qualquer recurso
kubectl apply -f ..\kubernetes\base\namespace.yaml

REM 6. Buildar e push das imagens Docker para o registro local
set REGISTRY=localhost:5000
set TAG=latest
set BASE_DIR=%CD%\..

echo [INFO] Buildando imagem do monitoramento...
cd "%BASE_DIR%\src\monitoramento"
docker build -t %REGISTRY%/autocura-cognitiva/monitoramento:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/monitoramento:%TAG%

echo [INFO] Buildando imagem do diagnóstico...
cd "%BASE_DIR%\src\diagnostico"
docker build -t %REGISTRY%/autocura-cognitiva/diagnostico:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/diagnostico:%TAG%

echo [INFO] Buildando imagem do gerador de ações...
cd "%BASE_DIR%\src\gerador_acoes"
docker build -t %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG%

echo [INFO] Buildando imagem da observabilidade...
cd "%BASE_DIR%\src\observabilidade"
docker build -t %REGISTRY%/autocura-cognitiva/observabilidade:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/observabilidade:%TAG%

cd "%BASE_DIR%\scripts"

REM 7. Aplicar os manifests Kubernetes do ambiente de desenvolvimento
cd "%BASE_DIR%\kubernetes"
echo [INFO] Aplicando recursos base...
kubectl apply -k base

if exist operators (
    echo [INFO] Aplicando operadores customizados...
    kubectl apply -k operators
)
if exist components (
    echo [INFO] Aplicando componentes do sistema...
    kubectl apply -k components
)
if exist storage (
    echo [INFO] Aplicando recursos de armazenamento...
    kubectl apply -k storage
)

REM 7.1 Limpar deployments antigos para evitar erro de campo imutável
kubectl delete deployment --all -n autocura-cognitiva

if exist environments\development (
    echo [INFO] Aplicando ambiente de desenvolvimento...
    kubectl apply -k environments\development
)

REM 8. Mostrar status dos pods e serviços
kubectl get pods -n autocura-cognitiva
kubectl get services -n autocura-cognitiva

REM 9. Mensagem final

echo [SUCESSO] Todos os serviços do Sistema de Autocura Cognitiva foram implantados no cluster Kubernetes local!
pause
exit /b 0 