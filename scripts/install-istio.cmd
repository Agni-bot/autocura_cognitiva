@echo off
REM Script para instalar o Istio CLI no Windows

echo === Instalando Istio CLI ===

REM Verificar se o curl está instalado
where curl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo curl não está instalado. Por favor, instale-o primeiro.
    exit /b 1
)

REM Criar diretório temporário
set "TEMP_DIR=%TEMP%\istio-install"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Baixar Istio CLI
echo Baixando Istio CLI...
curl -L https://github.com/istio/istio/releases/download/1.18.0/istio-1.18.0-win.zip -o "%TEMP_DIR%\istio.zip"

REM Extrair arquivos
echo Extraindo arquivos...
powershell -Command "Expand-Archive -Path '%TEMP_DIR%\istio.zip' -DestinationPath '%TEMP_DIR%' -Force"

REM Mover istioctl para o PATH
echo Instalando istioctl...
copy "%TEMP_DIR%\istio-1.18.0\bin\istioctl.exe" "%SystemRoot%\System32\"

REM Limpar arquivos temporários
echo Limpando arquivos temporários...
rmdir /s /q "%TEMP_DIR%"

echo === Istio CLI instalado com sucesso! ===
echo Execute 'istioctl version' para verificar a instalação. 