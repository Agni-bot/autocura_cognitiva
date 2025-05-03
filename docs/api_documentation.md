# Documentação da API

## Visão Geral

A API do Sistema de Autocura Cognitiva fornece endpoints RESTful para interagir com todos os módulos do sistema. Esta documentação descreve os endpoints disponíveis, seus parâmetros e respostas.

## Autenticação

Todos os endpoints da API requerem autenticação. O sistema utiliza JWT (JSON Web Tokens) para autenticação.

### Obtendo um Token

```http
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=seu_usuario&password=sua_senha
```

Resposta:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

### Usando o Token

Inclua o token no cabeçalho de todas as requisições:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Endpoints

### Monitoramento

#### Listar Métricas
```http
GET /api/monitoramento/metrics
```

Parâmetros:
- `start_time` (opcional): Data/hora inicial
- `end_time` (opcional): Data/hora final
- `metric_names` (opcional): Lista de nomes de métricas

#### Obter Alertas
```http
GET /api/monitoramento/alerts
```

Parâmetros:
- `severity` (opcional): Severidade do alerta
- `status` (opcional): Status do alerta

### Diagnóstico

#### Listar Problemas
```http
GET /api/diagnostico/problems
```

Parâmetros:
- `status` (opcional): Status do problema
- `severity` (opcional): Severidade do problema

#### Iniciar Análise
```http
POST /api/diagnostico/analyze
```

Corpo:
```json
{
    "scope": ["componente1", "componente2"],
    "depth": "quick"
}
```

### Ações

#### Listar Ações Recomendadas
```http
GET /api/acoes/recommended
```

Parâmetros:
- `problem_id` (opcional): ID do problema relacionado

#### Executar Ação
```http
POST /api/acoes/execute/{action_id}
```

### Observabilidade

#### Obter Topologia
```http
GET /api/observabilidade/topology
```

Parâmetros:
- `depth` (opcional): Profundidade da análise (padrão: 2)

#### Obter Previsões
```http
GET /api/observabilidade/predictions/{metric_id}
```

Parâmetros:
- `horizon` (opcional): Horizonte de previsão (padrão: "1h")

## Respostas

Todas as respostas seguem o formato:

```json
{
    "status_code": 200,
    "message": "Success",
    "data": {},
    "timestamp": "2024-05-02T12:00:00Z"
}
```

## Códigos de Status

- 200: Sucesso
- 400: Requisição inválida
- 401: Não autorizado
- 403: Proibido
- 404: Não encontrado
- 500: Erro interno do servidor

## Limites de Taxa

- 100 requisições por minuto por IP
- 1000 requisições por hora por usuário

## Exemplos de Uso

### Python
```python
import requests

# Autenticação
response = requests.post(
    "http://api.exemplo.com/auth/token",
    data={"username": "usuario", "password": "senha"}
)
token = response.json()["access_token"]

# Requisição autenticada
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://api.exemplo.com/monitoramento/metrics",
    headers=headers
)
```

### cURL
```bash
# Autenticação
curl -X POST http://api.exemplo.com/auth/token \
  -d "username=usuario&password=senha"

# Requisição autenticada
curl -H "Authorization: Bearer $TOKEN" \
  http://api.exemplo.com/monitoramento/metrics
```

## Suporte

Para suporte técnico ou dúvidas sobre a API:
- Email: suporte@exemplo.com
- Documentação: https://docs.exemplo.com/api
- Fórum: https://forum.exemplo.com/api 