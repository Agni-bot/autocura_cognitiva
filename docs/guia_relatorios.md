# Guia de Relatórios

## Visão Geral

Este guia descreve o sistema de geração e gerenciamento de relatórios do Sistema de Autocura Cognitiva.

## Tipos de Relatórios

### 1. Monitoramento

#### Estrutura
```python
class MonitoringReport:
    def __init__(self):
        self.title: str
        self.period: dict
        self.metrics: list[dict]
        self.alerts: list[dict]
        self.incidents: list[dict]
```

#### Implementação
```python
async def generate_monitoring_report(period: dict):
    """
    Gera relatório de monitoramento.
    
    Args:
        period: Período do relatório
        
    Returns:
        MonitoringReport: Relatório gerado
    """
    # Coleta métricas
    metrics = await collect_metrics(period)
    
    # Coleta alertas
    alerts = await collect_alerts(period)
    
    # Coleta incidentes
    incidents = await collect_incidents(period)
    
    return MonitoringReport(
        title="Relatório de Monitoramento",
        period=period,
        metrics=metrics,
        alerts=alerts,
        incidents=incidents
    )
```

### 2. Diagnóstico

#### Estrutura
```python
class DiagnosticReport:
    def __init__(self):
        self.title: str
        self.timestamp: datetime
        self.scope: dict
        self.findings: list[dict]
        self.recommendations: list[str]
```

#### Implementação
```python
async def generate_diagnostic_report(scope: dict):
    """
    Gera relatório de diagnóstico.
    
    Args:
        scope: Escopo do diagnóstico
        
    Returns:
        DiagnosticReport: Relatório gerado
    """
    # Executa diagnóstico
    findings = await run_diagnostic(scope)
    
    # Gera recomendações
    recommendations = generate_recommendations(findings)
    
    return DiagnosticReport(
        title="Relatório de Diagnóstico",
        timestamp=datetime.now(),
        scope=scope,
        findings=findings,
        recommendations=recommendations
    )
```

### 3. Ações

#### Estrutura
```python
class ActionReport:
    def __init__(self):
        self.title: str
        self.period: dict
        self.actions: list[dict]
        self.success_rate: float
        self.efficiency: float
```

#### Implementação
```python
async def generate_action_report(period: dict):
    """
    Gera relatório de ações.
    
    Args:
        period: Período do relatório
        
    Returns:
        ActionReport: Relatório gerado
    """
    # Coleta ações
    actions = await collect_actions(period)
    
    # Calcula métricas
    success_rate = calculate_success_rate(actions)
    efficiency = calculate_efficiency(actions)
    
    return ActionReport(
        title="Relatório de Ações",
        period=period,
        actions=actions,
        success_rate=success_rate,
        efficiency=efficiency
    )
```

## Templates

### 1. Definição

#### Estrutura
```python
class ReportTemplate:
    def __init__(self):
        self.name: str
        self.type: str
        self.sections: list[dict]
        self.styles: dict
        self.filters: dict
```

### 2. Gerenciamento

#### Implementação
```python
async def manage_templates():
    """
    Gerencia templates de relatório.
    """
    # Lista templates
    templates = await list_templates()
    
    # Cria template
    template = await create_template(
        name="Template Padrão",
        type="monitoring",
        sections=[
            {"title": "Métricas", "type": "metrics"},
            {"title": "Alertas", "type": "alerts"},
            {"title": "Incidentes", "type": "incidents"}
        ]
    )
    
    # Atualiza template
    await update_template(
        template.id,
        styles={"theme": "dark", "font": "Arial"}
    )
    
    # Remove template
    await delete_template(template.id)
```

## Agendamento

### 1. Configuração

#### Implementação
```python
async def schedule_report(
    template_id: str,
    schedule: str,
    recipients: list[str]
):
    """
    Agenda geração de relatório.
    
    Args:
        template_id: ID do template
        schedule: Cron expression
        recipients: Lista de destinatários
    """
    # Cria job
    job = scheduler.add_job(
        generate_scheduled_report,
        'cron',
        **parse_cron(schedule),
        args=[template_id, recipients]
    )
    
    return job.id
```

### 2. Execução

