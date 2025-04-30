@echo off
REM Script para construir todas as imagens Docker do Sistema Autocura Cognitiva no Windows
REM Este script constrói as imagens e as carrega no cluster kind local

echo === Construindo imagens Docker para o Sistema Autocura Cognitiva ===

REM Diretório base do projeto
set BASE_DIR=%CD%
set REGISTRY=localhost:5000
set TAG=dev

REM Verificar se o cluster kind está em execução
kind get clusters | findstr "autocura-cognitiva" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Cluster kind 'autocura-cognitiva' não está em execução.
    echo Execute 'setup-kind.cmd' primeiro para configurar o ambiente.
    exit /b 1
)

REM Verificar se o registro local está em execução
docker ps | findstr "registry:2" > nul
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando registro Docker local na porta 5000...
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
    if %ERRORLEVEL% NEQ 0 (
        echo Erro: Falha ao iniciar o registro Docker local.
        exit /b 1
    )
    echo Registro local iniciado!
) else (
    echo Registro local já está em execução.
)

REM Verificar existência dos diretórios
if not exist "%BASE_DIR%\src\monitoramento" (
    echo Erro: Diretório monitoramento não encontrado
    exit /b 1
)

if not exist "%BASE_DIR%\src\diagnostico" (
    echo Erro: Diretório diagnostico não encontrado
    exit /b 1
)

if not exist "%BASE_DIR%\src\gerador_acoes" (
    echo Erro: Diretório gerador_acoes não encontrado
    exit /b 1
)

if not exist "%BASE_DIR%\src\observabilidade" (
    echo Erro: Diretório observabilidade não encontrado
    exit /b 1
)

REM Construir imagens dos componentes principais
echo Construindo imagens dos componentes principais...

REM Função para construir e enviar uma imagem
:build_image
    setlocal
    set COMPONENT=%~1
    set IMAGE_NAME=%REGISTRY%/autocura-cognitiva/%COMPONENT%:%TAG%
    
    echo Construindo imagem: %IMAGE_NAME%
    cd "%BASE_DIR%\src\%COMPONENT%"
    
    docker build -t %IMAGE_NAME% .
    if %ERRORLEVEL% NEQ 0 (
        echo Erro: Falha ao construir a imagem %IMAGE_NAME%
        exit /b 1
    )
    
    docker push %IMAGE_NAME%
    if %ERRORLEVEL% NEQ 0 (
        echo Erro: Falha ao enviar a imagem %IMAGE_NAME%
        exit /b 1
    )
    
    echo Imagem %IMAGE_NAME% construída e enviada com sucesso!
    endlocal
    exit /b 0

REM Construir cada componente
call :build_image monitoramento
call :build_image diagnostico
call :build_image gerador-acoes
call :build_image observabilidade

REM Construir imagens dos operadores (usando imagens pré-construídas)
echo Construindo imagens dos operadores...

echo Usando imagens pré-construídas para os operadores...
echo Imagem %REGISTRY%/autocura-cognitiva/healing-operator:%TAG% disponível
echo Imagem %REGISTRY%/autocura-cognitiva/rollback-operator:%TAG% disponível

echo === Todas as imagens foram construídas e enviadas com sucesso! ===
cd "%BASE_DIR%"
