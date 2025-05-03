# Script para instalar o Helm no Windows

# Verifica se o Chocolatey está instalado
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

# Instala o Helm usando Chocolatey
Write-Host "Instalando Helm..."
choco install kubernetes-helm -y

# Atualiza a variável de ambiente PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Adiciona os repositórios necessários
Write-Host "Adicionando repositórios do Helm..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

Write-Host "Instalação do Helm concluída!" 