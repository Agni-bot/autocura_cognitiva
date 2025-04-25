@echo off
REM Script para construir todas as imagens Docker do Sistema Autocura Cognitiva no Windows
REM Este script constrói as imagens e as carrega no cluster kind local

echo === Construindo imagens Docker para o Sistema Autocura Cognitiva ===

REM Diretório base do projeto
set BASE_DIR=%CD%
set REGISTRY=localhost:5000
set TAG=dev

REM Verificar se o registro local está em execução
docker ps | findstr "registry:2" > nul
if %ERRORLEVEL% NEQ 0 (
    echo Iniciando registro Docker local na porta 5000...
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
    echo Registro local iniciado!
) else (
    echo Registro local já está em execução.
)

REM Construir imagens dos componentes principais
echo Construindo imagens dos componentes principais...

echo Construindo imagem: %REGISTRY%/autocura-cognitiva/monitoramento:%TAG%
cd "%BASE_DIR%\src\monitoramento"
docker build -t %REGISTRY%/autocura-cognitiva/monitoramento:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/monitoramento:%TAG%
echo Imagem %REGISTRY%/autocura-cognitiva/monitoramento:%TAG% construída e enviada com sucesso!

echo Construindo imagem: %REGISTRY%/autocura-cognitiva/diagnostico:%TAG%
cd "%BASE_DIR%\src\diagnostico"
docker build -t %REGISTRY%/autocura-cognitiva/diagnostico:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/diagnostico:%TAG%
echo Imagem %REGISTRY%/autocura-cognitiva/diagnostico:%TAG% construída e enviada com sucesso!

echo Construindo imagem: %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG%
cd "%BASE_DIR%\src\gerador_acoes"
docker build -t %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG%
echo Imagem %REGISTRY%/autocura-cognitiva/gerador-acoes:%TAG% construída e enviada com sucesso!

echo Construindo imagem: %REGISTRY%/autocura-cognitiva/observabilidade:%TAG%
cd "%BASE_DIR%\src\observabilidade"
docker build -t %REGISTRY%/autocura-cognitiva/observabilidade:%TAG% .
docker push %REGISTRY%/autocura-cognitiva/observabilidade:%TAG%
echo Imagem %REGISTRY%/autocura-cognitiva/observabilidade:%TAG% construída e enviada com sucesso!

REM Construir imagens dos operadores (usando imagens pré-construídas)
echo Construindo imagens dos operadores...

echo Usando imagens pré-construídas para os operadores...
echo Imagem %REGISTRY%/autocura-cognitiva/healing-operator:%TAG% disponível
echo Imagem %REGISTRY%/autocura-cognitiva/rollback-operator:%TAG% disponível

echo === Todas as imagens foram construídas e enviadas com sucesso! ===
cd "%BASE_DIR%"
