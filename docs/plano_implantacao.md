# Plano de Implantação em Kubernetes

Este documento detalha o plano de implantação do Sistema de Autocura Cognitiva em um ambiente Kubernetes, incluindo operadores customizados para healing automático, sistema de rollback probabilístico e orquestração de ambientes paralelos.

## Estrutura de Diretórios

```
kubernetes/
├── base/                      # Configurações base compartilhadas
│   ├── namespace.yaml         # Namespace dedicado
│   ├── serviceaccount.yaml    # Conta de serviço com permissões necessárias
│   ├── rbac/                  # Configurações de RBAC
│   │   ├── role.yaml          # Papel com permissões necessárias
│   │   └── rolebinding.yaml   # Vinculação de papel à conta de serviço
│   └── configmap.yaml         # Configurações compartilhadas
├── operators/                 # Operadores customizados
│   ├── healing-operator/      # Operador de healing automático
│   │   ├── crds/              # Custom Resource Definitions
│   │   ├── controller/        # Controlador do operador
│   │   └── deployment.yaml    # Implantação do operador
│   └── rollback-operator/     # Operador de rollback probabilístico
│       ├── crds/              # Custom Resource Definitions
│       ├── controller/        # Controlador do operador
│       └── deployment.yaml    # Implantação do operador
├── components/                # Componentes do sistema
│   ├── monitoramento/         # Módulo de monitoramento
│   │   ├── deployment.yaml    # Implantação do módulo
│   │   ├── service.yaml       # Serviço para o módulo
│   │   └── configmap.yaml     # Configurações específicas
│   ├── diagnostico/           # Módulo de diagnóstico
│   │   ├── deployment.yaml    # Implantação do módulo
│   │   ├── service.yaml       # Serviço para o módulo
│   │   └── configmap.yaml     # Configurações específicas
│   ├── gerador-acoes/         # Módulo gerador de ações
│   │   ├── deployment.yaml    # Implantação do módulo
│   │   ├── service.yaml       # Serviço para o módulo
│   │   └── configmap.yaml     # Configurações específicas
│   └── observabilidade/       # Módulo de observabilidade
│       ├── deployment.yaml    # Implantação do módulo
│       ├── service.yaml       # Serviço para o módulo
│       ├── ingress.yaml       # Ingress para acesso externo
│       └── configmap.yaml     # Configurações específicas
├── storage/                   # Configurações de armazenamento
│   ├── persistentvolume.yaml  # Volume persistente para dados
│   └── persistentvolumeclaim.yaml # Reivindicação de volume persistente
├── environments/              # Ambientes paralelos
│   ├── production/            # Ambiente de produção
│   │   └── kustomization.yaml # Customização para produção
│   ├── staging/               # Ambiente de staging
│   │   └── kustomization.yaml # Customização para staging
│   └── development/           # Ambiente de desenvolvimento
│       └── kustomization.yaml # Customização para desenvolvimento
└── kustomization.yaml         # Configuração principal do Kustomize
```

## Namespace e RBAC

Primeiro, vamos definir o namespace e as permissões necessárias para o sistema.

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
          name: http
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi
          requests:
            cpu: 500m
            memory: 512Mi
        env:
        - name: CONFIG_MAP
          value: monitoramento-config
        - name: LOG_LEVEL
          value: INFO
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: data-volume
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: monitoramento-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: autocura-cognitiva-data
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: monitoramento
  namespace: autocura-cognitiva
  labels:
    app: monitoramento
    component: autocura-cognitiva
spec:
  selector:
    app: monitoramento
  ports:
  - port: 8080
    targetPort: http
    name: http
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
          name: http
        resources:
          limits:
            cpu: 2000m
            memory: 2Gi
          requests:
            cpu: 1000m
            memory: 1Gi
        env:
        - name: MONITORAMENTO_URL
          value: "http://monitoramento:8080"
        - name: CONFIG_MAP
          value: diagnostico-config
        - name: LOG_LEVEL
          value: INFO
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: models-volume
          mountPath: /app/models
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 60
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: diagnostico-config
      - name: models-volume
        persistentVolumeClaim:
          claimName: autocura-cognitiva-models
```

### Módulo Gerador de Ações

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gerador-acoes
  namespace: autocura-cognitiva
  labels:
    app: gerador-acoes
    component: autocura-cognitiva
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
          name: http
        resources:
          limits:
            cpu: 1500m
            memory: 1.5Gi
          requests:
            cpu: 750m
            memory: 768Mi
        env:
        - name: DIAGNOSTICO_URL
          value: "http://diagnostico:8081"
        - name: CONFIG_MAP
          value: gerador-acoes-config
        - name: LOG_LEVEL
          value: INFO
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: templates-volume
          mountPath: /app/templates
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 45
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: gerador-acoes-config
      - name: templates-volume
        persistentVolumeClaim:
          claimName: autocura-cognitiva-templates
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
          name: http
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi
          requests:
            cpu: 500m
            memory: 512Mi
        env:
        - name: MONITORAMENTO_URL
          value: "http://monitoramento:8080"
        - name: DIAGNOSTICO_URL
          value: "http://diagnostico:8081"
        - name: GERADOR_ACOES_URL
          value: "http://gerador-acoes:8082"
        - name: CONFIG_MAP
          value: observabilidade-config
        - name: LOG_LEVEL
          value: INFO
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: visualizacoes-volume
          mountPath: /app/visualizacoes
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: observabilidade-config
      - name: visualizacoes-volume
        persistentVolumeClaim:
          claimName: autocura-cognitiva-visualizacoes
```

#### ingress.yaml
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: observabilidade-ingress
  namespace: autocura-cognitiva
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - observabilidade.autocura-cognitiva.example.com
    secretName: observabilidade-tls
  rules:
  - host: observabilidade.autocura-cognitiva.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: observabilidade
            port:
              name: http
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
namespace: autocura-cognitiva-dev
bases:
- ../../base
resources:
- namespace.yaml
patchesStrategicMerge:
- patches/resources.yaml
- patches/debug.yaml
images:
- name: autocura-cognitiva/monitoramento
  newTag: dev
- name: autocura-cognitiva/diagnostico
  newTag: dev
- name: autocura-cognitiva/gerador-acoes
  newTag: dev
- name: autocura-cognitiva/observabilidade
  newTag: dev
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
