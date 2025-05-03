@echo off
setlocal enabledelayedexpansion
set "NAMESPACE=autocura-cognitiva"
set "MAX_RETRIES=3"
set "TIMEOUT_SECONDS=60"

:log_info
echo [INFO] %~1
exit /b 0

:log_error
echo [ERRO] %~1
exit /b 1

:test_operators
    call :log_info "Testando operadores..."
    
    REM Verificar CRDs
    kubectl get crd healings.autocura-cognitiva.io
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "CRD de healing não encontrado"
        exit /b 1
    )
    
    kubectl get crd rollbacks.autocura-cognitiva.io
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "CRD de rollback não encontrado"
        exit /b 1
    )
    
    REM Verificar operadores
    set "RETRY_COUNT=0"
    :operator_retry
    kubectl get pods -n %NAMESPACE% -l app.kubernetes.io/name=healing-operator --no-headers | findstr /C:"Running"
    if %ERRORLEVEL% NEQ 0 (
        set /a "RETRY_COUNT+=1"
        if !RETRY_COUNT! LSS %MAX_RETRIES% (
            call :log_info "Aguardando healing-operator (tentativa !RETRY_COUNT! de %MAX_RETRIES%)..."
            timeout /t 10 >nul
            goto operator_retry
        )
        call :log_error "Healing operator não está rodando"
        exit /b 1
    )
    
    set "RETRY_COUNT=0"
    :rollback_retry
    kubectl get pods -n %NAMESPACE% -l app.kubernetes.io/name=rollback-operator --no-headers | findstr /C:"Running"
    if %ERRORLEVEL% NEQ 0 (
        set /a "RETRY_COUNT+=1"
        if !RETRY_COUNT! LSS %MAX_RETRIES% (
            call :log_info "Aguardando rollback-operator (tentativa !RETRY_COUNT! de %MAX_RETRIES%)..."
            timeout /t 10 >nul
            goto rollback_retry
        )
        call :log_error "Rollback operator não está rodando"
        exit /b 1
    )
    
    call :log_info "Operadores testados com sucesso"
    exit /b 0

:test_components
    call :log_info "Testando componentes..."
    
    REM Lista de componentes para testar
    set "COMPONENTS=diagnostico gerador-acoes observabilidade monitoramento"
    
    for %%c in (%COMPONENTS%) do (
        call :log_info "Testando componente %%c..."
        
        REM Verificar ServiceAccount
        kubectl get serviceaccount %%c -n %NAMESPACE%
        if %ERRORLEVEL% NEQ 0 (
            call :log_error "ServiceAccount do %%c não encontrado"
            exit /b 1
        )
        
        REM Verificar Role
        kubectl get role %%c-role -n %NAMESPACE%
        if %ERRORLEVEL% NEQ 0 (
            call :log_error "Role do %%c não encontrada"
            exit /b 1
        )
        
        REM Verificar RoleBinding
        kubectl get rolebinding %%c-rolebinding -n %NAMESPACE%
        if %ERRORLEVEL% NEQ 0 (
            call :log_error "RoleBinding do %%c não encontrado"
            exit /b 1
        )
        
        REM Verificar Pod
        set "RETRY_COUNT=0"
        :pod_retry
        kubectl get pods -n %NAMESPACE% -l app.kubernetes.io/name=%%c --no-headers | findstr /C:"Running"
        if %ERRORLEVEL% NEQ 0 (
            set /a "RETRY_COUNT+=1"
            if !RETRY_COUNT! LSS %MAX_RETRIES% (
                call :log_info "Aguardando pod do %%c (tentativa !RETRY_COUNT! de %MAX_RETRIES%)..."
                timeout /t 10 >nul
                goto pod_retry
            )
            call :log_error "Pod do %%c não está rodando"
            exit /b 1
        )
    )
    
    call :log_info "Componentes testados com sucesso"
    exit /b 0

:test_storage
    call :log_info "Testando armazenamento..."
    
    REM Verificar PVCs
    kubectl get pvc -n %NAMESPACE% | findstr "visualizacoes-pvc"
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "PVC de visualizações não encontrado"
        exit /b 1
    )
    
    call :log_info "Armazenamento testado com sucesso"
    exit /b 0

:test_monitoring
    call :log_info "Testando monitoramento..."
    
    REM Verificar Prometheus
    kubectl get pods -n %NAMESPACE% -l app.kubernetes.io/name=prometheus --no-headers | findstr /C:"Running"
    if %ERRORLEVEL% NEQ 0 (
        call :log_error "Prometheus não está rodando"
        exit /b 1
    )
    
    call :log_info "Monitoramento testado com sucesso"
    exit /b 0

REM Executar testes
call :test_operators
if %ERRORLEVEL% NEQ 0 exit /b 1

call :test_storage
if %ERRORLEVEL% NEQ 0 exit /b 1

call :test_monitoring
if %ERRORLEVEL% NEQ 0 exit /b 1

call :test_components
if %ERRORLEVEL% NEQ 0 exit /b 1

call :log_info "Todos os testes passaram com sucesso!"
exit /b 0 