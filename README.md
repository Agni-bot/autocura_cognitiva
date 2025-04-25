# Sistema de Autocura Cognitiva

Este repositório contém o Sistema de Autocura Cognitiva, uma solução avançada para manutenção autônoma de sistemas de Inteligência Artificial.

## Visão Geral

O Sistema de Autocura Cognitiva representa uma evolução significativa na manutenção autônoma de sistemas de IA. Diferentemente dos sistemas tradicionais de monitoramento e recuperação, este sistema incorpora princípios de cognição adaptativa, permitindo não apenas identificar e corrigir falhas, mas também evoluir continuamente para prevenir problemas futuros.

## Pré-requisitos

Para executar o Sistema de Autocura Cognitiva localmente, você precisará ter instalado:

- Docker
- kubectl
- kind (Kubernetes in Docker)

## Configuração do Ambiente Local

Siga estas etapas para configurar e executar o Sistema de Autocura Cognitiva em seu ambiente local:

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/autocura-cognitiva.git
cd autocura-cognitiva
```

### 2. Configure o ambiente Kubernetes local

Execute o script de configuração do ambiente para criar um cluster kind configurado para o Sistema de Autocura Cognitiva:

```bash
# Torne o script executável
chmod +x setup-kind.sh

# Execute o script
./setup-kind.sh
```

Este script irá:
- Verificar os pré-requisitos (Docker, kubectl, kind)
- Criar um cluster kind com a configuração necessária
- Configurar um registro Docker local
- Conectar o registro à rede do kind

### 3. Construa as imagens Docker

Execute o script de build para construir todas as imagens Docker necessárias:

```bash
# Torne o script executável
chmod +x build.sh

# Execute o script
./build.sh
```

Este script irá:
- Construir as imagens Docker para todos os componentes (monitoramento, diagnóstico, gerador de ações, observabilidade)
- Construir as imagens Docker para os operadores (healing, rollback)
- Enviar as imagens para o registro local

### 4. Implante o sistema no cluster

Implante o Sistema de Autocura Cognitiva no cluster kind:

```bash
# Implante o ambiente de desenvolvimento
kubectl apply -k kubernetes/environments/development
```

### 5. Verifique a implantação

Verifique se todos os componentes foram implantados corretamente:

```bash
# Verifique os pods
kubectl get pods -n autocura-cognitiva-dev

# Verifique os serviços
kubectl get services -n autocura-cognitiva-dev
```

### 6. Acesse o painel de observabilidade

O painel de observabilidade está disponível através do serviço de observabilidade:

```bash
# Encaminhe a porta do serviço de observabilidade
kubectl port-forward -n autocura-cognitiva-dev svc/observabilidade 8080:8080
```

Acesse o painel em seu navegador: http://localhost:8080

## Estrutura do Projeto

```
autocura_cognitiva/
├── src/                      # Código-fonte dos componentes
│   ├── monitoramento/        # Módulo de Monitoramento Multidimensional
│   ├── diagnostico/          # Módulo de Diagnóstico Neural
│   ├── gerador_acoes/        # Gerador de Ações Emergentes
│   ├── observabilidade/      # Interface de Observabilidade 4D
│   └── integracao/           # Módulos de integração
├── kubernetes/               # Configurações de implantação
│   ├── base/                 # Recursos base
│   ├── operators/            # Operadores customizados
│   ├── components/           # Componentes do sistema
│   ├── environments/         # Ambientes paralelos
│   └── storage/              # Configurações de armazenamento
├── docs/                     # Documentação
├── tests/                    # Testes
└── config/                   # Configurações
```

## Solução de Problemas

### Erro ImagePullBackOff

Se você encontrar erros de ImagePullBackOff:

1. Verifique se o registro local está em execução:
   ```bash
   docker ps | grep registry
   ```

2. Verifique se as imagens foram construídas e enviadas corretamente:
   ```bash
   docker images | grep autocura-cognitiva
   ```

3. Verifique se o cluster kind está configurado para acessar o registro local:
   ```bash
   kubectl get nodes -o wide
   ```

4. Reconstrua as imagens e reimplante o sistema:
   ```bash
   ./build.sh
   kubectl delete -k kubernetes/environments/development
   kubectl apply -k kubernetes/environments/development
   ```

## Documentação Adicional

Para mais informações, consulte os documentos na pasta `docs/`:

- [Análise de Requisitos](docs/analise_requisitos.md)
- [Arquitetura Modular](docs/arquitetura_modular.md)
- [Plano de Implantação](docs/plano_implantacao.md)
- [Protocolo de Emergência](docs/protocolo_emergencia.md)
- [Documentação Completa](docs/documentacao_completa.md)

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
