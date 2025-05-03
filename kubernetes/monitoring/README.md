# Monitoramento com Prometheus e Grafana

Este diretório contém os arquivos de configuração para implantar um stack de monitoramento usando Prometheus e Grafana no Kubernetes.

## Pré-requisitos

- Kubernetes cluster
- kubectl configurado
- kustomize instalado

## Instalação

Para aplicar todos os recursos, execute o seguinte comando:

```bash
kubectl apply -k .
```

## Acessando as interfaces

### Grafana
- URL: https://grafana.example.com
- Usuário: admin
- Senha: admin123

### Prometheus
- URL: https://prometheus.example.com

### Alertmanager
- URL: https://alertmanager.example.com

## Configuração

### Prometheus
O Prometheus está configurado para coletar métricas de:
- Kubernetes API server
- Kubernetes nodes
- Kubernetes pods
- Node Exporter (métricas do sistema operacional)
- Serviços com anotações prometheus.io/scrape=true

### Grafana
O Grafana está configurado com:
- Fonte de dados do Prometheus
- Painéis básicos para visualização de métricas
- Credenciais seguras armazenadas como secrets

### Alertmanager
O Alertmanager é responsável por gerenciar alertas enviados pelo Prometheus, incluindo:
- Agrupamento de alertas
- Inibição de alertas
- Silenciamento de alertas
- Encaminhamento de alertas para diferentes canais (webhook)

## Segurança

- Todas as conexões são forçadas a usar HTTPS através dos ingress
- Credenciais do Grafana são armazenadas como secrets
- O Prometheus tem permissões limitadas através de RBAC
- O Node Exporter tem acesso somente leitura aos recursos do sistema
- O Alertmanager tem configurações de segurança para webhooks

## Manutenção

Para atualizar as configurações:

1. Modifique os arquivos YAML conforme necessário
2. Aplique as alterações:
   ```bash
   kubectl apply -k .
   ```

Para remover todos os recursos:

```bash
kubectl delete -k .
``` 