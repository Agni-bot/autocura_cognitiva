# Guia de Instalação e Configuração

## Requisitos do Sistema

### Hardware Mínimo

- CPU: 4 núcleos
- RAM: 16GB
- Armazenamento: 100GB SSD
- Rede: 1Gbps

### Software

- Sistema Operacional:
  - Ubuntu 20.04 LTS ou superior
  - CentOS 8 ou superior
  - Windows Server 2019 ou superior

- Dependências:
  - Python 3.8+
  - Docker 20.10+
  - Docker Compose 2.0+
  - PostgreSQL 13+
  - Redis 6.0+

## Instalação

### 1. Preparação do Ambiente

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3-pip python3-venv git curl

# Instalar Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clonar o Repositório

```bash
git clone https://github.com/exemplo/autocura-cognitiva.git
cd autocura-cognitiva
```

### 3. Configurar Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
# Configurações do Sistema
APP_ENV=production
DEBUG=False
SECRET_KEY=sua_chave_secreta

# Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=autocura
DB_USER=usuario
DB_PASSWORD=senha

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=senha_redis

# API Keys
OPENAI_API_KEY=sua_chave_openai
PROMETHEUS_API_KEY=sua_chave_prometheus
```

### 5. Inicializar Banco de Dados

```bash
# Criar banco de dados
sudo -u postgres psql -c "CREATE DATABASE autocura;"
sudo -u postgres psql -c "CREATE USER usuario WITH PASSWORD 'senha';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE autocura TO usuario;"

# Executar migrações
python manage.py migrate
```

### 6. Iniciar Serviços

```bash
# Iniciar containers Docker
docker-compose up -d

# Iniciar aplicação
python manage.py runserver
```

## Configuração Pós-Instalação

### 1. Configurar Monitoramento

1. Acesse o painel administrativo
2. Vá para "Configurações > Monitoramento"
3. Configure:
   - Endpoints do Prometheus
   - Métricas a serem coletadas
   - Intervalos de coleta

### 2. Configurar Alertas

1. Acesse "Configurações > Alertas"
2. Configure:
   - Regras de alerta
   - Destinatários
   - Canais de notificação
   - Limiares

### 3. Configurar Diagnóstico

1. Vá para "Configurações > Diagnóstico"
2. Configure:
   - Regras de análise
   - Profundidade padrão
   - Componentes a monitorar

### 4. Configurar Ações

1. Acesse "Configurações > Ações"
2. Configure:
   - Ações disponíveis
   - Permissões
   - Agendamentos

## Verificação da Instalação

### Testes Básicos

```bash
# Verificar status dos containers
docker-compose ps

# Testar conexão com banco
python manage.py check_db

# Verificar logs
docker-compose logs -f
```

### Testes Avançados

```bash
# Executar testes unitários
python manage.py test

# Verificar cobertura
coverage run manage.py test
coverage report
```

## Manutenção

### Backup

Configure backup automático:

```bash
# Criar script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup do banco
pg_dump -U usuario autocura > $BACKUP_DIR/db.sql

# Backup de configurações
tar -czf $BACKUP_DIR/config.tar.gz /etc/autocura

# Backup de logs
tar -czf $BACKUP_DIR/logs.tar.gz /var/log/autocura
EOF

# Agendar backup diário
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

### Atualização

```bash
# Atualizar código
git pull origin main

# Atualizar dependências
pip install -r requirements.txt

# Executar migrações
python manage.py migrate

# Reiniciar serviços
docker-compose down
docker-compose up -d
```

## Solução de Problemas

### Logs

Principais locais de logs:
- `/var/log/autocura/app.log`
- `/var/log/autocura/error.log`
- `docker-compose logs -f`

### Problemas Comuns

1. **Banco de Dados não Conecta**
   - Verificar credenciais no `.env`
   - Confirmar se PostgreSQL está rodando
   - Checar permissões do usuário

2. **Serviços Docker não Iniciam**
   - Verificar memória disponível
   - Checar conflitos de portas
   - Verificar logs do Docker

3. **Aplicação não Responde**
   - Verificar logs da aplicação
   - Confirmar se Redis está rodando
   - Checar uso de CPU/memória

## Suporte

Para suporte técnico:
- Email: suporte@exemplo.com
- Telefone: (11) 1234-5678
- Documentação: https://docs.exemplo.com 