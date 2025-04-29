#!/bin/bash

# Script para construir todas as imagens Docker do Sistema Autocura Cognitiva
# Este script constrói as imagens e as carrega no cluster kind local

set -e

echo "=== Construindo imagens Docker para o Sistema Autocura Cognitiva ==="

# Diretório base do projeto
BASE_DIR=$(pwd)
REGISTRY="localhost:5000"
TAG="dev"

# Função para construir e carregar uma imagem
build_and_load() {
    local component=$1
    local dir=$2
    local image_name="${REGISTRY}/autocura-cognitiva/${component}:${TAG}"
    
    echo "Construindo imagem: ${image_name}"
    cd "${BASE_DIR}/${dir}"
    docker build -t "${image_name}" .
    
    echo "Enviando imagem para o registro local: ${image_name}"
    docker push "${image_name}"
    
    echo "Imagem ${image_name} construída e enviada com sucesso!"
    echo ""
}

# Verificar se o registro local está em execução
if ! docker ps | grep -q registry:2; then
    echo "Iniciando registro Docker local na porta 5000..."
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
    echo "Registro local iniciado!"
else
    echo "Registro local já está em execução."
fi

# Construir imagens dos componentes principais
echo "Construindo imagens dos componentes principais..."
build_and_load "monitoramento" "src/monitoramento"
build_and_load "diagnostico" "src/diagnostico"
build_and_load "gerador-acoes" "src/gerador_acoes"
build_and_load "observabilidade" "src/observabilidade"

# Construir imagens dos operadores
echo "Construindo imagens dos operadores..."
build_and_load "healing-operator" "kubernetes/operators/healing-operator"
build_and_load "rollback-operator" "kubernetes/operators/rollback-operator"

echo "=== Todas as imagens foram construídas e enviadas com sucesso! ==="
