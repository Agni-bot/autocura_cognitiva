# Plano de Implantação em Kubernetes

Este documento detalha o plano de implantação do Sistema de Autocura Cognitiva em um ambiente Kubernetes, incluindo operadores customizados para healing automático, sistema de rollback probabilístico e orquestração de ambientes paralelos.

## Estrutura de Diretórios

```
autocura_cognitiva/
├── kubernetes/                    # Configurações Kubernetes
│   ├── base/                      # Configurações base compartilhadas
│   │   ├── namespace.yaml         # Namespace dedicado
│   │   ├── serviceaccount.yaml    # Conta de serviço com permissões necessárias
│   │   ├── rbac/                  # Configurações de RBAC
│   │   │   ├── role.yaml          # Papel com permissões necessárias
│   │   │   └── rolebinding.yaml   # Vinculação de papel à conta de serviço
│   │   └── configmap.yaml         # Configurações compartilhadas
│   ├── operators/                 # Operadores customizados
│   │   ├── healing-operator/      # Operador de healing automático
│   │   │   ├── crds/              # Custom Resource Definitions
│   │   │   ├── controller/        # Controlador do operador
│   │   │   └── deployment.yaml    # Implantação do operador
│   │   └── rollback-operator/     # Operador de rollback probabilístico
│   │       ├── crds/              # Custom Resource Definitions
│   │       ├── controller/        # Controlador do operador
│   │       └── deployment.yaml    # Implantação do operador
│   ├── components/                # Componentes do sistema
│   │   ├── monitoramento/         # Módulo de monitoramento
│   │   │   ├── deployment.yaml    # Implantação do módulo
│   │   │   ├── service.yaml       # Serviço para o módulo
│   │   │   └── configmap.yaml     # Configurações específicas
│   │   ├── diagnostico/           # Módulo de diagnóstico
│   │   │   ├── deployment.yaml    # Implantação do módulo
│   │   │   ├── service.yaml       # Serviço para o módulo
│   │   │   └── configmap.yaml     # Configurações específicas
│   │   ├── gerador-acoes/         # Módulo gerador de ações
│   │   │   ├── deployment.yaml    # Implantação do módulo
│   │   │   ├── service.yaml       # Serviço para o módulo
│   │   │   └── configmap.yaml     # Configurações específicas
│   │   └── observabilidade/       # Módulo de observabilidade
│   │       ├── deployment.yaml    # Implantação do módulo
│   │       ├── service.yaml       # Serviço para o módulo
│   │       ├── ingress.yaml       # Ingress para acesso externo
│   │       └── configmap.yaml     # Configurações específicas
│   ├── storage/                   # Configurações de armazenamento
│   │   ├── persistentvolume.yaml  # Volume persistente para dados
│   │   └── persistentvolumeclaim.yaml # Reivindicação de volume persistente
│   ├── environments/              # Ambientes paralelos
│   │   ├── production/            # Ambiente de produção
│   │   │   └── kustomization.yaml # Customização para produção
│   │   ├── staging/               # Ambiente de staging
│   │   │   └── kustomization.yaml # Customização para staging
│   │   └── development/           # Ambiente de desenvolvimento
│   │       └── kustomization.yaml # Customização para desenvolvimento
│   └── kustomization.yaml         # Configuração principal do Kustomize
├── kind-config/                   # Configurações do Kind (Kubernetes in Docker)
│   ├── kind-config.yaml           # Configuração do cluster Kind
│   └── setup-kind.cmd             # Script de configuração do ambiente Kind
├── src/                           # Código fonte do sistema
│   ├── monitoramento/             # Módulo de monitoramento
│   │   ├── monitoramento.py       # Código principal do módulo
│   │   ├── Dockerfile             # Dockerfile específico do módulo
│   │   └── requirements.txt       # Dependências Python
│   ├── diagnostico/               # Módulo de diagnóstico
│   │   ├── diagnostico.py         # Código principal do módulo
│   │   ├── Dockerfile             # Dockerfile específico do módulo
│   │   └── requirements.txt       # Dependências Python
│   ├── gerador_acoes/             # Módulo gerador de ações
│   │   ├── gerador_acoes.py       # Código principal do módulo
│   │   ├── Dockerfile             # Dockerfile específico do módulo
│   │   └── requirements.txt       # Dependências Python
│   └── observabilidade/           # Módulo de observabilidade
│       ├── observabilidade.py     # Código principal do módulo
│       ├── Dockerfile             # Dockerfile específico do módulo
│       └── requirements.txt       # Dependências Python
├── scripts/                       # Scripts do sistema
│   └── build.cmd                  # Script de build
├── config/                        # Configurações do sistema
│   └── docker-compose.yml         # Configuração do Docker Compose
├── tests/                         # Testes do sistema
│   └── gerador_acoes_test.py      # Testes do módulo gerador de ações
├── docs/                          # Documentação do sistema
│   ├── plano_implantacao.md       # Plano de implantação em Kubernetes
│   ├── analise_requisitos.md      # Análise de requisitos
│   ├── arquitetura_modular.md     # Documentação da arquitetura modular
│   ├── documentacao_completa.md   # Documentação completa do sistema
│   ├── manual_usuario.md          # Manual do usuário
│   └── protocolo_emergencia.md    # Protocolo de emergência
├── logs/                          # Logs do sistema
│   └── observabilidade.log        # Logs do módulo de observabilidade
└── README.md                      # Documentação principal do projeto
```

## Namespace e RBAC

Primeiro, vamos definir o namespace e as permissões necessárias.

### namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autocura-cognitiva
  labels:
    name: autocura-cognitiva
    part-of: autocura-cognitiva-system
```

### serviceaccount.yaml
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: autocura-cognitiva-sa
  namespace: autocura-cognitiva
```

