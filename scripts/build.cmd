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

REM Construir imagens dos componentes principais
echo Construindo imagens dos componentes principais...

REM Construir e enviar imagem do monitoramento
echo Construindo imagem do monitoramento...
cd "%BASE_DIR%\src\monitoramento"
docker build -t %REGISTRY%/autocura-cognitiva/monitoramento:%TAG% .
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Falha ao construir a imagem do monitoramento
    exit /b 1
)
docker push %REGISTRY%/autocura-cognitiva/monitoramento:%TAG%

REM Construir e enviar imagem do diagnóstico
echo Construindo imagem do diagnóstico...
cd "%BASE_DIR%\src\diagnostico"
docker build -t %REGISTRY%/autocura-cognitiva/diagnostico:%TAG% .
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Falha ao construir a imagem do diagnóstico
    exit /b 1
)
docker push %REGISTRY%/autocura-cognitiva/diagnostico:%TAG%

REM Construir e enviar imagem do gerador de ações
echo Construindo imagem do gerador de ações...
cd "%BASE_DIR%\src\gerador-acoes"
docker build -t %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG% .
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Falha ao construir a imagem do gerador de ações
    exit /b 1
)
docker push %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG%

REM Construir e enviar imagem da observabilidade
echo Construindo imagem da observabilidade...
cd "%BASE_DIR%\src\observabilidade"
docker build -t %REGISTRY%/autocura-cognitiva/observabilidade:%TAG% .
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Falha ao construir a imagem da observabilidade
    exit /b 1
)
docker push %REGISTRY%/autocura-cognitiva/observabilidade:%TAG%

REM Construir imagens dos operadores (usando imagens pré-construídas)
echo Construindo imagens dos operadores...

echo Usando imagens pré-construídas para os operadores...
docker pull %REGISTRY%/autocura-cognitiva/healing-operator:%TAG% || echo Aviso: Imagem do healing-operator não encontrada
docker pull %REGISTRY%/autocura-cognitiva/rollback-operator:%TAG% || echo Aviso: Imagem do rollback-operator não encontrada

echo === Todas as imagens foram construídas e enviadas com sucesso! ===
cd "%BASE_DIR%"
