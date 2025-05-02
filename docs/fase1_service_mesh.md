# Fase 1: Service Mesh e Circuit Breaker

## Visão Geral
Esta fase implementa o Service Mesh usando Istio e configura o Circuit Breaker para garantir resiliência na comunicação entre os serviços.

## Estrutura de Diretórios
```
kubernetes/
└── istio/
    ├── circuit-breaker.yaml    # Configuração do Circuit Breaker
    ├── mtls.yaml              # Configuração de mTLS
    └── traffic-policy.yaml     # Políticas de tráfego
```

## Configurações Implementadas

### 1. Circuit Breaker (`circuit-breaker.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: autocura-cognitiva-circuit-breaker
  namespace: autocura-cognitiva
spec:
  host: "*.autocura-cognitiva.svc.cluster.local"
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1024
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 10
```

**Parâmetros Configurados:**
- `maxConnections`: Limite de 100 conexões TCP simultâneas
- `http1MaxPendingRequests`: Máximo de 1024 requisições HTTP pendentes
- `maxRequestsPerConnection`: 10 requisições por conexão
- `consecutive5xxErrors`: 5 erros consecutivos para ativar o Circuit Breaker
- `interval`: Verificação a cada 30 segundos
- `baseEjectionTime`: 30 segundos de ejeção base
- `maxEjectionPercent`: 10% de serviços podem ser ejetados

### 2. mTLS (`mtls.yaml`)
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: autocura-cognitiva-mtls
  namespace: autocura-cognitiva
spec:
  mtls:
    mode: STRICT
```

**Configurações:**
- Modo STRICT: Todas as comunicações entre serviços devem usar mTLS
- Aplicado em todo o namespace `autocura-cognitiva`

### 3. Políticas de Tráfego (`traffic-policy.yaml`)
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: autocura-cognitiva-traffic
  namespace: autocura-cognitiva
spec:
  hosts:
  - "*"
  gateways:
  - istio-ingressgateway
  http:
  - match:
    - uri:
        prefix: /monitoramento
    route:
    - destination:
        host: monitoramento
        port:
          number: 8080
  - match:
    - uri:
        prefix: /diagnostico
    route:
    - destination:
        host: diagnostico
        port:
          number: 8081
  - match:
    - uri:
        prefix: /gerador-acoes
    route:
    - destination:
        host: gerador-acoes
        port:
          number: 8082
  - match:
    - uri:
        prefix: /observabilidade
    route:
    - destination:
        host: observabilidade
        port:
          number: 5000
```

**Rotas Configuradas:**
- `/monitoramento` → Serviço monitoramento (porta 8080)
- `/diagnostico` → Serviço diagnóstico (porta 8081)
- `/gerador-acoes` → Serviço gerador de ações (porta 8082)
- `/observabilidade` → Serviço de observabilidade (porta 5000)

## Scripts de Instalação

### Instalação do Istio CLI (`scripts/install-istio.cmd`)
```batch
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
```

## Comandos de Implantação

1. Criar namespace e habilitar injeção do Istio:
```bash
kubectl create namespace autocura-cognitiva
kubectl label namespace autocura-cognitiva istio-injection=enabled
```

2. Instalar Istio:
```bash
istioctl install --set profile=default -y
```

3. Aplicar configurações:
```bash
kubectl apply -f kubernetes/istio/
```

## Próximos Passos
1. Monitorar métricas do Service Mesh
2. Implementar testes de resiliência
3. Documentar procedimentos de troubleshooting
4. Preparar para a Fase 2 (Bulkhead e Isolamento) 