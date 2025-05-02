# Script para iniciar o servidor de observabilidade
Write-Host "Iniciando o servidor de observabilidade..."

# Verificar se o Go está instalado
$goPath = "C:\Program Files\Go\bin\go.exe"
if (-not (Test-Path $goPath)) {
    Write-Host "Go não encontrado em $goPath"
    Write-Host "Por favor, instale o Go e adicione-o ao PATH do sistema"
    exit 1
}

# Navegar para o diretório do projeto
Set-Location $PSScriptRoot

# Iniciar o servidor
& $goPath run main.go 