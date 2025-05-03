@echo off
REM Script para inicializar todo o Sistema de Autocura Cognitiva no Kubernetes local (Kind)
REM Versão: 2.0.2
REM Última atualização: %date% %time%

REM Configurações globais
setlocal enabledelayedexpansion
set "LOG_FILE=..\logs\startup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%.log"
set "MAX_RETRIES=3"
set "TIMEOUT_SECONDS=300"
set "REGISTRY=localhost:5000"
set "TAG=latest"
set "BASE_DIR=%CD%"
set "NAMESPACE=autocura-cognitiva"

REM Funções utilitárias
call :log_info "Iniciando script de inicialização do Sistema de Autocura Cognitiva"
call :log_info "Logs serão salvos em: %LOG_FILE%"

REM 1. Verificar pré-requisitos
call :check_prerequisites
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha na verificação de pré-requisitos"
    exit /b 1
)

REM 2. Configurar ambiente
call :setup_environment
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha na configuração do ambiente"
    exit /b 1
)

REM 3. Build e push de imagens
call :build_and_push_images
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha no build e push das imagens"
    exit /b 1
)

REM 4. Aplicar recursos Kubernetes
call :apply_kubernetes_resources
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha na aplicação dos recursos Kubernetes"
    exit /b 1
)

REM 5. Verificar status final
call :check_final_status
if %ERRORLEVEL% NEQ 0 (
    call :log_error "Falha na verificação do status final"
    exit /b 1
)

call :log_info "Script concluído com sucesso!"
exit /b 0

REM ===== Funções =====

:log_info
echo [INFO] %~1
echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%"
exit /b 0

:log_error
echo [ERRO] %~1
echo [%date% %time%] [ERRO] %~1 >> "%LOG_FILE%"
exit /b 1

:check_prerequisites
    call :log_info "Verificando pré-requisitos..."

    REM Verificar Docker
    where docker >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Docker não está instalado"
        exit /b 1
    )

    REM Verificar versão do Docker
    for /f "tokens=*" %%i in ('docker --version') do set "DOCKER_VERSION=%%i"
    call :log_info "Versão do Docker: %DOCKER_VERSION%"

    REM Verificar se Docker está rodando
    set "RETRY_COUNT=0"
    :docker_retry
    docker info >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        set /a "RETRY_COUNT+=1"
        if !RETRY_COUNT! LSS %MAX_RETRIES% (
            call :log_info "Aguardando Docker iniciar (tentativa !RETRY_COUNT! de %MAX_RETRIES%)..."
            timeout /t 5 >nul
            goto docker_retry
        )
        call :log_error "Docker Desktop não está rodando"
        exit /b 1
    )

    REM Verificar Kind
    where kind >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Kind não está instalado"
        exit /b 1
    )

    REM Verificar kubectl
    where kubectl >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "kubectl não está instalado"
        exit /b 1
    )

    REM Verificar versão do kubectl
    for /f "tokens=*" %%i in ('kubectl version --client') do set "KUBECTL_VERSION=%%i"
    call :log_info "Versão do kubectl: %KUBECTL_VERSION%"

    exit /b 0

:setup_environment
    call :log_info "Configurando ambiente..."

    REM Verificar e iniciar registry local
    set "REGISTRY_RUNNING=0"
    for /f "tokens=*" %%i in ('docker ps --format "{{.Names}}"') do (
        echo %%i | findstr /C:"registry" >nul 2>&1 && set "REGISTRY_RUNNING=1"
    )

    if !REGISTRY_RUNNING! EQU 0 (
        call :log_info "Iniciando registry local..."
        docker run -d -p 5000:5000 --restart=always --name registry registry:2
        if %ERRORLEVEL% NEQ 0 (
            call :log_error "Falha ao iniciar registry local"
            exit /b 1
        )
    ) else (
        call :log_info "Registry local já está rodando"
    )

    REM Configurar cluster Kind
    cd "%BASE_DIR%\kind-config"
    call setup-kind.cmd
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Falha ao configurar cluster Kind"
        exit /b 1
    )
    cd "%BASE_DIR%\scripts"

    REM Criar namespace
    kubectl apply -f "%BASE_DIR%\kubernetes\base\namespace.yaml"
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Falha ao criar namespace"
        exit /b 1
    )

    exit /b 0

