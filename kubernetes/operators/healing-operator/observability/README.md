# Módulos de Observabilidade

O projeto possui dois módulos de observabilidade distintos:

## 1. Módulo de Observabilidade 4D (observability/)

Este módulo implementa a interface visual 4D com as seguintes funcionalidades:
- Visualização holográfica do cluster
- Projeção temporal de métricas
- Interface adaptativa
- Controle interativo

### Estrutura
```
observability/
├── main.go              # Servidor WebSocket e coleta de métricas
├── web/                 # Interface web
│   └── index.html       # Interface 4D
├── Dockerfile           # Configuração do container
└── k8s/                 # Configurações Kubernetes
    └── deployment.yaml  # Implantação do módulo
```

## 2. Módulo de Observabilidade do Operador (kubernetes/observability/)

Este módulo implementa a coleta de métricas e monitoramento do operador Healing:
- Coleta de métricas do cluster
- Monitoramento de recursos
- Detecção de anomalias
- Integração com o operador Healing

### Estrutura
```
kubernetes/observability/
├── metrics/             # Coletores de métricas
├── alerts/              # Regras de alerta
└── dashboards/          # Painéis de monitoramento
```

## Diferenças Principais

1. **Propósito**:
   - Observabilidade 4D: Interface visual interativa para operadores humanos
   - Observabilidade do Operador: Coleta e análise automática de métricas

2. **Funcionalidades**:
   - Observabilidade 4D: Visualização 3D, projeção temporal, interface adaptativa
   - Observabilidade do Operador: Coleta de métricas, alertas, dashboards

3. **Usuários**:
   - Observabilidade 4D: Operadores humanos
   - Observabilidade do Operador: Sistema de autocura

4. **Integração**:
   - Observabilidade 4D: Consome métricas do módulo de observabilidade do operador
   - Observabilidade do Operador: Fornece métricas para o módulo 4D e para o operador Healing

## Implantação

Para implantar ambos os módulos:

1. Implantar o módulo de observabilidade do operador:
```bash
kubectl apply -f kubernetes/observability/
```

2. Implantar o módulo de observabilidade 4D:
```bash
cd observability
./setup-observability.cmd
```

3. Acessar a interface 4D:
```bash
kubectl port-forward -n healing-operator-system service/healing-observability 8080:80
```
Acesse http://localhost:8080 