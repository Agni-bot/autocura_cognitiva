# Rollback Operator - Configuração Local

Este operador foi ajustado para desenvolvimento local, sem dependências de repositórios remotos do GitHub.

## Ajustes Realizados

- O arquivo `go.mod` foi alterado para:
  ```
  module rollback-operator
  ```
- Todos os imports internos foram atualizados para:
  - `rollback-operator/api/v1`
  - `rollback-operator/controller`

Isso permite rodar `go mod tidy`, buildar e gerar a imagem Docker sem dependências externas inexistentes.

## Passos para Desenvolver Localmente

1. No diretório do operador, execute:
   ```sh
   go mod tidy
   ```
2. Para buildar a imagem Docker:
   ```sh
   docker build -t localhost:5000/autocura-cognitiva/rollback-operator:latest .
   ```
3. Para enviar ao registro local:
   ```sh
   docker push localhost:5000/autocura-cognitiva/rollback-operator:latest
   ```

## Referência

Para mais detalhes sobre a arquitetura, configuração e integração, consulte a pasta [`docs`](../../../../docs) do projeto. 