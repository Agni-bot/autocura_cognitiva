# Guia de Dashboard

## Visão Geral

Este guia descreve o sistema de dashboard do Sistema de Autocura Cognitiva.

## Componentes

### 1. Widgets

#### Estrutura
```python
class Widget:
    def __init__(self):
        self.id: str
        self.type: str
        self.title: str
        self.data: dict
        self.position: dict
        self.size: dict
        self.refresh: int
```

#### Implementação
```python
async def create_widget(
    type: str,
    title: str,
    data: dict,
    position: dict,
    size: dict
):
    """
    Cria novo widget.
    
    Args:
        type: Tipo do widget
        title: Título do widget
        data: Dados do widget
        position: Posição do widget
        size: Tamanho do widget
        
    Returns:
        Widget: Widget criado
    """
    widget = Widget(
        id=str(uuid.uuid4()),
        type=type,
        title=title,
        data=data,
        position=position,
        size=size,
        refresh=60  # segundos
    )
    
    await db.widgets.insert_one(widget.dict())
    
    return widget
```

### 2. Layout

#### Estrutura
```python
class Layout:
    def __init__(self):
        self.id: str
        self.name: str
        self.widgets: list[Widget]
        self.grid: dict
        self.theme: str
```

#### Implementação
```python
async def create_layout(
    name: str,
    widgets: list[Widget],
    grid: dict,
    theme: str
):
    """
    Cria novo layout.
    
    Args:
        name: Nome do layout
        widgets: Lista de widgets
        grid: Configuração da grade
        theme: Tema do layout
        
    Returns:
        Layout: Layout criado
    """
    layout = Layout(
        id=str(uuid.uuid4()),
        name=name,
        widgets=widgets,
        grid=grid,
        theme=theme
    )
    
    await db.layouts.insert_one(layout.dict())
    
    return layout
```

## Tipos de Widgets

### 1. Métricas

#### Implementação
```python
class MetricWidget(Widget):
    def __init__(self):
        super().__init__()
        self.metric: str
        self.aggregation: str
        self.thresholds: list[dict]
    
    async def update(self):
        """
        Atualiza dados do widget.
        """
        # Coleta métrica
        value = await collect_metric(
            self.metric,
            self.aggregation
        )
        
        # Atualiza dados
        self.data = {
            "value": value,
            "trend": calculate_trend(value),
            "status": check_thresholds(value, self.thresholds)
        }
```

### 2. Gráficos

#### Implementação
```python
class ChartWidget(Widget):
    def __init__(self):
        super().__init__()
        self.chart_type: str
        self.metrics: list[str]
        self.time_range: dict
    
    async def update(self):
        """
        Atualiza dados do widget.
        """
        # Coleta métricas
        data = await collect_metrics(
            self.metrics,
            self.time_range
        )
        
        # Gera gráfico
        chart = generate_chart(
            self.chart_type,
            data
        )
        
        # Atualiza dados
        self.data = chart
```

### 3. Alertas

#### Implementação
```python
class AlertWidget(Widget):
    def __init__(self):
        super().__init__()
        self.severity: str
        self.status: str
        self.limit: int
    
    async def update(self):
        """
        Atualiza dados do widget.
        """
        # Coleta alertas
        alerts = await collect_alerts(
            severity=self.severity,
            status=self.status,
            limit=self.limit
        )
        
        # Atualiza dados
        self.data = {
            "alerts": alerts,
            "count": len(alerts)
        }
```

## Personalização

### 1. Temas

#### Implementação
```python
class Theme:
    def __init__(self):
        self.name: str
        self.colors: dict
        self.fonts: dict
        self.styles: dict

async def apply_theme(
    layout_id: str,
    theme: Theme
):
    """
    Aplica tema ao layout.
    
    Args:
        layout_id: ID do layout
        theme: Tema a aplicar
    """
    # Atualiza layout
    await db.layouts.update_one(
        {"_id": layout_id},
        {"$set": {"theme": theme.dict()}}
    )
```

### 2. Posicionamento

#### Implementação
```python
async def update_widget_position(
    widget_id: str,
    position: dict
):
    """
    Atualiza posição do widget.
    
    Args:
        widget_id: ID do widget
        position: Nova posição
    """
    # Atualiza widget
    await db.widgets.update_one(
        {"_id": widget_id},
        {"$set": {"position": position}}
    )
```

## Atualização

### 1. Dados

#### Implementação
```python
async def update_dashboard(layout_id: str):
    """
    Atualiza dados do dashboard.
    
    Args:
        layout_id: ID do layout
    """
    # Obtém layout
    layout = await get_layout(layout_id)
    
    # Atualiza widgets
    for widget in layout.widgets:
        await widget.update()
    
    # Salva atualizações
    await db.layouts.update_one(
        {"_id": layout_id},
        {"$set": {"widgets": [w.dict() for w in layout.widgets]}}
    )
```

### 2. Cache

#### Implementação
```python
async def cache_dashboard(layout_id: str):
    """
    Armazena dashboard em cache.
    
    Args:
        layout_id: ID do layout
    """
    # Obtém layout
    layout = await get_layout(layout_id)
    
    # Armazena em cache
    await cache.set(
        f"dashboard:{layout_id}",
        layout.dict(),
        expire=300  # 5 minutos
    )
```

## Visualização

### 1. Renderização

#### Implementação
```python
async def render_dashboard(layout_id: str):
    """
    Renderiza dashboard.
    
    Args:
        layout_id: ID do layout
        
    Returns:
        dict: Dashboard renderizado
    """
    # Obtém layout do cache
    layout = await cache.get(f"dashboard:{layout_id}")
    
    if not layout:
        # Atualiza dashboard
        await update_dashboard(layout_id)
        
        # Obtém layout atualizado
        layout = await get_layout(layout_id)
        
        # Armazena em cache
        await cache_dashboard(layout_id)
    
    # Renderiza widgets
    widgets = []
    for widget in layout.widgets:
        rendered = await render_widget(widget)
        widgets.append(rendered)
    
    return {
        "layout": layout,
        "widgets": widgets
    }
```

### 2. Responsividade

#### Implementação
```python
def make_responsive(layout: dict, screen_size: dict):
    """
    Ajusta layout para tamanho de tela.
    
    Args:
        layout: Layout a ajustar
        screen_size: Tamanho da tela
        
    Returns:
        dict: Layout ajustado
    """
    # Calcula proporções
    width_ratio = screen_size["width"] / layout["grid"]["width"]
    height_ratio = screen_size["height"] / layout["grid"]["height"]
    
    # Ajusta widgets
    for widget in layout["widgets"]:
        widget["position"]["x"] *= width_ratio
        widget["position"]["y"] *= height_ratio
        widget["size"]["width"] *= width_ratio
        widget["size"]["height"] *= height_ratio
    
    return layout
```

## Monitoramento

### 1. Métricas

#### Implementação
```python
from prometheus_client import Counter, Histogram

dashboard_counter = Counter(
    'dashboard_views_total',
    'Total de visualizações do dashboard',
    ['layout']
)

dashboard_latency = Histogram(
    'dashboard_render_seconds',
    'Tempo de renderização do dashboard',
    ['layout']
)
```

### 2. Alertas

#### Configuração
```yaml
groups:
  - name: dashboard
    rules:
      - alert: HighDashboardLatency
        expr: dashboard_render_seconds > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alta latência na renderização do dashboard"
          description: "Tempo de renderização acima de 2 segundos"
``` 