:build_and_push_images
    call :log_info "Iniciando build e push de imagens..."

    REM Função para build e push com retry
    set "SERVICES=monitoramento diagnostico gerador_acoes observabilidade portal_web"

    for %%s in (%SERVICES%) do (
        call :log_info "Buildando imagem do %%s..."
        cd "%BASE_DIR%\src\%%s"
        
        set "RETRY_COUNT=0"
        :build_retry
        docker build -t %REGISTRY%/autocura-cognitiva/%%s:%TAG% -f Dockerfile .
        if %ERRORLEVEL% NEQ 0 (
            set /a "RETRY_COUNT+=1"
            if !RETRY_COUNT! LSS %MAX_RETRIES% (
                call :log_info "Tentando build novamente (tentativa !RETRY_COUNT! de %MAX_RETRIES%)..."
                timeout /t 5 >nul
                goto build_retry
            )
            call :log_error "Falha ao buildar imagem do %%s"
            exit /b 1
        )

        set "RETRY_COUNT=0"
        :push_retry
        docker push %REGISTRY%/autocura-cognitiva/%%s:%TAG%
        if %ERRORLEVEL% NEQ 0 (
            set /a "RETRY_COUNT+=1"
            if !RETRY_COUNT! LSS %MAX_RETRIES% (
                call :log_info "Tentando push novamente (tentativa !RETRY_COUNT! de %MAX_RETRIES%)..."
                timeout /t 5 >nul
                goto push_retry
            )
            call :log_error "Falha ao enviar imagem do %%s"
            exit /b 1
        )
    )

    cd "%BASE_DIR%\scripts"
    exit /b 0

:apply_kubernetes_resources
    call :log_info "Aplicando recursos Kubernetes..."

    REM Limpar deployments antigos
    call :log_info "Limpando deployments antigos..."
    kubectl delete deployment --all -n %NAMESPACE%

    REM Aplicar recursos na ordem correta
    cd "%BASE_DIR%\kubernetes"

    REM Aplicar CRDs
    if exist operators (
        call :log_info "Aplicando CRDs..."
        kubectl apply -f operators/healing-operator/config/crd/bases/healing.autocura-cognitiva.io_healings.yaml
        kubectl apply -f operators/rollback-operator/config/crd/bases/rollback.autocura-cognitiva.io_rollbacks.yaml
    )

    REM Aplicar recursos base
    call :log_info "Aplicando recursos base..."
    kubectl apply -k base

    REM Aplicar recursos de monitoramento
    call :log_info "Aplicando recursos de monitoramento..."
    kubectl apply -k monitoring

    REM Aplicar recursos de armazenamento
    call :log_info "Aplicando recursos de armazenamento..."
    kubectl apply -k storage

    REM Aplicar recursos de componentes
    call :log_info "Aplicando recursos de componentes..."
    kubectl apply -k components

    REM Aplicar recursos de operadores
    call :log_info "Aplicando recursos de operadores..."
    kubectl apply -k operators

    cd "%BASE_DIR%\scripts"
    exit /b 0

:check_final_status
    call :log_info "Verificando status final..."

    REM Verificar status dos pods
    set "PODS_READY=0"
    set "MAX_ATTEMPTS=30"
    set "ATTEMPT=0"

    :check_pods
    set /a "ATTEMPT+=1"
    kubectl get pods -n %NAMESPACE% --no-headers | findstr /C:"Running" >nul
    if %ERRORLEVEL% EQU 0 (
        set "PODS_READY=1"
    ) else (
        if !ATTEMPT! LSS %MAX_ATTEMPTS% (
            call :log_info "Aguardando pods ficarem prontos (tentativa !ATTEMPT! de %MAX_RETRIES%)..."
            timeout /t 10 >nul
            goto check_pods
        )
    )

    if !PODS_READY! EQU 0 (
        call :log_error "Falha ao verificar status dos pods"
        exit /b 1
    )

    call :log_info "Todos os pods estão rodando!"
    exit /b 0 