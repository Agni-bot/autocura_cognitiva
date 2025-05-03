# Guia de Notificações

## Visão Geral

Este guia descreve o sistema de notificações do Sistema de Autocura Cognitiva.

## Tipos de Notificações

### 1. Email

#### Estrutura
```python
class EmailNotification:
    def __init__(self):
        self.subject: str
        self.body: str
        self.to: list[str]
        self.cc: list[str]
        self.bcc: list[str]
        self.attachments: list[str]
        self.priority: str
        self.template: str
```

#### Implementação
```python
async def send_email(notification: EmailNotification):
    """
    Envia notificação por email.
    
    Args:
        notification: Dados da notificação
    """
    # Configura mensagem
    message = MIMEMultipart()
    message["Subject"] = notification.subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = ", ".join(notification.to)
    
    # Adiciona corpo
    message.attach(MIMEText(notification.body, "html"))
    
    # Adiciona anexos
    for attachment in notification.attachments:
        with open(attachment, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(attachment)}"
            )
            message.attach(part)
    
    # Envia email
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.send_message(message)
```

### 2. Push

#### Estrutura
```python
class PushNotification:
    def __init__(self):
        self.title: str
        self.body: str
        self.data: dict
        self.tokens: list[str]
        self.priority: str
        self.ttl: int
```

#### Implementação
```python
async def send_push(notification: PushNotification):
    """
    Envia notificação push.
    
    Args:
        notification: Dados da notificação
    """
    # Configura mensagem
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=notification.title,
            body=notification.body
        ),
        data=notification.data,
        tokens=notification.tokens,
        android=messaging.AndroidConfig(
            priority=notification.priority,
            ttl=notification.ttl
        )
    )
    
    # Envia notificação
    response = messaging.send_multicast(message)
    
    return {
        "success": response.success_count,
        "failure": response.failure_count,
        "responses": response.responses
    }
```

### 3. SMS

#### Estrutura
```python
class SMSNotification:
    def __init__(self):
        self.message: str
        self.to: list[str]
        self.from_: str
        self.encoding: str
```

#### Implementação
```python
async def send_sms(notification: SMSNotification):
    """
    Envia notificação por SMS.
    
    Args:
        notification: Dados da notificação
    """
    # Configura cliente
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Envia SMS
    responses = []
    for number in notification.to:
        response = client.messages.create(
            body=notification.message,
            from_=notification.from_,
            to=number
        )
        responses.append(response.sid)
    
    return responses
```

## Gerenciamento de Notificações

### 1. Fila

#### Implementação
```python
class NotificationQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.workers = []
    
    async def add(self, notification):
        """
        Adiciona notificação à fila.
        
        Args:
            notification: Notificação a adicionar
        """
        await self.queue.put(notification)
    
    async def process(self):
        """
        Processa notificações da fila.
        """
        while True:
            notification = await self.queue.get()
            try:
                if isinstance(notification, EmailNotification):
                    await send_email(notification)
                elif isinstance(notification, PushNotification):
                    await send_push(notification)
                elif isinstance(notification, SMSNotification):
                    await send_sms(notification)
            except Exception as e:
                logger.error(f"Erro ao enviar notificação: {e}")
            finally:
                self.queue.task_done()
```

### 2. Priorização

#### Implementação
```python
def prioritize_notification(notification):
    """
    Prioriza notificação.
    
    Args:
        notification: Notificação a priorizar
        
    Returns:
        int: Prioridade (0-100)
    """
    # Fatores de prioridade
    factors = {
        "type": {
            "email": 1,
            "push": 2,
            "sms": 3
        },
        "priority": {
            "low": 1,
            "normal": 2,
            "high": 3,
            "urgent": 4
        }
    }
    
    # Calcula prioridade
    priority = (
        factors["type"][notification.type] *
        factors["priority"][notification.priority]
    )
    
    return priority
```

### 3. Agendamento

#### Implementação
```python
async def schedule_notification(notification, when):
    """
    Agenda notificação.
    
    Args:
        notification: Notificação a agendar
        when: Quando enviar
    """
    # Calcula delay
    now = datetime.now()
    delay = (when - now).total_seconds()
    
    # Agenda envio
    asyncio.create_task(
        send_delayed_notification(notification, delay)
    )
```

## Templates

### 1. Email

#### Implementação
```python
class EmailTemplate:
    def __init__(self):
        self.name: str
        self.subject: str
        self.body: str
        self.variables: list[str]
    
    def render(self, data: dict) -> EmailNotification:
        """
        Renderiza template com dados.
        
        Args:
            data: Dados para renderização
            
        Returns:
            EmailNotification: Notificação renderizada
        """
        # Renderiza assunto
        subject = self.subject.format(**data)
        
        # Renderiza corpo
        body = self.body.format(**data)
        
        return EmailNotification(
            subject=subject,
            body=body,
            to=data["to"]
        )
```

### 2. Push

#### Implementação
```python
class PushTemplate:
    def __init__(self):
        self.name: str
        self.title: str
        self.body: str
        self.data: dict
        self.variables: list[str]
    
    def render(self, data: dict) -> PushNotification:
        """
        Renderiza template com dados.
        
        Args:
            data: Dados para renderização
            
        Returns:
            PushNotification: Notificação renderizada
        """
        # Renderiza título
        title = self.title.format(**data)
        
        # Renderiza corpo
        body = self.body.format(**data)
        
        # Renderiza dados
        rendered_data = {
            k: v.format(**data) if isinstance(v, str) else v
            for k, v in self.data.items()
        }
        
        return PushNotification(
            title=title,
            body=body,
            data=rendered_data,
            tokens=data["tokens"]
        )
```

## Preferências

### 1. Configuração

#### Estrutura
```python
class NotificationPreferences:
    def __init__(self):
        self.email: bool
        self.push: bool
        self.sms: bool
        self.frequency: str
        self.channels: list[str]
        self.quiet_hours: dict
```

### 2. Gerenciamento

#### Implementação
```python
async def update_preferences(user_id: str, preferences: NotificationPreferences):
    """
    Atualiza preferências de notificação.
    
    Args:
        user_id: ID do usuário
        preferences: Novas preferências
    """
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {"notification_preferences": preferences.dict()}}
    )
```

## Monitoramento

### 1. Métricas

#### Implementação
```python
from prometheus_client import Counter, Histogram

notification_counter = Counter(
    'notifications_total',
    'Total de notificações enviadas',
    ['type', 'status']
)

notification_latency = Histogram(
    'notification_processing_seconds',
    'Tempo de processamento de notificação',
    ['type']
)
```

### 2. Alertas

#### Configuração
```yaml
groups:
  - name: notifications
    rules:
      - alert: HighNotificationFailureRate
        expr: rate(notifications_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de falha em notificações"
          description: "Taxa de falha acima de 10% nos últimos 5 minutos"
```

## Troubleshooting

### 1. Problemas Comuns

#### Implementação
```python
def check_notification_system():
    """
    Verifica sistema de notificações.
    """
    # Verifica serviços
    check_email_service()
    check_push_service()
    check_sms_service()
    
    # Verifica fila
    check_notification_queue()
    
    # Verifica templates
    check_notification_templates()
```

### 2. Solução de Problemas

#### Implementação
```python
def troubleshoot_notifications():
    """
    Soluciona problemas com notificações.
    """
    # Verifica configuração
    check_notification_system()
    
    # Verifica métricas
    check_notification_metrics()
    
    # Verifica logs
    check_notification_logs()
``` 