### role.yaml
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: autocura-cognitiva-role
  namespace: autocura-cognitiva
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets", "events"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["autoscaling"]
  resources: ["horizontalpodautoscalers"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["autocura.cognitiva.io"]
  resources: ["healingpolicies", "rollbackpolicies", "parallelenvironments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

### rolebinding.yaml
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: autocura-cognitiva-rolebinding
  namespace: autocura-cognitiva
subjects:
- kind: ServiceAccount
  name: autocura-cognitiva-sa
  namespace: autocura-cognitiva
roleRef:
  kind: Role
  name: autocura-cognitiva-role
  apiGroup: rbac.authorization.k8s.io
```

## Operadores Customizados

### Operador de Healing Automático

#### CRD - HealingPolicy
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: healingpolicies.autocura.cognitiva.io
spec:
  group: autocura.cognitiva.io
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                targetRef:
                  type: object
                  properties:
                    apiVersion:
                      type: string
                    kind:
                      type: string
                    name:
                      type: string
                    namespace:
                      type: string
                metrics:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      type:
                        type: string
                        enum: [Resource, Custom]
                      resource:
                        type: object
                        properties:
                          name:
                            type: string
                          target:
                            type: object
                            properties:
                              type:
                                type: string
                                enum: [Utilization, Value]
                              averageUtilization:
                                type: integer
                              averageValue:
                                type: string
                      custom:
                        type: object
                        properties:
                          metricName:
                            type: string
                          threshold:
                            type: number
                actions:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                        enum: [Scale, Restart, Reconfigure, Custom]
                      scale:
                        type: object
                        properties:
                          replicas:
                            type: integer
                          minReplicas:
                            type: integer
                          maxReplicas:
                            type: integer
                      restart:
                        type: object
                        properties:
                          gracePeriodSeconds:
                            type: integer
                      reconfigure:
                        type: object
                        properties:
                          configMap:
                            type: string
                          key:
                            type: string
                          value:
                            type: string
                      custom:
                        type: object
                        properties:
                          command:
                            type: string
                          args:
                            type: array
                            items:
                              type: string
                cooldownSeconds:
                  type: integer
                maxAttempts:
                  type: integer
            status:
              type: object
              properties:
                lastHealing:
                  type: string
                  format: date-time
                attempts:
                  type: integer
                conditions:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                      status:
                        type: string
                      lastTransitionTime:
                        type: string
                        format: date-time
                      reason:
                        type: string
                      message:
                        type: string
  scope: Namespaced
  names:
    plural: healingpolicies
    singular: healingpolicy
    kind: HealingPolicy
    shortNames:
    - hp
```

#### Exemplo de HealingPolicy
```yaml
apiVersion: autocura.cognitiva.io/v1
kind: HealingPolicy
metadata:
  name: monitoramento-healing-policy
  namespace: autocura-cognitiva
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: monitoramento
    namespace: autocura-cognitiva
  metrics:
    - name: cpu-utilization
      type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
    - name: memory-utilization
      type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - name: latency
      type: Custom
      custom:
        metricName: api_latencia_media
        threshold: 100
  actions:
    - type: Scale
      scale:
        minReplicas: 2
        maxReplicas: 5
    - type: Restart
      restart:
        gracePeriodSeconds: 30
    - type: Reconfigure
      reconfigure:
        configMap: monitoramento-config
        key: collection_interval
        value: "30"
  cooldownSeconds: 300
  maxAttempts: 3
```

#### Deployment do Operador de Healing
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healing-operator
  namespace: autocura-cognitiva
spec:
  replicas: 1
  selector:
    matchLabels:
      app: healing-operator
  template:
    metadata:
      labels:
        app: healing-operator
    spec:
      serviceAccountName: autocura-cognitiva-sa
      containers:
      - name: healing-operator
        image: autocura-cognitiva/healing-operator:latest
        imagePullPolicy: Always
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        env:
        - name: WATCH_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: OPERATOR_NAME
          value: "healing-operator"
```

### Operador de Rollback Probabilístico

#### CRD - RollbackPolicy
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: rollbackpolicies.autocura.cognitiva.io
spec:
  group: autocura.cognitiva.io
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                targetRef:
                  type: object
                  properties:
                    apiVersion:
                      type: string
                    kind:
                      type: string
                    name:
                      type: string
                    namespace:
                      type: string
                metrics:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      weight:
                        type: number
                      threshold:
                        type: number
                      comparisonOperator:
                        type: string
                        enum: [GreaterThan, LessThan, Equal]
                probabilityThreshold:
                  type: number
                  minimum: 0
                  maximum: 1
                observationWindowSeconds:
                  type: integer
                rollbackToRevision:
                  type: string
                successCriteria:
                  type: object
                  properties:
                    metricName:
                      type: string
                    threshold:
                      type: number
                    comparisonOperator:
                      type: string
                      enum: [GreaterThan, LessThan, Equal]
                    durationSeconds:
                      type: integer
            status:
              type: object
              properties:
                currentProbability:
                  type: number
                lastEvaluation:
                  type: string
                  format: date-time
                lastRollback:
                  type: string
                  format: date-time
                observations:
                  type: array
                  items:
                    type: object
                    properties:
                      timestamp:
                        type: string
                        format: date-time
                      metrics:
                        type: object
                        additionalProperties:
                          type: number
                      probability:
                        type: number
                conditions:
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        type: string
                      status:
                        type: string
                      lastTransitionTime:
                        type: string
                        format: date-time
                      reason:
                        type: string
                      message:
                        type: string
  scope: Namespaced
  names:
    plural: rollbackpolicies
    singular: rollbackpolicy
    kind: RollbackPolicy
    shortNames:
    - rbp
```

#### Exemplo de RollbackPolicy
```yaml
apiVersion: autocura.cognitiva.io/v1
kind: RollbackPolicy
metadata:
  name: diagnostico-rollback-policy
  namespace: autocura-cognitiva
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: diagnostico
    namespace: autocura-cognitiva
  metrics:
    - name: error_rate
      weight: 0.5
      threshold: 0.05
      comparisonOperator: GreaterThan
    - name: latency_p95
      weight: 0.3
      threshold: 200
      comparisonOperator: GreaterThan
    - name: success_rate
      weight: 0.2
      threshold: 0.95
      comparisonOperator: LessThan
  probabilityThreshold: 0.7
  observationWindowSeconds: 300
  rollbackToRevision: "diagnostico-stable"
  successCriteria:
    metricName: success_rate
    threshold: 0.98
    comparisonOperator: GreaterThan
    durationSeconds: 600
```

## Implantação dos Componentes

### Módulo de Monitoramento

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoramento
  namespace: autocura-cognitiva
  labels:
    app: monitoramento
    component: autocura-cognitiva
spec:
  replicas: 2
  selector:
    matchLabels:
      app: monitoramento
  template:
    metadata:
      labels:
        app: monitoramento
    spec:
      serviceAccountName: autocura-cognitiva-sa
      containers:
      - name: monitoramento
        image: autocura-cognitiva/monitoramento:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        env:
        - name: CONFIG_MAP
          valueFrom:
            configMapKeyRef:
              name: autocura-cognitiva-config
              key: monitoramento.properties
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: monitoramento
  namespace: autocura-cognitiva
spec:
  selector:
    app: monitoramento
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```

### Módulo de Diagnóstico

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: diagnostico
  namespace: autocura-cognitiva
  labels:
    app: diagnostico
    component: autocura-cognitiva
spec:
  replicas: 2
  selector:
    matchLabels:
      app: diagnostico
  template:
    metadata:
      labels:
        app: diagnostico
    spec:
      serviceAccountName: autocura-cognitiva-sa
      containers:
      - name: diagnostico
        image: autocura-cognitiva/diagnostico:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8081
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        env:
        - name: MONITORAMENTO_URL
          value: "http://monitoramento:8080"
        - name: CONFIG_MAP
          valueFrom:
            configMapKeyRef:
              name: autocura-cognitiva-config
              key: diagnostico.properties
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: diagnostico
  namespace: autocura-cognitiva
spec:
  selector:
    app: diagnostico
  ports:
  - port: 8081
    targetPort: 8081
  type: ClusterIP
```

### Módulo Gerador de Ações

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gerador-acoes
  namespace: autocura-cognitiva
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gerador-acoes
  template:
    metadata:
      labels:
        app: gerador-acoes
    spec:
      serviceAccountName: autocura-cognitiva-sa
      containers:
      - name: gerador-acoes
        image: autocura-cognitiva/gerador-acoes:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8082
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        env:
        - name: DIAGNOSTICO_URL
          value: "http://diagnostico:8081"
        - name: CONFIG_MAP
          valueFrom:
            configMapKeyRef:
              name: autocura-cognitiva-config
              key: gerador-acoes.properties
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: gerador-acoes
  namespace: autocura-cognitiva
spec:
  selector:
    app: gerador-acoes
  ports:
  - port: 8082
    targetPort: 8082
  type: ClusterIP
```

### Módulo de Observabilidade

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: observabilidade
  namespace: autocura-cognitiva
  labels:
    app: observabilidade
    component: autocura-cognitiva
spec:
  replicas: 1
  selector:
    matchLabels:
      app: observabilidade
  template:
    metadata:
      labels:
        app: observabilidade
    spec:
      serviceAccountName: autocura-cognitiva-sa
      containers:
      - name: observabilidade
        image: autocura-cognitiva/observabilidade:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 200m
            memory: 256Mi
        env:
        - name: MONITORAMENTO_URL
          value: "http://monitoramento:8080"
        - name: DIAGNOSTICO_URL
          value: "http://diagnostico:8081"
        - name: GERADOR_ACOES_URL
          value: "http://gerador-acoes:8082"
        - name: CONFIG_MAP
          valueFrom:
            configMapKeyRef:
              name: autocura-cognitiva-config
              key: observabilidade.properties
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: observabilidade
  namespace: autocura-cognitiva
spec:
  selector:
    app: observabilidade
  ports:
  - port: 5000
    targetPort: 5000
  type: ClusterIP
```

#### ingress.yaml
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: observabilidade
  namespace: autocura-cognitiva
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: observabilidade.autocura-cognitiva.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: observabilidade
            port:
              number: 5000
```

## Armazenamento Persistente

### persistentvolumeclaim.yaml
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: autocura-cognitiva-data
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: autocura-cognitiva-models
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: autocura-cognitiva-templates
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: autocura-cognitiva-visualizacoes
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 8Gi
  storageClassName: standard
```

## Ambientes Paralelos

### environments/production/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: autocura-cognitiva-prod
bases:
- ../../base
resources:
- namespace.yaml
patchesStrategicMerge:
- patches/resources.yaml
images:
- name: autocura-cognitiva/monitoramento
  newTag: stable
- name: autocura-cognitiva/diagnostico
  newTag: stable
- name: autocura-cognitiva/gerador-acoes
  newTag: stable
- name: autocura-cognitiva/observabilidade
  newTag: stable
```

### environments/staging/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: autocura-cognitiva-staging
bases:
- ../../base
resources:
- namespace.yaml
patchesStrategicMerge:
- patches/resources.yaml
images:
- name: autocura-cognitiva/monitoramento
  newTag: latest
- name: autocura-cognitiva/diagnostico
  newTag: latest
- name: autocura-cognitiva/gerador-acoes
  newTag: latest
- name: autocura-cognitiva/observabilidade
  newTag: latest
```

### environments/development/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base
- ../../operators/healing-operator
- ../../operators/rollback-operator
- ../../components/monitoramento
- ../../components/diagnostico
- ../../components/gerador-acoes
- ../../components/observabilidade

patches:
- target:
    kind: Deployment
    name: monitoramento
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 1
- target:
    kind: Deployment
    name: diagnostico
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 1
- target:
    kind: Deployment
    name: gerador-acoes
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 1
- target:
    kind: Deployment
    name: healing-operator
  patch: |-
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/cpu
      value: 200m
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/memory
      value: 256Mi
- target:
    kind: Deployment
    name: rollback-operator
  patch: |-
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/cpu
      value: 200m
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/memory
      value: 256Mi

configMapGenerator:
- name: autocura-cognitiva-config
  behavior: merge
  literals:
  - global.properties=log_level=DEBUG\nmetrics_interval=15\nenable_tracing=false
  - monitoramento.properties=collection_interval=30\nretention_period_days=3\nanomaly_detection_sensitivity=0.7
  - diagnostico.properties=model_update_interval=1800\nconfidence_threshold=0.6\nmax_diagnosis_depth=3
  - gerador_acoes.properties=action_validation_enabled=false\nsimulation_iterations=50\nrisk_threshold=0.4
  - observabilidade.properties=dashboard_refresh_rate=30\nhistory_max_days=7\nalert_channels=slack
```

## Implantação

Para implantar o sistema, siga estas etapas:

1. Aplique as configurações base:
   ```bash
   kubectl apply -k kubernetes/base
   ```

2. Implante os operadores customizados:
   ```bash
   kubectl apply -k kubernetes/operators
   ```

3. Implante os componentes do sistema:
   ```bash
   kubectl apply -k kubernetes/components
   ```

4. Configure o armazenamento persistente:
   ```bash
   kubectl apply -k kubernetes/storage
   ```

5. Implante o ambiente desejado (produção, staging ou desenvolvimento):
   ```bash
   kubectl apply -k kubernetes/environments/production
   # ou
   kubectl apply -k kubernetes/environments/staging
   # ou
   kubectl apply -k kubernetes/environments/development
   ```

## Monitoramento e Manutenção

Após a implantação, monitore o sistema usando:

```bash
kubectl get pods -n autocura-cognitiva
kubectl get services -n autocura-cognitiva
kubectl get deployments -n autocura-cognitiva
kubectl get healingpolicies -n autocura-cognitiva
kubectl get rollbackpolicies -n autocura-cognitiva
```

Para visualizar logs de um componente específico:

```bash
kubectl logs -f deployment/monitoramento -n autocura-cognitiva
kubectl logs -f deployment/diagnostico -n autocura-cognitiva
kubectl logs -f deployment/gerador-acoes -n autocura-cognitiva
kubectl logs -f deployment/observabilidade -n autocura-cognitiva
```

Para acessar a interface de observabilidade:

```bash
kubectl port-forward service/observabilidade 5000:5000 -n autocura-cognitiva
```

Então, acesse http://localhost:5000 no navegador.

## Considerações de Segurança

- Todos os segredos sensíveis devem ser armazenados como Kubernetes Secrets.
- Utilize Network Policies para restringir a comunicação entre os componentes.
- Configure RBAC adequadamente para limitar permissões.
- Implemente monitoramento de segurança e escaneamento de vulnerabilidades.
- Mantenha as imagens de contêiner atualizadas com as últimas correções de segurança.

## Pontos de Atenção das 4 Fases Implementadas

### Fase 1 - Service Mesh e Circuit Breaker
- **Configuração do Istio**:
  - Verificar se o Istio está corretamente injetado no namespace `autocura-cognitiva`
  - Monitorar o consumo de recursos do control plane do Istio
  - Validar a configuração de mTLS entre os serviços

- **Circuit Breaker**:
  - Monitorar métricas de falhas e timeouts
  - Ajustar thresholds baseado no comportamento real do sistema
  - Implementar alertas para mudanças de estado do circuit breaker

### Fase 2 - Bulkhead e Isolamento
- **Namespaces**:
  - Verificar isolamento entre namespaces (monitoramento, diagnostico, gerador-acoes, observabilidade)
  - Implementar Network Policies específicas para cada namespace
  - Monitorar utilização de recursos por namespace

- **Bulkhead Pattern**:
  - Ajustar limites de recursos baseado em métricas reais
  - Implementar healthchecks específicos para cada componente
  - Monitorar latência entre componentes isolados

### Fase 3 - CQRS e Otimização de Dados
- **Cache Redis**:
  - Monitorar hit ratio do cache
  - Implementar estratégias de invalidação adequadas
  - Configurar backup e persistência dos dados

- **Rate Limiting**:
  - Ajustar limites baseado em métricas de uso
  - Implementar circuit breaker para o rate limiter
  - Monitorar rejeições e latência

### Fase 4 - Circuit Breaker e Retry
- **Políticas de Retry**:
  - Monitorar tentativas de retry por serviço
  - Ajustar timeouts e número de tentativas
  - Implementar backoff exponencial

- **Balanceamento de Carga**:
  - Monitorar distribuição de conexões
  - Ajustar políticas de balanceamento
  - Implementar healthchecks para remoção de endpoints não saudáveis

### Métricas e Monitoramento
- **Healthchecks**:
  - Implementar healthchecks em todos os componentes
  - Configurar alertas para falhas de healthcheck
  - Monitorar tempo de resposta dos healthchecks

- **Métricas Personalizadas**:
  - Coletar métricas de latência cognitiva
  - Monitorar precisão do diagnóstico
  - Acompanhar taxa de sucesso das ações

### Próximos Passos Recomendados
1. Implementar testes de carga para validar as configurações
2. Criar dashboards específicos para cada fase
3. Documentar procedimentos de troubleshooting
4. Automatizar testes de resiliência
5. Implementar backup e recuperação de dados
6. Criar plano de disaster recovery

## Configurações de Healthchecks e Métricas

### Healthchecks
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: healthcheck-config
  namespace: autocura-cognitiva
data:
  health-settings: |
    {
      "probes": {
        "liveness": {
          "httpGet": {
            "path": "/health/live",
            "port": "http"
          },
          "initialDelaySeconds": 30,
          "periodSeconds": 10,
          "timeoutSeconds": 5,
          "successThreshold": 1,
          "failureThreshold": 3
        },
        "readiness": {
          "httpGet": {
            "path": "/health/ready",
            "port": "http"
          },
          "initialDelaySeconds": 15,
          "periodSeconds": 5,
          "timeoutSeconds": 3,
          "successThreshold": 1,
          "failureThreshold": 2
        },
        "startup": {
          "httpGet": {
            "path": "/health/startup",
            "port": "http"
          },
          "initialDelaySeconds": 10,
          "periodSeconds": 5,
          "timeoutSeconds": 2,
          "successThreshold": 1,
          "failureThreshold": 30
        }
      }
    }
```

### Métricas Personalizadas
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-metrics-config
  namespace: autocura-cognitiva
data:
  metrics.yaml: |
    metrics:
      # Métricas de Monitoramento
      - name: autocura_monitoramento_anomalias_detectadas_total
        type: Counter
        help: "Número total de anomalias detectadas"
        labels:
          - severity
          - component
          - type

      - name: autocura_monitoramento_latencia_cognitiva
        type: Histogram
        help: "Latência do processamento cognitivo"
        buckets: [0.1, 0.5, 1.0, 2.0, 5.0]
        labels:
          - operation
          - component

      # Métricas de Diagnóstico
      - name: autocura_diagnostico_precisao
        type: Gauge
        help: "Precisão do diagnóstico em porcentagem"
        labels:
          - model
          - component

      # Métricas de Circuit Breaker
      - name: autocura_circuit_breaker_estado
        type: Gauge
        help: "Estado atual do circuit breaker"
        labels:
          - service
          - endpoint

      # Métricas de Cache
      - name: autocura_cache_hit_ratio
        type: Gauge
        help: "Taxa de acerto do cache"
        labels:
          - cache_type
          - service

      # Métricas de Rate Limiting
      - name: autocura_rate_limit_rejeicoes_total
        type: Counter
        help: "Número total de requisições rejeitadas"
        labels:
          - service
          - endpoint
```

### Configuração do Service Mesh
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: autocura-cognitiva-circuit-breaker
  namespace: autocura-cognitiva
spec:
  host: "*.autocura-cognitiva.svc.cluster.local"
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1024
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 10
```

### 3. Configuração de mTLS

```yaml
# kubernetes/istio/mtls.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: autocura-cognitiva-mtls
  namespace: autocura-cognitiva
spec:
  mtls:
    mode: STRICT
```

### 4. Políticas de Tráfego

```yaml
# kubernetes/istio/traffic-policy.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: autocura-cognitiva-traffic
  namespace: autocura-cognitiva
spec:
  hosts:
  - "*"
  gateways:
  - istio-ingressgateway
  http:
  - match:
    - uri:
        prefix: /monitoramento
    route:
    - destination:
        host: monitoramento
        port:
          number: 8080
  - match:
    - uri:
        prefix: /diagnostico
    route:
    - destination:
        host: diagnostico
        port:
          number: 8081
  - match:
    - uri:
        prefix: /gerador-acoes
    route:
    - destination:
        host: gerador-acoes
        port:
          number: 8082
  - match:
    - uri:
        prefix: /observabilidade
    route:
    - destination:
        host: observabilidade
        port:
          number: 5000
```

### 5. Monitoramento do Service Mesh

```yaml
# kubernetes/istio/monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: istio-metrics
  namespace: istio-system
spec:
  selector:
    matchLabels:
      istio: mixer
  endpoints:
  - port: http-monitoring
    interval: 15s
```

### Configuração do Cache Redis
```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-cache
  namespace: autocura-cognitiva
spec:
  selector:
    app: redis-cache
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-cache
  namespace: autocura-cognitiva
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis-cache
  template:
    metadata:
      labels:
        app: redis-cache
    spec:
      containers:
      - name: redis
        image: redis:7.0-alpine
        ports:
        - containerPort: 6379
        resources:
          limits:
            memory: 512Mi
            cpu: 500m
          requests:
            memory: 256Mi
            cpu: 250m
```

## Configurações de Monitoramento e Alertas

### Prometheus e Grafana
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: autocura-cognitiva-monitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: autocura-cognitiva
  endpoints:
  - port: metrics
    interval: 15s
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: autocura-cognitiva-alerts
  namespace: monitoring
spec:
  groups:
  - name: autocura-cognitiva
    rules:
    - alert: HighLatency
      expr: autocura_monitoramento_latencia_cognitiva > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Latência cognitiva alta detectada"
        description: "A latência do processamento cognitivo está acima de 2 segundos por mais de 5 minutos"
    
    - alert: HighAnomalyRate
      expr: rate(autocura_monitoramento_anomalias_detectadas_total[5m]) > 10
      for: 10m
      labels:
        severity: critical
      annotations:
        summary: "Taxa alta de anomalias"
        description: "Mais de 10 anomalias detectadas por minuto nos últimos 10 minutos"
    
    - alert: CircuitBreakerOpen
      expr: autocura_circuit_breaker_estado == 1
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "Circuit Breaker aberto"
        description: "O circuit breaker está aberto por mais de 2 minutos"
    
    - alert: CacheHitRatioLow
      expr: autocura_cache_hit_ratio < 0.7
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "Taxa de acerto do cache baixa"
        description: "A taxa de acerto do cache está abaixo de 70% por mais de 15 minutos"
```

### Configuração do Grafana
```yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: autocura-cognitiva-dashboard
  namespace: monitoring
spec:
  json: |
    {
      "annotations": {
        "list": []
      },
      "editable": true,
      "fiscalYearStartMonth": 0,
      "graphTooltip": 0,
      "links": [],
      "liveNow": false,
      "panels": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "fieldConfig": {
            "defaults": {
              "color": {
                "mode": "palette-classic"
              },
              "custom": {
                "axisCenteredZero": false,
                "axisColorMode": "text",
                "axisLabel": "",
                "axisPlacement": "auto",
                "barAlignment": 0,
                "drawStyle": "line",
                "fillOpacity": 20,
                "gradientMode": "none",
                "hideFrom": {
                  "legend": false,
                  "tooltip": false,
                  "viz": false
                },
                "lineInterpolation": "linear",
                "lineWidth": 1,
                "pointSize": 5,
                "scaleDistribution": {
                  "type": "linear"
                },
                "showPoints": "never",
                "spanNulls": false,
                "stacking": {
                  "group": "A",
                  "mode": "none"
                },
                "thresholdsStyle": {
                  "mode": "off"
                }
              },
              "mappings": [],
              "thresholds": {
                "mode": "absolute",
                "steps": [
                  {
                    "color": "green",
                    "value": null
                  },
                  {
                    "color": "red",
                    "value": 80
                  }
                ]
              },
              "unit": "s"
            },
            "overrides": []
          },
          "gridPos": {
            "h": 8,
            "w": 12,
            "x": 0,
            "y": 0
          },
          "id": 1,
          "options": {
            "legend": {
              "calcs": [],
              "displayMode": "list",
              "placement": "bottom",
              "showLegend": true
            },
            "tooltip": {
              "mode": "single",
              "sort": "none"
            }
          },
          "targets": [
            {
              "datasource": {
                "type": "prometheus",
                "uid": "prometheus"
              },
              "expr": "autocura_monitoramento_latencia_cognitiva",
              "interval": "",
              "legendFormat": "Latência",
              "refId": "A"
            }
          ],
          "title": "Latência Cognitiva",
          "type": "timeseries"
        },
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "fieldConfig": {
            "defaults": {
              "color": {
                "mode": "palette-classic"
              },
              "custom": {
                "axisCenteredZero": false,
                "axisColorMode": "text",
                "axisLabel": "",
                "axisPlacement": "auto",
                "barAlignment": 0,
                "drawStyle": "line",
                "fillOpacity": 20,
                "gradientMode": "none",
                "hideFrom": {
                  "legend": false,
                  "tooltip": false,
                  "viz": false
                },
                "lineInterpolation": "linear",
                "lineWidth": 1,
                "pointSize": 5,
                "scaleDistribution": {
                  "type": "linear"
                },
                "showPoints": "never",
                "spanNulls": false,
                "stacking": {
                  "group": "A",
                  "mode": "none"
                },
                "thresholdsStyle": {
                  "mode": "off"
                }
              },
              "mappings": [],
              "thresholds": {
                "mode": "absolute",
                "steps": [
                  {
                    "color": "green",
                    "value": null
                  },
                  {
                    "color": "red",
                    "value": 80
                  }
                ]
              }
            },
            "overrides": []
          },
          "gridPos": {
            "h": 8,
            "w": 12,
            "x": 12,
            "y": 0
          },
          "id": 2,
          "options": {
            "legend": {
              "calcs": [],
              "displayMode": "list",
              "placement": "bottom",
              "showLegend": true
            },
            "tooltip": {
              "mode": "single",
              "sort": "none"
            }
          },
          "targets": [
            {
              "datasource": {
                "type": "prometheus",
                "uid": "prometheus"
              },
              "expr": "rate(autocura_monitoramento_anomalias_detectadas_total[5m])",
              "interval": "",
              "legendFormat": "Anomalias/min",
              "refId": "A"
            }
          ],
          "title": "Taxa de Anomalias",
          "type": "timeseries"
        }
      ],
      "refresh": "10s",
      "schemaVersion": 38,
      "style": "dark",
      "tags": ["autocura-cognitiva"],
      "templating": {
        "list": []
      },
      "time": {
        "from": "now-6h",
        "to": "now"
      },
      "timepicker": {},
      "timezone": "",
      "title": "Autocura Cognitiva",
      "version": 0,
      "weekStart": ""
    }