#### Implementação
```python
async def generate_scheduled_report(
    template_id: str,
    recipients: list[str]
):
    """
    Gera relatório agendado.
    
    Args:
        template_id: ID do template
        recipients: Lista de destinatários
    """
    # Obtém template
    template = await get_template(template_id)
    
    # Gera relatório
    report = await generate_report(template)
    
    # Envia relatório
    await send_report(report, recipients)
```

## Distribuição

### 1. Formatos

#### Implementação
```python
async def export_report(
    report: Report,
    format: str
):
    """
    Exporta relatório em formato específico.
    
    Args:
        report: Relatório a exportar
        format: Formato de exportação
        
    Returns:
        bytes: Relatório exportado
    """
    if format == "pdf":
        return await export_to_pdf(report)
    elif format == "excel":
        return await export_to_excel(report)
    elif format == "html":
        return await export_to_html(report)
    else:
        raise ValueError(f"Formato não suportado: {format}")
```

### 2. Envio

#### Implementação
```python
async def send_report(
    report: Report,
    recipients: list[str]
):
    """
    Envia relatório para destinatários.
    
    Args:
        report: Relatório a enviar
        recipients: Lista de destinatários
    """
    # Exporta relatório
    pdf = await export_report(report, "pdf")
    
    # Envia email
    await send_email(
        to=recipients,
        subject=report.title,
        body="Segue relatório em anexo.",
        attachments=[("report.pdf", pdf)]
    )
```

## Visualização

### 1. Dashboard

#### Implementação
```python
async def view_report(report_id: str):
    """
    Visualiza relatório no dashboard.
    
    Args:
        report_id: ID do relatório
        
    Returns:
        dict: Dados do relatório
    """
    # Obtém relatório
    report = await get_report(report_id)
    
    # Formata dados
    data = {
        "title": report.title,
        "period": report.period,
        "metrics": format_metrics(report.metrics),
        "alerts": format_alerts(report.alerts),
        "incidents": format_incidents(report.incidents)
    }
    
    return data
```

### 2. Gráficos

#### Implementação
```python
def generate_charts(data: dict):
    """
    Gera gráficos para relatório.
    
    Args:
        data: Dados do relatório
        
    Returns:
        list: Lista de gráficos
    """
    charts = []
    
    # Gráfico de métricas
    metrics_chart = {
        "type": "line",
        "data": {
            "labels": [m["timestamp"] for m in data["metrics"]],
            "datasets": [{
                "label": "Métricas",
                "data": [m["value"] for m in data["metrics"]]
            }]
        }
    }
    charts.append(metrics_chart)
    
    # Gráfico de alertas
    alerts_chart = {
        "type": "bar",
        "data": {
            "labels": [a["type"] for a in data["alerts"]],
            "datasets": [{
                "label": "Alertas",
                "data": [a["count"] for a in data["alerts"]]
            }]
        }
    }
    charts.append(alerts_chart)
    
    return charts
```

## Armazenamento

### 1. Banco de Dados

#### Implementação
```python
async def store_report(report: Report):
    """
    Armazena relatório no banco.
    
    Args:
        report: Relatório a armazenar
    """
    # Insere relatório
    await db.reports.insert_one({
        "title": report.title,
        "type": report.type,
        "data": report.dict(),
        "created_at": datetime.now()
    })
```

### 2. Arquivos

#### Implementação
```python
async def save_report_file(
    report: Report,
    format: str
):
    """
    Salva relatório em arquivo.
    
    Args:
        report: Relatório a salvar
        format: Formato do arquivo
    """
    # Gera nome do arquivo
    filename = f"{report.title}_{datetime.now().isoformat()}.{format}"
    
    # Exporta relatório
    content = await export_report(report, format)
    
    # Salva arquivo
    with open(filename, "wb") as f:
        f.write(content)
```

## Monitoramento

### 1. Métricas

#### Implementação
```python
from prometheus_client import Counter, Histogram

report_counter = Counter(
    'reports_total',
    'Total de relatórios gerados',
    ['type', 'status']
)

report_latency = Histogram(
    'report_generation_seconds',
    'Tempo de geração de relatório',
    ['type']
)
```

### 2. Alertas

#### Configuração
```yaml
groups:
  - name: reports
    rules:
      - alert: HighReportGenerationFailureRate
        expr: rate(reports_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de falha em geração de relatórios"
          description: "Taxa de falha acima de 10% nos últimos 5 minutos"
``` 