# Guia de Exportação

## Visão Geral

Este guia descreve o sistema de exportação de dados do Sistema de Autocura Cognitiva.

## Formatos de Exportação

### 1. CSV

#### Implementação
```python
def export_to_csv(data: list[dict], filename: str):
    """
    Exporta dados para CSV.
    
    Args:
        data: Dados a exportar
        filename: Nome do arquivo
    """
    # Cria DataFrame
    df = pd.DataFrame(data)
    
    # Exporta para CSV
    df.to_csv(
        filename,
        index=False,
        encoding='utf-8',
        quoting=csv.QUOTE_ALL
    )
```

### 2. JSON

#### Implementação
```python
def export_to_json(data: list[dict], filename: str):
    """
    Exporta dados para JSON.
    
    Args:
        data: Dados a exportar
        filename: Nome do arquivo
    """
    # Exporta para JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )
```

### 3. Excel

#### Implementação
```python
def export_to_excel(data: list[dict], filename: str):
    """
    Exporta dados para Excel.
    
    Args:
        data: Dados a exportar
        filename: Nome do arquivo
    """
    # Cria DataFrame
    df = pd.DataFrame(data)
    
    # Exporta para Excel
    df.to_excel(
        filename,
        index=False,
        engine='openpyxl'
    )
```

## Filtros

### 1. Implementação

```python
class ExportFilter:
    def __init__(self):
        self.start_date: datetime
        self.end_date: datetime
        self.types: list[str]
        self.status: list[str]
        self.users: list[str]
    
    def apply(self, data: list[dict]) -> list[dict]:
        """
        Aplica filtros aos dados.
        
        Args:
            data: Dados a filtrar
            
        Returns:
            list[dict]: Dados filtrados
        """
        filtered = data
        
        # Filtra por data
        if self.start_date:
            filtered = [
                d for d in filtered
                if d['timestamp'] >= self.start_date
            ]
        if self.end_date:
            filtered = [
                d for d in filtered
                if d['timestamp'] <= self.end_date
            ]
        
        # Filtra por tipo
        if self.types:
            filtered = [
                d for d in filtered
                if d['type'] in self.types
            ]
        
        # Filtra por status
        if self.status:
            filtered = [
                d for d in filtered
                if d['status'] in self.status
            ]
        
        # Filtra por usuário
        if self.users:
            filtered = [
                d for d in filtered
                if d['user_id'] in self.users
            ]
        
        return filtered
```

## Compressão

### 1. Implementação

```python
def compress_file(filename: str):
    """
    Comprime arquivo.
    
    Args:
        filename: Nome do arquivo
    """
    # Cria arquivo ZIP
    with zipfile.ZipFile(
        f"{filename}.zip",
        'w',
        zipfile.ZIP_DEFLATED
    ) as zipf:
        zipf.write(filename)
```

## Criptografia

### 1. Implementação

```python
def encrypt_file(filename: str, key: str):
    """
    Criptografa arquivo.
    
    Args:
        filename: Nome do arquivo
        key: Chave de criptografia
    """
    # Lê arquivo
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Criptografa dados
    cipher = Fernet(key)
    encrypted = cipher.encrypt(data)
    
    # Salva arquivo criptografado
    with open(f"{filename}.enc", 'wb') as f:
        f.write(encrypted)
```

## Armazenamento

### 1. S3

#### Implementação
```python
async def upload_to_s3(filename: str, bucket: str):
    """
    Upload para S3.
    
    Args:
        filename: Nome do arquivo
        bucket: Nome do bucket
    """
    # Configura cliente
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY
    )
    
    # Upload
    s3.upload_file(
        filename,
        bucket,
        os.path.basename(filename)
    )
```

### 2. Local

#### Implementação
```python
def save_local(filename: str, path: str):
    """
    Salva arquivo localmente.
    
    Args:
        filename: Nome do arquivo
        path: Caminho de destino
    """
    # Cria diretório se não existir
    os.makedirs(path, exist_ok=True)
    
    # Move arquivo
    shutil.move(
        filename,
        os.path.join(path, os.path.basename(filename))
    )
```

## Agendamento

### 1. Implementação

```python
async def schedule_export(filter: ExportFilter, schedule: str):
    """
    Agenda exportação.
    
    Args:
        filter: Filtros a aplicar
        schedule: Cron expression
    """
    # Cria job
    job = scheduler.add_job(
        export_data,
        'cron',
        **parse_cron(schedule),
        args=[filter]
    )
    
    return job.id
```

## Monitoramento

### 1. Métricas

#### Implementação
```python
from prometheus_client import Counter, Histogram

export_counter = Counter(
    'exports_total',
    'Total de exportações',
    ['format', 'status']
)

export_latency = Histogram(
    'export_processing_seconds',
    'Tempo de processamento de exportação',
    ['format']
)
```

### 2. Alertas

#### Configuração
```yaml
groups:
  - name: exports
    rules:
      - alert: HighExportFailureRate
        expr: rate(exports_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de falha em exportações"
          description: "Taxa de falha acima de 10% nos últimos 5 minutos"
```

## Troubleshooting

### 1. Problemas Comuns

#### Implementação
```python
def check_export_system():
    """
    Verifica sistema de exportação.
    """
    # Verifica permissões
    check_permissions()
    
    # Verifica espaço em disco
    check_disk_space()
    
    # Verifica conectividade
    check_connectivity()
```

### 2. Solução de Problemas

#### Implementação
```python
def troubleshoot_exports():
    """
    Soluciona problemas com exportações.
    """
    # Verifica configuração
    check_export_system()
    
    # Verifica métricas
    check_export_metrics()
    
    # Verifica logs
    check_export_logs()
``` 