```

### Configuração de Alertas no Slack
```yaml
apiVersion: monitoring.coreos.com/v1
kind: AlertmanagerConfig
metadata:
  name: autocura-cognitiva-alerts
  namespace: monitoring
spec:
  receivers:
  - name: slack-alerts
    slackConfigs:
    - apiURL:
        key: slack-webhook-url
        name: alertmanager-slack
      channel: '#autocura-cognitiva-alerts'
      sendResolved: true
      title: '{{ template "slack.default.title" . }}'
      text: '{{ template "slack.default.text" . }}'
  route:
    groupBy: ['alertname']
    groupWait: 30s
    groupInterval: 5m
    repeatInterval: 4h
    receiver: slack-alerts
```

## Configurações de Backup e Recuperação

### Backup do Redis
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: redis-backup
  namespace: autocura-cognitiva
spec:
  schedule: "0 0 * * *"  # Diariamente à meia-noite
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: redis-backup
            image: redis:7.0-alpine
            command:
            - /bin/sh
            - -c
            - |
              redis-cli -h redis-cache SAVE
              tar -czf /backup/redis-backup-$(date +%Y%m%d).tar.gz /data
            volumeMounts:
            - name: redis-data
              mountPath: /data
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: redis-data
            persistentVolumeClaim:
              claimName: redis-data-pvc
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Backup do Prometheus
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: prometheus-backup
  namespace: monitoring
spec:
  schedule: "0 */6 * * *"  # A cada 6 horas
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: prometheus-backup
            image: prom/prometheus:v2.45.0
            command:
            - /bin/sh
            - -c
            - |
              wget -qO- http://prometheus-server/api/v1/admin/tsdb/snapshot | jq -r '.data.name' > /backup/snapshot-name
              tar -czf /backup/prometheus-backup-$(date +%Y%m%d-%H%M).tar.gz /prometheus/snapshots/$(cat /backup/snapshot-name)
            volumeMounts:
            - name: prometheus-data
              mountPath: /prometheus
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: prometheus-data
            persistentVolumeClaim:
              claimName: prometheus-data-pvc
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Política de Retenção de Backups
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-cleanup
  namespace: autocura-cognitiva
spec:
  schedule: "0 1 * * *"  # Diariamente às 1h
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup-cleanup
            image: alpine:3.18
            command:
            - /bin/sh
            - -c
            - |
              # Manter backups diários por 7 dias
              find /backup -name "*-backup-*.tar.gz" -mtime +7 -delete
              # Manter backups semanais por 30 dias
              find /backup -name "*-backup-*-00.tar.gz" -mtime +30 -delete
              # Manter backups mensais por 1 ano
              find /backup -name "*-backup-*-01-00.tar.gz" -mtime +365 -delete
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Plano de Recuperação de Desastre
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: disaster-recovery-plan
  namespace: autocura-cognitiva
data:
  recovery-steps.yaml: |
    steps:
      # Fase 1 - Recuperação de Infraestrutura
      - name: "Recuperar Namespaces"
        description: "Recriar namespaces necessários"
        commands:
          - kubectl create namespace autocura-cognitiva
          - kubectl create namespace monitoring
          - kubectl label namespace autocura-cognitiva istio-injection=enabled

      # Fase 2 - Recuperação de Armazenamento
      - name: "Restaurar Volumes Persistentes"
        description: "Recriar PVCs e restaurar dados"
        commands:
          - kubectl apply -f kubernetes/storage/redis-pvc.yaml
          - kubectl apply -f kubernetes/storage/prometheus-pvc.yaml
          - kubectl apply -f kubernetes/storage/backup-pvc.yaml

      # Fase 3 - Restauração de Dados
      - name: "Restaurar Redis"
        description: "Restaurar dados do Redis do último backup"
        commands:
          - kubectl create job --from=cronjob/redis-backup redis-restore
          - kubectl wait --for=condition=complete job/redis-restore

      # Fase 4 - Recuperação de Serviços
      - name: "Implantar Serviços"
        description: "Implantar serviços na ordem correta"
        commands:
          - kubectl apply -k kubernetes/base
          - kubectl apply -k kubernetes/components/monitoramento
          - kubectl apply -k kubernetes/components/diagnostico
          - kubectl apply -k kubernetes/components/gerador-acoes
          - kubectl apply -k kubernetes/components/observabilidade

      # Fase 5 - Validação
      - name: "Validar Recuperação"
        description: "Verificar integridade dos serviços"
        commands:
          - kubectl get pods -n autocura-cognitiva
          - kubectl get svc -n autocura-cognitiva
          - curl -s http://monitoramento:8080/health
          - curl -s http://diagnostico:8081/health
          - curl -s http://gerador-acoes:8082/health
          - curl -s http://observabilidade:5000/health
```

