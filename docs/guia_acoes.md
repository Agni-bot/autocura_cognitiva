# Guia de Ações

## Visão Geral

Este guia descreve as ações disponíveis no Sistema de Autocura Cognitiva e como utilizá-las.

## Tipos de Ações

### 1. Ações Automáticas

#### Reinicialização de Serviços
```yaml
action:
  name: "restart_service"
  description: "Reinicializa um serviço específico"
  parameters:
    service_name: string
    timeout: number
  steps:
    - stop_service
    - wait
    - start_service
    - verify
```

#### Escalonamento
```yaml
action:
  name: "scale_service"
  description: "Ajusta o número de réplicas de um serviço"
  parameters:
    service_name: string
    replicas: number
    strategy: string
  steps:
    - check_capacity
    - update_replicas
    - verify_health
```

### 2. Ações Semi-Automáticas

#### Backup de Dados
```yaml
action:
  name: "backup_data"
  description: "Realiza backup dos dados do sistema"
  parameters:
    scope: string[]
    destination: string
    retention: number
  steps:
    - verify_space
    - create_backup
    - validate_backup
    - cleanup_old
```

#### Atualização de Configuração
```yaml
action:
  name: "update_config"
  description: "Atualiza configurações do sistema"
  parameters:
    config_file: string
    changes: object
    backup: boolean
  steps:
    - create_backup
    - apply_changes
    - verify_changes
    - rollback_if_needed
```

### 3. Ações Manuais

#### Investigação de Problemas
```yaml
action:
  name: "investigate_issue"
  description: "Guia para investigação de problemas"
  parameters:
    issue_type: string
    severity: string
  steps:
    - collect_logs
    - analyze_metrics
    - check_dependencies
    - document_findings
```

#### Recuperação de Desastres
```yaml
action:
  name: "disaster_recovery"
  description: "Procedimento de recuperação de desastres"
  parameters:
    scenario: string
    backup_point: string
  steps:
    - assess_damage
    - restore_backup
    - verify_systems
    - resume_operations
```

## Implementação de Ações

### 1. Estrutura Base

```python
from abc import ABC, abstractmethod

class Action(ABC):
    """Classe base para todas as ações."""
    
    def __init__(self, parameters: dict):
        self.parameters = parameters
        self.status = "pending"
        self.result = None
    
    @abstractmethod
    def execute(self) -> dict:
        """Executa a ação."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Valida os parâmetros da ação."""
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        """Reverte a ação em caso de falha."""
        pass
```

### 2. Exemplo de Implementação

```python
class RestartService(Action):
    """Ação para reinicializar um serviço."""
    
    def validate(self) -> bool:
        required = ["service_name", "timeout"]
        return all(param in self.parameters for param in required)
    
    def execute(self) -> dict:
        try:
            # Parar serviço
            stop_service(self.parameters["service_name"])
            
            # Aguardar
            time.sleep(self.parameters["timeout"])
            
            # Iniciar serviço
            start_service(self.parameters["service_name"])
            
            # Verificar
            if verify_service(self.parameters["service_name"]):
                self.status = "completed"
                self.result = {"success": True}
            else:
                raise Exception("Serviço não iniciou corretamente")
                
        except Exception as e:
            self.status = "failed"
            self.result = {"success": False, "error": str(e)}
            self.rollback()
            
        return self.result
    
    def rollback(self) -> bool:
        try:
            start_service(self.parameters["service_name"])
            return True
        except:
            return False
```

## Orquestração de Ações

### 1. Workflows

```yaml
workflow:
  name: "recover_from_high_cpu"
  description: "Recuperação de alta utilização de CPU"
  steps:
    - action: "analyze_cpu_usage"
      parameters:
        threshold: 80
        duration: "5m"
    
    - action: "identify_process"
      parameters:
        metric: "cpu_usage"
        threshold: 80
    
    - action: "restart_service"
      parameters:
        service_name: "{{ identified_service }}"
        timeout: 30
    
    - action: "verify_recovery"
      parameters:
        metric: "cpu_usage"
        threshold: 50
        duration: "1m"
```

### 2. Execução Paralela

```python
from concurrent.futures import ThreadPoolExecutor

def execute_parallel_actions(actions: list) -> dict:
    """
    Executa múltiplas ações em paralelo.
    
    Args:
        actions: Lista de ações a executar
        
    Returns:
        dict: Resultados das ações
    """
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_action = {
            executor.submit(action.execute): action 
            for action in actions
        }
        
        for future in concurrent.futures.as_completed(future_to_action):
            action = future_to_action[future]
            try:
                results[action.name] = future.result()
            except Exception as e:
                results[action.name] = {"error": str(e)}
                
    return results
```

## Monitoramento de Ações

### 1. Métricas

```python
class ActionMetrics:
    """Coleta métricas sobre execução de ações."""
    
    def __init__(self):
        self.execution_time = Gauge(
            'action_execution_time_seconds',
            'Tempo de execução das ações'
        )
        self.success_rate = Counter(
            'action_success_total',
            'Número de ações bem sucedidas'
        )
        self.failure_rate = Counter(
            'action_failure_total',
            'Número de ações que falharam'
        )
```

### 2. Logs

```python
def log_action(action: Action, result: dict):
    """
    Registra informações sobre execução de ação.
    
    Args:
        action: Ação executada
        result: Resultado da execução
    """
    logger.info(
        "Ação executada",
        extra={
            "action": action.name,
            "parameters": action.parameters,
            "status": action.status,
            "result": result
        }
    )
```

## Segurança

### 1. Permissões

```yaml
permissions:
  - action: "restart_service"
    roles: ["admin", "operator"]
    conditions:
      - "time_of_day in ['00:00-06:00']"
      - "severity == 'high'"
  
  - action: "update_config"
    roles: ["admin"]
    conditions:
      - "environment == 'production'"
      - "approval_required == true"
```

### 2. Validação

```python
def validate_action_permission(
    user: User,
    action: Action
) -> bool:
    """
    Valida se usuário tem permissão para executar ação.
    
    Args:
        user: Usuário solicitante
        action: Ação a ser executada
        
    Returns:
        bool: True se permitido, False caso contrário
    """
    if not user.has_role(action.required_role):
        return False
        
    if not action.validate_conditions():
        return False
        
    return True
```

## Documentação

### 1. Template de Ação

```markdown
## Nome da Ação

### Descrição
Breve descrição do propósito da ação.

### Parâmetros
- `param1`: Descrição do parâmetro 1
- `param2`: Descrição do parâmetro 2

### Comportamento
Descrição detalhada do que a ação faz.

### Exemplo
```yaml
action:
  name: "action_name"
  parameters:
    param1: "value1"
    param2: "value2"
```

### Possíveis Erros
- Erro 1: Descrição e solução
- Erro 2: Descrição e solução

### Rollback
Descrição do procedimento de rollback.
```

### 2. Histórico de Execução

```python
def log_action_history(
    action: Action,
    result: dict
):
    """
    Registra histórico de execução de ação.
    
    Args:
        action: Ação executada
        result: Resultado da execução
    """
    history = {
        "timestamp": datetime.now(),
        "action": action.name,
        "parameters": action.parameters,
        "status": action.status,
        "result": result,
        "user": current_user
    }
    
    db.actions_history.insert_one(history)
``` 