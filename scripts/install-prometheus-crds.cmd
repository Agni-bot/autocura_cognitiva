@echo off
setlocal enabledelayedexpansion

echo [INFO] Instalando CRDs do Prometheus Operator...

kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.68.0/bundle.yaml

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao instalar CRDs do Prometheus Operator
    exit /b 1
)

echo [INFO] CRDs do Prometheus Operator instalados com sucesso
exit /b 0 