### Script de Recuperação Automática
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auto-recovery-script
  namespace: autocura-cognitiva
data:
  recovery.sh: |
    #!/bin/bash
    
    # Função para verificar saúde do serviço
    check_service_health() {
      local service=$1
      local port=$2
      local max_attempts=30
      local attempt=1
      
      while [ $attempt -le $max_attempts ]; do
        if curl -s "http://$service:$port/health" | grep -q "healthy"; then
          echo "Serviço $service está saudável"
          return 0
        fi
        echo "Tentativa $attempt: Serviço $service não está respondendo"
        sleep 10
        ((attempt++))
      done
      
      echo "Timeout: Serviço $service não está saudável após $max_attempts tentativas"
      return 1
    }
    
    # Função para restaurar backup
    restore_backup() {
      local service=$1
      local backup_file=$2
      
      echo "Restaurando backup $backup_file para $service"
      tar -xzf "/backup/$backup_file" -C /
      return $?
    }
    
    # Função para reiniciar serviço
    restart_service() {
      local deployment=$1
      local namespace=$2
      
      echo "Reiniciando deployment $deployment no namespace $namespace"
      kubectl rollout restart deployment/$deployment -n $namespace
      kubectl rollout status deployment/$deployment -n $namespace
      return $?
    }
    
    # Função principal de recuperação
    auto_recover() {
      local service=$1
      local port=$2
      local deployment=$3
      local namespace=$4
      local backup_file=$5
      
      echo "Iniciando recuperação automática para $service"
      
      # Verificar saúde do serviço
      if check_service_health $service $port; then
        echo "Serviço $service está saudável, nenhuma ação necessária"
        return 0
      fi
      
      # Tentar reiniciar o serviço
      if restart_service $deployment $namespace; then
        echo "Serviço $service reiniciado com sucesso"
        return 0
      fi
      
      # Se reinício falhar, restaurar backup
      if restore_backup $service $backup_file; then
        echo "Backup restaurado com sucesso"
        
        # Reiniciar após restauração
        if restart_service $deployment $namespace; then
          echo "Serviço $service recuperado com sucesso"
          return 0
        fi
      fi
      
      echo "Falha na recuperação do serviço $service"
      return 1
    }
    
    # Executar recuperação para cada serviço
    auto_recover "monitoramento" "8080" "monitoramento" "autocura-cognitiva" "monitoramento-backup-latest.tar.gz"
    auto_recover "diagnostico" "8081" "diagnostico" "autocura-cognitiva" "diagnostico-backup-latest.tar.gz"
    auto_recover "gerador-acoes" "8082" "gerador-acoes" "autocura-cognitiva" "gerador-acoes-backup-latest.tar.gz"
    auto_recover "observabilidade" "5000" "observabilidade" "autocura-cognitiva" "observabilidade-backup-latest.tar.gz"
