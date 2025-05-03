@echo off
setlocal enabledelayedexpansion

:: Configurações
set "KIND_CLUSTER_NAME=autocura-cognitiva"

:: Menu principal
:menu
cls
echo ==========================================
echo Ferramentas de Análise - Autocura Cognitiva
echo ==========================================
echo [1] Visão Geral do Cluster
echo [2] Análise de Pods Problemáticos
echo [3] Ver Logs de Pods
echo [4] Verificar Eventos do Cluster
echo [5] Verificar Configurações
echo [0] Sair
echo ==========================================
set /p op=Escolha uma opção: 

if "%op%"=="1" goto OVERVIEW
if "%op%"=="2" goto PROBLEM_ANALYSIS
if "%op%"=="3" goto LOGS
if "%op%"=="4" goto EVENTS
if "%op%"=="5" goto CONFIG
if "%op%"=="0" exit /b 0
goto menu

:OVERVIEW
echo ===== VISÃO GERAL DO CLUSTER =====
echo.
echo === NODES ===
kubectl get nodes
echo.
echo === PODS ===
kubectl get pods -A -o wide
echo.
echo === SERVICES ===
kubectl get svc -A
pause
goto menu

:PROBLEM_ANALYSIS
echo ===== ANÁLISE DE PODS PROBLEMÁTICOS =====
echo.
echo === Pods com ImagePullBackOff ===
kubectl get pods -A --field-selector=status.phase=ImagePullBackOff -o wide
echo.
echo === Pods em Pending ===
kubectl get pods -A --field-selector=status.phase=Pending -o wide
echo.
echo === Pods com múltiplos restarts ===
kubectl get pods -A --field-selector=status.phase=Running -o wide | findstr "2/1"
echo.
echo === Descrevendo pods problemáticos ===
for /f "tokens=1,2" %%a in ('kubectl get pods -A --field-selector=status.phase!=Running -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name --no-headers') do (
    echo.
    echo === Descrevendo pod %%b no namespace %%a ===
    kubectl describe pod %%b -n %%a
)
pause
goto menu

:LOGS
echo ===== LOGS DE PODS =====
echo.
echo Lista de pods:
kubectl get pods -A
echo.
set /p pod=Digite o nome do pod para ver os logs (ou deixe em branco para voltar): 
if "%pod%"=="" goto menu
set /p namespace=Digite o namespace do pod: 
echo.
echo === Logs do pod %pod% ===
kubectl logs %pod% -n %namespace%
pause
goto menu

:EVENTS
echo ===== EVENTOS DO CLUSTER =====
echo.
echo Eventos ordenados por timestamp:
kubectl get events -A --sort-by='.lastTimestamp'
pause
goto menu

:CONFIG
echo ===== CONFIGURAÇÕES =====
echo.
echo === ConfigMaps ===
kubectl get configmaps -A
echo.
echo === Secrets ===
kubectl get secrets -A
echo.
echo === PersistentVolumeClaims ===
kubectl get pvc -A
pause
goto menu 