# Guia de Configuração

## Visão Geral

Este guia descreve as configurações disponíveis no Sistema de Autocura Cognitiva.

## Configurações do Sistema

### 1. Configurações Gerais

#### Estrutura
```json
{
    "system": {
        "name": "Autocura Cognitiva",
        "version": "1.0.0",
        "environment": "production",
        "timezone": "America/Sao_Paulo",
        "language": "pt_BR"
    }
}
```

#### Implementação
```python
from pydantic import BaseSettings

class SystemSettings(BaseSettings):
    name: str
    version: str
    environment: str
    timezone: str
    language: str
    
    class Config:
        env_prefix = "SYSTEM_"
```

### 2. Configurações de Banco de Dados

#### MongoDB
```python
class DatabaseSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    database: str
    
    class Config:
        env_prefix = "DB_"
```

#### Redis
```python
class CacheSettings(BaseSettings):
    host: str
    port: int
    password: str
    db: int
    
    class Config:
        env_prefix = "REDIS_"
```

### 3. Configurações de API

#### FastAPI
```python
class APISettings(BaseSettings):
    title: str
    description: str
    version: str
    docs_url: str
    redoc_url: str
    
    class Config:
        env_prefix = "API_"
```

#### CORS
```python
class CORSSettings(BaseSettings):
    allow_origins: list[str]
    allow_methods: list[str]
    allow_headers: list[str]
    allow_credentials: bool
    
    class Config:
        env_prefix = "CORS_"
```

## Configurações de Usuário

### 1. Perfil

#### Estrutura
```json
{
    "profile": {
        "name": "João Silva",
        "email": "joao@exemplo.com",
        "role": "admin",
        "preferences": {
            "notifications": true,
            "theme": "dark",
            "language": "pt_BR"
        }
    }
}
```

#### Implementação
```python
class UserProfile(BaseModel):
    name: str
    email: str
    role: str
    preferences: dict
```

### 2. Preferências

#### Notificações
```python
class NotificationPreferences(BaseModel):
    email: bool
    push: bool
    sms: bool
    frequency: str
    channels: list[str]
```

#### Interface
```python
class InterfacePreferences(BaseModel):
    theme: str
    language: str
    timezone: str
    date_format: str
    time_format: str
```

## Configurações de Segurança

### 1. Autenticação

#### JWT
```python
class JWTSettings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    
    class Config:
        env_prefix = "JWT_"
```

#### OAuth
```python
class OAuthSettings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    facebook_client_id: str
    facebook_client_secret: str
    
    class Config:
        env_prefix = "OAUTH_"
```

### 2. Criptografia

#### Chaves
```python
class EncryptionSettings(BaseSettings):
    key: str
    algorithm: str
    salt: str
    
    class Config:
        env_prefix = "ENCRYPTION_"
```

## Configurações de Monitoramento

### 1. Logs

#### Estrutura
```python
class LogSettings(BaseSettings):
    level: str
    format: str
    file: str
    max_size: int
    backup_count: int
    
    class Config:
        env_prefix = "LOG_"
```

### 2. Métricas

#### Prometheus
```python
class MetricsSettings(BaseSettings):
    enabled: bool
    port: int
    path: str
    
    class Config:
        env_prefix = "METRICS_"
```

## Configurações de Notificações

### 1. Email

#### SMTP
```python
class EmailSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    from_email: str
    tls: bool
    
    class Config:
        env_prefix = "EMAIL_"
```

### 2. Push

#### Firebase
```python
class PushSettings(BaseSettings):
    project_id: str
    private_key: str
    client_email: str
    
    class Config:
        env_prefix = "PUSH_"
```

## Configurações de Exportação

### 1. Formatos

#### Estrutura
```python
class ExportSettings(BaseSettings):
    formats: list[str]
    compression: bool
    encryption: bool
    max_size: int
    
    class Config:
        env_prefix = "EXPORT_"
```

### 2. Armazenamento

#### S3
```python
class StorageSettings(BaseSettings):
    bucket: str
    region: str
    access_key: str
    secret_key: str
    
    class Config:
        env_prefix = "STORAGE_"
```

## Configurações de Relatórios

### 1. Agendamento

#### Estrutura
```python
class ReportSettings(BaseSettings):
    schedule: str
    format: str
    recipients: list[str]
    retention_days: int
    
    class Config:
        env_prefix = "REPORT_"
```

### 2. Templates

#### Implementação
```python
class TemplateSettings(BaseSettings):
    path: str
    default: str
    custom: list[str]
    
    class Config:
        env_prefix = "TEMPLATE_"
```

## Configurações de Dashboard

### 1. Layout

#### Estrutura
```python
class DashboardSettings(BaseSettings):
    default_layout: dict
    widgets: list[str]
    refresh_interval: int
    
    class Config:
        env_prefix = "DASHBOARD_"
```

### 2. Widgets

#### Implementação
```python
class WidgetSettings(BaseSettings):
    enabled: list[str]
    position: dict
    size: dict
    
    class Config:
        env_prefix = "WIDGET_"
```

## Gerenciamento de Configurações

### 1. Carregamento

#### Implementação
```python
def load_settings():
    """
    Carrega todas as configurações do sistema.
    
    Returns:
        dict: Configurações carregadas
    """
    settings = {}
    
    # Carrega configurações do ambiente
    settings['system'] = SystemSettings()
    settings['database'] = DatabaseSettings()
    settings['api'] = APISettings()
    settings['cors'] = CORSSettings()
    settings['jwt'] = JWTSettings()
    settings['oauth'] = OAuthSettings()
    settings['encryption'] = EncryptionSettings()
    settings['log'] = LogSettings()
    settings['metrics'] = MetricsSettings()
    settings['email'] = EmailSettings()
    settings['push'] = PushSettings()
    settings['export'] = ExportSettings()
    settings['storage'] = StorageSettings()
    settings['report'] = ReportSettings()
    settings['template'] = TemplateSettings()
    settings['dashboard'] = DashboardSettings()
    settings['widget'] = WidgetSettings()
    
    return settings
```

### 2. Atualização

#### Implementação
```python
async def update_settings(settings: dict):
    """
    Atualiza as configurações do sistema.
    
    Args:
        settings: Novas configurações
        
    Returns:
        dict: Configurações atualizadas
    """
    # Valida configurações
    validate_settings(settings)
    
    # Atualiza no banco
    await db.settings.update_one(
        {'_id': 'system'},
        {'$set': settings},
        upsert=True
    )
    
    # Atualiza cache
    await cache.set('settings', settings)
    
    return settings
```

### 3. Validação

#### Implementação
```python
def validate_settings(settings: dict):
    """
    Valida as configurações do sistema.
    
    Args:
        settings: Configurações a validar
        
    Raises:
        ValidationError: Se as configurações forem inválidas
    """
    # Valida estrutura
    if not isinstance(settings, dict):
        raise ValidationError("Configurações devem ser um dicionário")
    
    # Valida campos obrigatórios
    required_fields = [
        'system',
        'database',
        'api',
        'jwt'
    ]
    
    for field in required_fields:
        if field not in settings:
            raise ValidationError(f"Campo obrigatório ausente: {field}")
    
    # Valida valores
    for key, value in settings.items():
        if not isinstance(value, dict):
            raise ValidationError(f"Valor inválido para {key}")
        
        # Valida campos específicos
        if key == 'system':
            validate_system_settings(value)
        elif key == 'database':
            validate_database_settings(value)
        elif key == 'api':
            validate_api_settings(value)
        elif key == 'jwt':
            validate_jwt_settings(value)
``` 