```

## Configurações de Segurança

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: autocura-cognitiva-network-policy
  namespace: autocura-cognitiva
spec:
  podSelector:
    matchLabels:
      app: autocura-cognitiva
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8081
    - protocol: TCP
      port: 8082
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090
    - protocol: TCP
      port: 9093
```

### RBAC e Service Accounts
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: autocura-cognitiva-sa
  namespace: autocura-cognitiva
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: autocura-cognitiva-role
  namespace: autocura-cognitiva
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["networkpolicies"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: autocura-cognitiva-rolebinding
  namespace: autocura-cognitiva
subjects:
- kind: ServiceAccount
  name: autocura-cognitiva-sa
  namespace: autocura-cognitiva
roleRef:
  kind: Role
  name: autocura-cognitiva-role
  apiGroup: rbac.authorization.k8s.io
```

### Configuração de mTLS
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: autocura-cognitiva-mtls
  namespace: autocura-cognitiva
spec:
  mtls:
    mode: STRICT
```

### Política de Auditoria
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
  - group: ""
    resources: ["configmaps"]
  - group: "apps"
    resources: ["deployments"]
  - group: "networking.k8s.io"
    resources: ["networkpolicies"]
  - group: "security.istio.io"
    resources: ["authorizationpolicies"]
  - group: "security.istio.io"
    resources: ["peerauthentications"]
- level: Request
  resources:
  - group: ""
    resources: ["pods"]
  - group: ""
    resources: ["services"]
  - group: "apps"
    resources: ["statefulsets"]
  - group: "networking.istio.io"
    resources: ["virtualservices"]
  - group: "networking.istio.io"
    resources: ["destinationrules"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["namespaces"]
  - group: "rbac.authorization.k8s.io"
    resources: ["roles"]
  - group: "rbac.authorization.k8s.io"
    resources: ["rolebindings"]
```

## Configurações de Escalabilidade

### Configuração do Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: monitoramento-hpa
  namespace: autocura-cognitiva
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: monitoramento
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: External
    external:
      metric:
        name: requests_per_second
        selector:
          matchLabels:
            app: monitoramento
      target:
        type: AverageValue
        averageValue: 100
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: diagnostico-hpa
  namespace: autocura-cognitiva
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: diagnostico
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: External
    external:
      metric:
        name: requests_per_second
        selector:
          matchLabels:
            app: diagnostico
      target:
        type: AverageValue
        averageValue: 100
```

### Configuração do Vertical Pod Autoscaling
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: monitoramento-vpa
  namespace: autocura-cognitiva
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: monitoramento
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: diagnostico-vpa
  namespace: autocura-cognitiva
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: diagnostico
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
```

### Configuração do Cluster Autoscaling
```yaml
apiVersion: autoscaling.openshift.io/v1
kind: ClusterAutoscaler
metadata:
  name: default
spec:
  resourceLimits:
    maxNodesTotal: 10
    cores:
      min: 8
      max: 128
    memory:
      min: 32
      max: 512
  scaleDown:
    enabled: true
    delayAfterAdd: 10m
    delayAfterDelete: 10m
    delayAfterFailure: 3m
    unneededTime: 10m
```

### Configuração do Node Affinity
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoramento
  namespace: autocura-cognitiva
spec:
  replicas: 2
  selector:
    matchLabels:
      app: monitoramento
  template:
    metadata:
      labels:
        app: monitoramento
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-role.kubernetes.io/worker
                operator: In
                values:
                - "true"
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 1
            preference:
              matchExpressions:
              - key: node-type
                operator: In
                values:
                - high-memory
      containers:
      - name: monitoramento
        image: autocura-cognitiva/monitoramento:latest
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 2
            memory: 4Gi
```

### Configuração do Pod Disruption Budget
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: monitoramento-pdb
  namespace: autocura-cognitiva
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: monitoramento
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: diagnostico-pdb
  namespace: autocura-cognitiva
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: diagnostico
```

### Configuração do TopologySpreadConstraints
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoramento
  namespace: autocura-cognitiva
spec:
  replicas: 2
  selector:
    matchLabels:
      app: monitoramento
  template:
    metadata:
      labels:
        app: monitoramento
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: monitoramento
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: monitoramento
      containers:
      - name: monitoramento
        image: autocura-cognitiva/monitoramento:latest
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 2
            memory: 4Gi
```

## Configurações de Logs

### Configuração do Fluentd
```yaml
apiVersion: logging.openshift.io/v1
kind: ClusterLogging
metadata:
  name: autocura-cognitiva
  namespace: openshift-logging
spec:
  managementState: Managed
  logStore:
    type: elasticsearch
    elasticsearch:
      nodeCount: 3
      resources:
        requests:
          memory: 16Gi
          cpu: 1
        limits:
          memory: 32Gi
          cpu: 2
      storage:
        storageClassName: standard
        size: 200Gi
  collection:
    logs:
      type: fluentd
      fluentd: {}
```

### Configuração do Elasticsearch
```yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  version: 7.17.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.master: true
      node.data: true
      node.ingest: true
      node.store.allow_mmap: false
    podTemplate:
      spec:
        containers:
        - name: elasticsearch
          resources:
            requests:
              memory: 4Gi
              cpu: 1
            limits:
              memory: 8Gi
              cpu: 2
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 100Gi
```

### Configuração do Kibana
```yaml
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  version: 7.17.0
  count: 1
  elasticsearchRef:
    name: autocura-cognitiva
  podTemplate:
    spec:
      containers:
      - name: kibana
        resources:
          requests:
            memory: 1Gi
            cpu: 500m
          limits:
            memory: 2Gi
            cpu: 1
```

### Configuração do Loki
```yaml
apiVersion: loki.grafana.com/v1
kind: LokiStack
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  size: 1x.small
  storage:
    schemas:
    - version: v11
      effectiveDate: "2022-06-01"
    secret:
      name: loki-s3
      type: s3
  storageClassName: standard
  tenants:
    mode: static
    authentication:
    - tenantId: autocura-cognitiva
      tenantName: autocura-cognitiva
      principal: system:serviceaccount:monitoring:prometheus
```

### Configuração do Vector
```yaml
apiVersion: vector.dev/v1alpha1
kind: Vector
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  role: Agent
  customConfig:
    data_dir: /vector-data-dir
    api:
      enabled: true
      address: 127.0.0.1:8686
    sources:
      kubernetes_logs:
        type: kubernetes_logs
        pod_annotation_fields:
          container_image: container_image
          container_name: container_name
          pod_labels: pod_labels
          pod_name: pod_name
          namespace: namespace
    transforms:
      remap_timestamps:
        type: remap
        inputs:
          - kubernetes_logs
        source: |
          .timestamp = parse_timestamp(.timestamp, format: "%+")
    sinks:
      elasticsearch:
        type: elasticsearch
        inputs:
          - remap_timestamps
        endpoints:
          - http://elasticsearch:9200
        bulk:
          index: vector-%Y-%m-%d
        compression: gzip
```

### Configuração do Promtail
```yaml
apiVersion: monitoring.grafana.com/v1alpha1
kind: Promtail
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  clients:
  - url: http://loki:3100/loki/api/v1/push
  scrapeConfigs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels:
      - __meta_kubernetes_pod_label_app
      target_label: app
    - source_labels:
      - __meta_kubernetes_pod_label_component
      target_label: component
    - source_labels:
      - __meta_kubernetes_pod_node_name
      target_label: node_name
    - source_labels:
      - __meta_kubernetes_namespace
      target_label: namespace
    - source_labels:
      - __meta_kubernetes_pod_name
      target_label: pod
    - source_labels:
      - __meta_kubernetes_container_name
      target_label: container
```

### Configuração do OpenTelemetry
```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  mode: deployment
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
    exporters:
      jaeger:
        endpoint: jaeger-collector:14250
        tls:
          insecure: true
      prometheus:
        endpoint: "0.0.0.0:8889"
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [jaeger]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]
  resources:
    requests:
      memory: 256Mi
      cpu: 100m
    limits:
      memory: 512Mi
      cpu: 200m
```

### Configuração do Thanos
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ThanosRuler
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  replicas: 2
  resources:
    requests:
      memory: 256Mi
      cpu: 100m
    limits:
      memory: 512Mi
      cpu: 200m
  ruleSelector:
    matchLabels:
      app: autocura-cognitiva
  objectStorageConfig:
    key: thanos.yaml
    name: thanos-objectstorage
```

## Configurações de CI/CD

### Configuração do ArgoCD
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ArgoCD
metadata:
  name: autocura-cognitiva
  namespace: argocd
spec:
  server:
    service:
      type: LoadBalancer
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  controller:
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  repoServer:
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  applicationSet:
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
```

### Configuração do Tekton
```yaml
apiVersion: operator.tekton.dev/v1alpha1
kind: TektonConfig
metadata:
  name: autocura-cognitiva
spec:
  targetNamespace: tekton-pipelines
  profile: all
  pruner:
    resources:
    - pipelinerun
    - taskrun
    schedule: "0 0 * * *"
    keep: 100
  config:
    default-service-account: pipeline
    default-timeout-minutes: 60
    default-managed-by-label-value: tekton-pipelines
```

### Configuração do Jenkins
```yaml
apiVersion: jenkins.io/v1alpha2
kind: Jenkins
metadata:
  name: autocura-cognitiva
  namespace: jenkins
spec:
  master:
    containers:
    - name: jenkins-master
      image: jenkins/jenkins:lts
      imagePullPolicy: Always
      resources:
        requests:
          memory: 1Gi
          cpu: 500m
        limits:
          memory: 2Gi
          cpu: 1
      env:
      - name: JAVA_OPTS
        value: "-Xmx1g -Djenkins.install.runSetupWizard=false"
    securityContext:
      runAsUser: 1000
      fsGroup: 1000
    volumes:
    - name: jenkins-home
      persistentVolumeClaim:
        claimName: jenkins-pvc
    - name: jenkins-config
      configMap:
        name: jenkins-config
  seedJobs:
  - id: jenkins-operator
    targets: "cicd/jobs/*.jenkins"
    description: "Jenkins Operator repository"
    repositoryBranch: master
    repositoryUrl: https://github.com/autocura-cognitiva/jenkins-operator.git
```

### Configuração do GitLab
```yaml
apiVersion: apps.gitlab.com/v1beta1
kind: GitLab
metadata:
  name: autocura-cognitiva
  namespace: gitlab
spec:
  chart:
    values:
      global:
        hosts:
          domain: gitlab.autocura-cognitiva.local
        ingress:
          configureCertmanager: true
      certmanager-issuer:
        email: gitlab@autocura-cognitiva.local
      gitlab:
        gitlab-shell:
          resources:
            requests:
              memory: 256Mi
              cpu: 100m
            limits:
              memory: 512Mi
              cpu: 200m
        sidekiq:
          resources:
            requests:
              memory: 1Gi
              cpu: 500m
            limits:
              memory: 2Gi
              cpu: 1
        webservice:
          resources:
            requests:
              memory: 1Gi
              cpu: 500m
            limits:
              memory: 2Gi
              cpu: 1
        gitaly:
          resources:
            requests:
              memory: 1Gi
              cpu: 500m
            limits:
              memory: 2Gi
              cpu: 1
        task-runner:
          resources:
            requests:
              memory: 1Gi
              cpu: 500m
            limits:
              memory: 2Gi
              cpu: 1
```

### Configuração do SonarQube
```yaml
apiVersion: sonarqube.talanlabs.com/v1alpha1
kind: SonarQube
metadata:
  name: autocura-cognitiva
  namespace: sonarqube
spec:
  version: 9.9.0
  edition: community
  persistence:
    enabled: true
    size: 10Gi
  resources:
    requests:
      memory: 2Gi
      cpu: 1
    limits:
      memory: 4Gi
      cpu: 2
  service:
    type: LoadBalancer
  ingress:
    enabled: true
    host: sonarqube.autocura-cognitiva.local
    annotations:
      kubernetes.io/ingress.class: nginx
```

### Configuração do Nexus
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus
  namespace: nexus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nexus
  template:
    metadata:
      labels:
        app: nexus
    spec:
      containers:
      - name: nexus
        image: sonatype/nexus3:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8081
        - containerPort: 5000
        resources:
          requests:
            memory: 2Gi
            cpu: 1
          limits:
            memory: 4Gi
            cpu: 2
        volumeMounts:
        - name: nexus-data
          mountPath: /nexus-data
      volumes:
      - name: nexus-data
        persistentVolumeClaim:
          claimName: nexus-pvc
```

### Configuração do Harbor
```yaml
apiVersion: goharbor.io/v1beta1
kind: HarborCluster
metadata:
  name: autocura-cognitiva
  namespace: harbor
spec:
  version: 2.5.0
  expose:
    type: ingress
    tls:
      enabled: true
    ingress:
      host: harbor.autocura-cognitiva.local
      annotations:
        kubernetes.io/ingress.class: nginx
  externalURL: https://harbor.autocura-cognitiva.local
  harborAdminPasswordRef: harbor-admin-password
  updateStrategy:
    type: RollingUpdate
  portal:
    replicas: 1
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  core:
    replicas: 1
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1
  jobservice:
    replicas: 1
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1
  registry:
    replicas: 1
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1
  chartmuseum:
    enabled: true
    replicas: 1
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  notary:
    enabled: true
    replicas: 1
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  trivy:
    enabled: true
    replicas: 1
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  database:
    replicas: 1
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1
  redis:
    replicas: 1
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
```

## Configurações de Segurança

### Configuração do OPA Gatekeeper
```yaml
apiVersion: config.gatekeeper.sh/v1alpha1
kind: Config
metadata:
  name: config
  namespace: gatekeeper-system
spec:
  sync:
    syncOnly:
    - group: ""
      version: "v1"
      kind: "Namespace"
    - group: ""
      version: "v1"
      kind: "Pod"
    - group: "apps"
      version: "v1"
      kind: "Deployment"
    - group: "apps"
      version: "v1"
      kind: "StatefulSet"
    - group: "apps"
      version: "v1"
      kind: "DaemonSet"
    - group: "batch"
      version: "v1"
      kind: "CronJob"
    - group: "batch"
      version: "v1"
      kind: "Job"
  validation:
    traces:
    - user: "system:serviceaccount:gatekeeper-system:gatekeeper-admin"
      kind: "AdmissionReview"
      dump: "All"
```

### Configuração do Kyverno
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: autocura-cognitiva-security
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: require-resource-limits
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "CPU and memory resource limits are required"
      pattern:
        spec:
          containers:
          - resources:
              limits:
                memory: "?*"
                cpu: "?*"
  - name: require-read-only-root-filesystem
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Root filesystem must be read-only"
      pattern:
        spec:
          containers:
          - securityContext:
              readOnlyRootFilesystem: true
  - name: require-non-root-user
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Container must not run as root"
      pattern:
        spec:
          containers:
          - securityContext:
              runAsNonRoot: true
```

### Configuração do Falco
```yaml
apiVersion: falco.security.guardrails.ai/v1alpha1
kind: Falco
metadata:
  name: autocura-cognitiva
  namespace: falco
spec:
  falco:
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
    rules:
      - rule: Terminal shell in container
        desc: A shell was used as the entrypoint/exec point into a container
        condition: >
          spawned_process and container and shell_procs and proc.tty != 0
          and container_entrypoint
        output: >
          A shell was spawned in a container with an attached terminal (user=%user.name user_loginuid=%user.loginuid %container.info
          shell=%proc.name parent=%proc.pname cmdline=%proc.cmdline terminal=%proc.tty container_id=%container.id image=%container.image.repository)
        priority: NOTICE
        tags: [container, shell, mitre_execution]
      - rule: Unexpected K8s NodePort Connection
        desc: Detect attempts to connect to NodePort services from unexpected sources
        condition: >
          evt.type=connect and evt.dir=< and
          fd.sport=nodeport and not k8s_containers
        output: >
          Unexpected connection to NodePort service (user=%user.name user_loginuid=%user.loginuid
          connection=%fd.name sport=%fd.sport dport=%fd.dport)
        priority: WARNING
        tags: [network, k8s]
```

### Configuração do Aqua Security
```yaml
apiVersion: operators.aquasec.com/v1alpha1
kind: AquaServer
metadata:
  name: autocura-cognitiva
  namespace: aqua
spec:
  common:
    imagePullSecret: aqua-registry
  server:
    service:
      type: LoadBalancer
    resources:
      requests:
        memory: 2Gi
        cpu: 1
      limits:
        memory: 4Gi
        cpu: 2
    db:
      passwordSecret:
        name: aqua-db-password
        key: password
    auditDB:
      passwordSecret:
        name: aqua-audit-db-password
        key: password
    enforcer:
      enabled: true
      resources:
        requests:
          memory: 256Mi
          cpu: 100m
        limits:
          memory: 512Mi
          cpu: 200m
```

### Configuração do Trivy
```yaml
apiVersion: aquasecurity.github.io/v1alpha1
kind: VulnerabilityReport
metadata:
  name: autocura-cognitiva
  namespace: autocura-cognitiva
spec:
  registry:
    server: harbor.autocura-cognitiva.local
    username: admin
    passwordSecret:
      name: harbor-admin-password
      key: password
  image:
    name: autocura-cognitiva:latest
  scanJob:
    resources:
      requests:
        memory: 256Mi
        cpu: 100m
      limits:
        memory: 512Mi
        cpu: 200m
  schedule: "0 0 * * *"
```

### Configuração do Vault
```yaml
apiVersion: vault.banzaicloud.com/v1alpha1
kind: Vault
metadata:
  name: autocura-cognitiva
  namespace: vault
spec:
  size: 1
  image: vault:1.12.0
  bankVaultsImage: banzaicloud/bank-vaults:latest
  config:
    storage:
      file:
        path: /vault/data
    listener:
      tcp:
        address: "0.0.0.0:8200"
        tls_disable: true
    ui: true
  unsealConfig:
    kubernetes:
      secretNamespace: vault
  resources:
    requests:
      memory: 256Mi
      cpu: 100m
    limits:
      memory: 512Mi
      cpu: 200m
  volumeClaimTemplates:
  - metadata:
      name: vault-data
    spec:
      accessModes:
      - ReadWriteOnce
      resources:
        requests:
          storage: 10Gi
```

### Configuração do Cert-Manager
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: cert-manager@autocura-cognitiva.local
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Configuração do Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: autocura-cognitiva-network-policy
  namespace: autocura-cognitiva
spec:
  podSelector:
    matchLabels:
      app: autocura-cognitiva
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8081
    - protocol: TCP
      port: 8082
    - protocol: TCP
      port: 5000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090
    - protocol: TCP
      port: 9093
```

### Configuração do Backup do Network Policies
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: network-policies-backup
  namespace: autocura-cognitiva
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: network-policies-backup
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - |
              kubectl get networkpolicies -o yaml > /backup/network-policies-backup-$(date +%Y%m%d).yaml
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Configuração do Backup do Grafana
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: grafana-backup
  namespace: monitoring
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: grafana-backup
            image: grafana/grafana:8.2.0
            command:
            - /bin/sh
            - -c
            - |
              curl -X GET http://admin:admin@grafana:3000/api/dashboards/db > /backup/grafana-dashboards-$(date +%Y%m%d).json
              curl -X GET http://admin:admin@grafana:3000/api/datasources > /backup/grafana-datasources-$(date +%Y%m%d).json
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

## Configurações de Monitoramento

### Configuração do ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: autocura-cognitiva
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics
  namespaceSelector:
    matchNames:
    - autocura-cognitiva
```

### Configuração do PrometheusRule
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  groups:
  - name: autocura-cognitiva
    rules:
    - alert: HighLatency
      expr: cognitive_latency_seconds > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High cognitive latency detected
        description: Cognitive latency is above 2 seconds for more than 5 minutes
    - alert: HighAnomalyRate
      expr: rate(anomalies_detected_total[1m]) > 10
      for: 10m
      labels:
        severity: warning
      annotations:
        summary: High anomaly rate detected
        description: More than 10 anomalies detected per minute over the last 10 minutes
    - alert: CircuitBreakerOpen
      expr: circuit_breaker_state == 1
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: Circuit breaker is open
        description: Circuit breaker has been open for more than 2 minutes
    - alert: CacheHitRatioLow
      expr: cache_hit_ratio < 0.7
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: Low cache hit ratio
        description: Cache hit ratio is below 70% for more than 15 minutes
```

### Configuração do GrafanaDashboard
```yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  json: |
    {
      "annotations": {
        "list": []
      },
      "editable": true,
      "gnetId": null,
      "graphTooltip": 0,
      "id": null,
      "links": [],
      "panels": [
        {
          "aliasColors": {},
          "bars": false,
          "dashLength": 10,
          "dashes": false,
          "datasource": "Prometheus",
          "fieldConfig": {
            "defaults": {
              "custom": {}
            },
            "overrides": []
          },
          "fill": 1,
          "fillGradient": 0,
          "gridPos": {
            "h": 8,
            "w": 12,
            "x": 0,
            "y": 0
          },
          "hiddenSeries": false,
          "id": 1,
          "legend": {
            "avg": false,
            "current": false,
            "max": false,
            "min": false,
            "show": true,
            "total": false,
            "values": false
          },
          "lines": true,
          "linewidth": 1,
          "nullPointMode": "null",
          "options": {
            "alertThreshold": true
          },
          "percentage": false,
          "pluginVersion": "7.2.0",
          "pointradius": 2,
          "points": false,
          "renderer": "flot",
          "seriesOverrides": [],
          "spaceLength": 10,
          "stack": false,
          "steppedLine": false,
          "targets": [
            {
              "expr": "cognitive_latency_seconds",
              "interval": "",
              "legendFormat": "",
              "refId": "A"
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeRegions": [],
          "timeShift": null,
          "title": "Cognitive Latency",
          "tooltip": {
            "shared": true,
            "sort": 0,
            "value_type": "individual"
          },
          "type": "graph",
          "xaxis": {
            "buckets": null,
            "mode": "time",
            "name": null,
            "show": true,
            "values": []
          },
          "yaxes": [
            {
              "format": "s",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            },
            {
              "format": "short",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            }
          ],
          "yaxis": {
            "align": false,
            "alignLevel": null
          }
        },
        {
          "aliasColors": {},
          "bars": false,
          "dashLength": 10,
          "dashes": false,
          "datasource": "Prometheus",
          "fieldConfig": {
            "defaults": {
              "custom": {}
            },
            "overrides": []
          },
          "fill": 1,
          "fillGradient": 0,
          "gridPos": {
            "h": 8,
            "w": 12,
            "x": 12,
            "y": 0
          },
          "hiddenSeries": false,
          "id": 2,
          "legend": {
            "avg": false,
            "current": false,
            "max": false,
            "min": false,
            "show": true,
            "total": false,
            "values": false
          },
          "lines": true,
          "linewidth": 1,
          "nullPointMode": "null",
          "options": {
            "alertThreshold": true
          },
          "percentage": false,
          "pluginVersion": "7.2.0",
          "pointradius": 2,
          "points": false,
          "renderer": "flot",
          "seriesOverrides": [],
          "spaceLength": 10,
          "stack": false,
          "steppedLine": false,
          "targets": [
            {
              "expr": "rate(anomalies_detected_total[1m])",
              "interval": "",
              "legendFormat": "",
              "refId": "A"
            }
          ],
          "thresholds": [],
          "timeFrom": null,
          "timeRegions": [],
          "timeShift": null,
          "title": "Anomaly Rate",
          "tooltip": {
            "shared": true,
            "sort": 0,
            "value_type": "individual"
          },
          "type": "graph",
          "xaxis": {
            "buckets": null,
            "mode": "time",
            "name": null,
            "show": true,
            "values": []
          },
          "yaxes": [
            {
              "format": "short",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            },
            {
              "format": "short",
              "label": null,
              "logBase": 1,
              "max": null,
              "min": null,
              "show": true
            }
          ],
          "yaxis": {
            "align": false,
            "alignLevel": null
          }
        }
      ],
      "refresh": "10s",
      "schemaVersion": 25,
      "style": "dark",
      "tags": [],
      "templating": {
        "list": []
      },
      "time": {
        "from": "now-6h",
        "to": "now"
      },
      "timepicker": {},
      "timezone": "",
      "title": "Autocura Cognitiva",
      "uid": "autocura-cognitiva",
      "version": 1
    }
```

### Configuração do AlertmanagerConfig
```yaml
apiVersion: monitoring.coreos.com/v1alpha1
kind: AlertmanagerConfig
metadata:
  name: autocura-cognitiva
  namespace: monitoring
spec:
  route:
    groupBy: ['alertname']
    groupWait: 30s
    groupInterval: 5m
    repeatInterval: 12h
    receiver: 'slack'
  receivers:
  - name: 'slack'
    slackConfigs:
    - channel: '#autocura-cognitiva-alerts'
      apiURL:
        key: slack-webhook-url
        name: slack-webhook
      username: 'Alertmanager'
      title: |-
        [{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }}
      text: >-
        {{ range .Alerts }}
          *Alert:* {{ .Annotations.summary }}
          *Description:* {{ .Annotations.description }}
          *Severity:* {{ .Labels.severity }}
          *Started:* {{ .StartsAt }}
        {{ end }}
```

## Configurações de Rede

### Configuração do Istio Gateway
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: autocura-cognitiva-gateway
  namespace: autocura-cognitiva
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    hosts:
    - "*"
    tls:
      mode: SIMPLE
      credentialName: autocura-cognitiva-cert
```

### Configuração do VirtualService
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: autocura-cognitiva
  namespace: autocura-cognitiva
spec:
  hosts:
  - "*"
  gateways:
  - autocura-cognitiva-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: autocura-cognitiva-service
        port:
          number: 8080
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: connect-failure,refused-stream,unavailable,cancelled,retriable-status-codes
    timeout: 10s
    corsPolicy:
      allowOrigin:
      - "*"
      allowMethods:
      - GET
      - POST
      - PUT
      - DELETE
      - OPTIONS
      allowHeaders:
      - authorization
      - content-type
      maxAge: "24h"
```

### Configuração do DestinationRule
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: autocura-cognitiva
  namespace: autocura-cognitiva
spec:
  host: autocura-cognitiva-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30ms
        tcpKeepalive:
          time: 7200s
          interval: 75s
      http:
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
        maxRetries: 3
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 10
  subsets:
  - name: v1
    labels:
      version: v1
```

### Configuração do Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: autocura-cognitiva-service
  namespace: autocura-cognitiva
  labels:
    app: autocura-cognitiva
    service: autocura-cognitiva
spec:
  ports:
  - port: 8080
    name: http
  - port: 8081
    name: metrics
  selector:
    app: autocura-cognitiva
```

### Configuração do Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: autocura-cognitiva
  namespace: autocura-cognitiva
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /$1
    nginx.ingress.kubernetes.io/proxy-body-size: "8m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "15"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - autocura-cognitiva.local
    secretName: autocura-cognitiva-tls
  rules:
  - host: autocura-cognitiva.local
    http:
      paths:
      - path: /(.*)
        pathType: Prefix
        backend:
          service:
            name: autocura-cognitiva-service
            port:
              number: 8080
```

### Configuração do NetworkPolicy
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: autocura-cognitiva-network-policy
  namespace: autocura-cognitiva
spec:
  podSelector:
    matchLabels:
      app: autocura-cognitiva
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - namespaceSelector:
        matchLabels:
          name: istio-system
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8081
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - namespaceSelector:
        matchLabels:
          name: redis
    - namespaceSelector:
        matchLabels:
          name: postgres
    ports:
    - protocol: TCP
      port: 9090
    - protocol: TCP
      port: 6379
    - protocol: TCP
      port: 5432
```

### Configuração do Service Mesh
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: autocura-cognitiva-circuit-breaker
  namespace: autocura-cognitiva
spec:
  host: autocura-cognitiva-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1
        maxRequestsPerConnection: 1
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
```

### Configuração do Redis Cache
```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-cache
  namespace: autocura-cognitiva
spec:
  ports:
  - port: 6379
  selector:
    app: redis-cache
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-cache
  namespace: autocura-cognitiva
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis-cache
  template:
    metadata:
      labels:
        app: redis-cache
    spec:
      containers:
      - name: redis
        image: redis:6.2
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 200m
            memory: 512Mi
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
```

## Configurações de Armazenamento

### Configuração do StorageClass
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: autocura-cognitiva-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### Configuração do PersistentVolumeClaim
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: autocura-cognitiva-storage
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: autocura-cognitiva-storage
  resources:
    requests:
      storage: 20Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: elasticsearch-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: autocura-cognitiva-storage
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: autocura-cognitiva-storage
  resources:
    requests:
      storage: 50Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: autocura-cognitiva-storage
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backup-pvc
  namespace: autocura-cognitiva
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: autocura-cognitiva-storage
  resources:
    requests:
      storage: 200Gi
```

### Configuração do VolumeSnapshot
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: autocura-cognitiva-snapshot-class
driver: kubernetes.io/aws-ebs
deletionPolicy: Retain
parameters:
  type: gp2
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: redis-snapshot
  namespace: autocura-cognitiva
spec:
  volumeSnapshotClassName: autocura-cognitiva-snapshot-class
  source:
    persistentVolumeClaimName: redis-pvc
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot
  namespace: autocura-cognitiva
spec:
  volumeSnapshotClassName: autocura-cognitiva-snapshot-class
  source:
    persistentVolumeClaimName: postgres-pvc
```

### Configuração do CSI Driver
```yaml
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata:
  name: ebs.csi.aws.com
spec:
  attachRequired: true
  podInfoOnMount: false
  volumeLifecycleModes:
  - Persistent
  - Ephemeral
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ebs-csi-controller-sa
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ebs-external-provisioner-role
rules:
- apiGroups: [""]
  resources: ["persistentvolumes"]
  verbs: ["get", "list", "watch", "create", "delete"]
- apiGroups: [""]
  resources: ["persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "update"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["events"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
- apiGroups: ["storage.k8s.io"]
  resources: ["csinodes"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["snapshot.storage.k8s.io"]
  resources: ["volumesnapshots"]
  verbs: ["get", "list"]
- apiGroups: ["snapshot.storage.k8s.io"]
  resources: ["volumesnapshotcontents"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ebs-csi-provisioner-binding
subjects:
- kind: ServiceAccount
  name: ebs-csi-controller-sa
  namespace: kube-system
roleRef:
  kind: ClusterRole
  name: ebs-external-provisioner-role
  apiGroup: rbac.authorization.k8s.io
```

### Configuração do Rook-Ceph
```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: ceph/ceph:v16.2.7
  dataDirHostPath: /var/lib/rook
  mon:
    count: 3
  mgr:
    count: 1
  dashboard:
    enabled: true
  storage:
    useAllNodes: true
    useAllDevices: false
    config:
      databaseSizeMB: "1024"
      journalSizeMB: "1024"
    nodes:
    - name: "node1"
      devices:
      - name: "sdb"
    - name: "node2"
      devices:
      - name: "sdb"
    - name: "node3"
      devices:
      - name: "sdb"
```

## Configurações de Recursos

### Configuração do ResourceQuota
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: autocura-cognitiva-quota
  namespace: autocura-cognitiva
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    requests.storage: 100Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
    services.nodeports: "0"
    count/pods: "20"
    count/services: "10"
    count/secrets: "20"
    count/configmaps: "20"
    count/persistentvolumeclaims: "10"
    count/services.loadbalancers: "2"
    count/services.nodeports: "0"
```

### Configuração do Limit Ranges
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: autocura-cognitiva-limits
  namespace: autocura-cognitiva
spec:
  limits:
  - type: Container
    default:
      cpu: 500m
      memory: 1Gi
    defaultRequest:
      cpu: 200m
      memory: 512Mi
    max:
      cpu: 2000m
      memory: 4Gi
    min:
      cpu: 100m
      memory: 128Mi
  - type: Pod
    max:
      cpu: 4000m
      memory: 8Gi
```

### Configuração do HorizontalPodAutoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: monitoramento-hpa
  namespace: autocura-cognitiva
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: monitoramento
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: External
    external:
      metric:
        name: requests_per_second
        selector:
          matchLabels:
            app: monitoramento
      target:
        type: AverageValue
        averageValue: 100
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: diagnostico-hpa
  namespace: autocura-cognitiva
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: diagnostico
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: External
    external:
      metric:
        name: requests_per_second
        selector:
          matchLabels:
            app: diagnostico
      target:
        type: AverageValue
        averageValue: 100
```

### Configuração do VerticalPodAutoscaler
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: monitoramento-vpa
  namespace: autocura-cognitiva
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: monitoramento
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
---
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: diagnostico-vpa
  namespace: autocura-cognitiva
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: diagnostico
  updatePolicy:
    updateMode: Auto
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
```

### Configuração do PodDisruptionBudget
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: monitoramento-pdb
  namespace: autocura-cognitiva
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: monitoramento
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: diagnostico-pdb
  namespace: autocura-cognitiva
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: diagnostico
```

### Configuração do TopologySpreadConstraints
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoramento
  namespace: autocura-cognitiva
spec:
  replicas: 2
  selector:
    matchLabels:
      app: monitoramento
  template:
    metadata:
      labels:
        app: monitoramento
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: monitoramento
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: monitoramento
      containers:
      - name: monitoramento
        image: autocura-cognitiva/monitoramento:latest
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 2
            memory: 4Gi
```