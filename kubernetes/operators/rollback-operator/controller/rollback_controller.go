package controllers

import (
	"context"
	"fmt"
	"time"

	"k8s.io/apimachinery/pkg/api/errors"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/util/wait"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/util/workqueue"
	"k8s.io/klog/v2"

	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/labels"
	"k8s.io/apimachinery/pkg/util/runtime"
	"k8s.io/client-go/informers"
	"k8s.io/client-go/tools/record"

	rollbackv1 "autocura_cognitiva\kubernetes\operators\rollback-operator\api\v1"
)

// RollbackController é o controlador para recursos RollbackPolicy
type RollbackController struct {
	kubeClient kubernetes.Interface
	config     *rest.Config
	
	// Informers para observar recursos Kubernetes
	deploymentInformer cache.SharedIndexInformer
	replicaSetInformer cache.SharedIndexInformer
	
	// Fila de trabalho para processar eventos
	workqueue workqueue.RateLimitingInterface
	
	// Recorder para eventos Kubernetes
	recorder record.EventRecorder
}

// NewRollbackController cria um novo controlador RollbackController
func NewRollbackController(kubeClient kubernetes.Interface, config *rest.Config) *RollbackController {
	// Criar informers factory
	informerFactory := informers.NewSharedInformerFactory(kubeClient, time.Minute*30)
	
	// Criar informers para deployments e replicasets
	deploymentInformer := informerFactory.Apps().V1().Deployments().Informer()
	replicaSetInformer := informerFactory.Apps().V1().ReplicaSets().Informer()
	
	// Criar controlador
	controller := &RollbackController{
		kubeClient:         kubeClient,
		config:             config,
		deploymentInformer: deploymentInformer,
		replicaSetInformer: replicaSetInformer,
		workqueue:          workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "RollbackPolicies"),
	}
	
	// Configurar handlers para eventos
	deploymentInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: controller.handleObject,
		UpdateFunc: func(old, new interface{}) {
			newDepl := new.(*appsv1.Deployment)
			oldDepl := old.(*appsv1.Deployment)
			if newDepl.ResourceVersion == oldDepl.ResourceVersion {
				return
			}
			controller.handleObject(new)
		},
		DeleteFunc: controller.handleObject,
	})
	
	replicaSetInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: controller.handleObject,
		UpdateFunc: func(old, new interface{}) {
			controller.handleObject(new)
		},
		DeleteFunc: controller.handleObject,
	})
	
	return controller
}

// Run inicia o controlador
func (c *RollbackController) Run(threadiness int, stopCh <-chan struct{}) error {
	defer runtime.HandleCrash()
	defer c.workqueue.ShutDown()
	
	klog.Info("Iniciando o controlador RollbackController")
	
	// Iniciar informers
	go c.deploymentInformer.Run(stopCh)
	go c.replicaSetInformer.Run(stopCh)
	
	// Aguardar cache sincronizado
	if !cache.WaitForCacheSync(stopCh, c.deploymentInformer.HasSynced, c.replicaSetInformer.HasSynced) {
		return fmt.Errorf("falha ao aguardar caches sincronizarem")
	}
	
	klog.Info("Caches de informers sincronizados com sucesso")
	
	// Iniciar workers
	for i := 0; i < threadiness; i++ {
		go wait.Until(c.runWorker, time.Second, stopCh)
	}
	
	klog.Info("Workers iniciados")
	<-stopCh
	klog.Info("Parando o controlador RollbackController")
	
	return nil
}

// runWorker é um loop de processamento de itens da fila
func (c *RollbackController) runWorker() {
	for c.processNextWorkItem() {
	}
}

// processNextWorkItem processa o próximo item da fila
func (c *RollbackController) processNextWorkItem() bool {
	obj, shutdown := c.workqueue.Get()
	
	if shutdown {
		return false
	}
	
	// Função para marcar item como processado
	defer c.workqueue.Done(obj)
	
	// Processar o item
	err := c.syncHandler(obj)
	if err != nil {
		// Recolocar na fila para reprocessamento
		c.workqueue.AddRateLimited(obj)
		return true
	}
	
	// Item processado com sucesso, remover da fila
	c.workqueue.Forget(obj)
	return true
}

// syncHandler processa um item da fila
func (c *RollbackController) syncHandler(obj interface{}) error {
	// Converter objeto para string (key)
	key, ok := obj.(string)
	if !ok {
		c.workqueue.Forget(obj)
		klog.Errorf("Tipo de objeto inesperado na fila: %#v", obj)
		return nil
	}
	
	// Processar a chave (namespace/nome)
	namespace, name, err := cache.SplitMetaNamespaceKey(key)
	if err != nil {
		klog.Errorf("Formato de chave inválido: %s", key)
		return nil
	}
	
	// Implementar lógica de rollback aqui
	klog.Infof("Processando objeto: %s/%s", namespace, name)
	
	// Verificar se é um deployment
	deployment, err := c.kubeClient.AppsV1().Deployments(namespace).Get(context.TODO(), name, metav1.GetOptions{})
	if err == nil {
		// É um deployment, verificar se precisa de rollback
		return c.checkDeploymentHealth(deployment)
	} else if !errors.IsNotFound(err) {
		// Erro ao obter deployment
		return err
	}
	
	return nil
}

// handleObject adiciona objetos à fila para processamento
func (c *RollbackController) handleObject(obj interface{}) {
	var object metav1.Object
	var ok bool
	
	// Extrair metadados do objeto
	if object, ok = obj.(metav1.Object); !ok {
		tombstone, ok := obj.(cache.DeletedFinalStateUnknown)
		if !ok {
			klog.Errorf("Erro ao obter objeto da cache: %#v", obj)
			return
		}
		object, ok = tombstone.Obj.(metav1.Object)
		if !ok {
			klog.Errorf("Objeto do tombstone não é um objeto válido: %#v", tombstone.Obj)
			return
		}
	}
	
	// Adicionar à fila
	key, err := cache.MetaNamespaceKeyFunc(object)
	if err != nil {
		klog.Errorf("Erro ao criar chave para objeto: %s", err.Error())
		return
	}
	
	c.workqueue.Add(key)
}

// checkDeploymentHealth verifica a saúde de um deployment e aplica rollback se necessário
func (c *RollbackController) checkDeploymentHealth(deployment *appsv1.Deployment) error {
	// Verificar se o deployment está saudável
	if isDeploymentHealthy(deployment) {
		return nil
	}
	
	klog.Infof("Deployment não saudável detectado: %s/%s", deployment.Namespace, deployment.Name)
	
	// Verificar se o deployment tem uma revisão anterior para rollback
	if deployment.Status.ObservedGeneration <= 1 {
		klog.Warningf("Deployment %s/%s não tem revisão anterior para rollback", deployment.Namespace, deployment.Name)
		return nil
	}
	
	// Aplicar rollback
	return c.rollbackDeployment(deployment)
}

// isDeploymentHealthy verifica se um deployment está saudável
func isDeploymentHealthy(deployment *appsv1.Deployment) bool {
	// Verificar se o deployment está progredindo
	for _, condition := range deployment.Status.Conditions {
		if condition.Type == appsv1.DeploymentProgressing {
			if condition.Status != corev1.ConditionTrue {
				return false
			}
		}
		
		if condition.Type == appsv1.DeploymentReplicaFailure {
			if condition.Status == corev1.ConditionTrue {
				return false
			}
		}
	}
	
	// Verificar se o número de réplicas disponíveis é menor que o desejado
	if deployment.Status.AvailableReplicas < *deployment.Spec.Replicas {
		// Verificar se o deployment está em progresso há muito tempo
		for _, condition := range deployment.Status.Conditions {
			if condition.Type == appsv1.DeploymentProgressing && condition.Status == corev1.ConditionTrue {
				// Verificar se o deployment está preso em progresso por mais de 10 minutos
				if time.Since(condition.LastUpdateTime.Time) > time.Minute*10 {
					return false
				}
			}
		}
	}
	
	return true
}

// rollbackDeployment realiza o rollback de um deployment
func (c *RollbackController) rollbackDeployment(deployment *appsv1.Deployment) error {
	klog.Infof("Realizando rollback do deployment %s/%s", deployment.Namespace, deployment.Name)
	
	// Obter histórico de revisões do deployment
	revisions, err := c.kubeClient.AppsV1().ControllerRevisions(deployment.Namespace).List(context.TODO(), metav1.ListOptions{
		LabelSelector: labels.SelectorFromSet(map[string]string{
			"app": deployment.Name,
		}).String(),
	})
	
	if err != nil {
		return fmt.Errorf("erro ao obter histórico de revisões: %v", err)
	}
	
	if len(revisions.Items) <= 1 {
		return fmt.Errorf("não há revisões anteriores disponíveis para rollback")
	}
	
	// Encontrar a revisão anterior
	var previousRevision int64 = 0
	for _, revision := range revisions.Items {
		revisionNumber := revision.Revision
		if revisionNumber > 0 && revisionNumber < deployment.Status.ObservedGeneration && revisionNumber > previousRevision {
			previousRevision = revisionNumber
		}
	}
	
	if previousRevision == 0 {
		return fmt.Errorf("não foi possível determinar a revisão anterior para rollback")
	}
	
	// Criar objeto de rollback
	rollbackConfig := &appsv1.DeploymentRollback{
		Name:               deployment.Name,
		UpdatedAnnotations: nil,
		RollbackTo: appsv1.RollbackConfig{
			Revision: previousRevision,
		},
	}
	
	// Executar rollback
	klog.Infof("Executando rollback do deployment %s/%s para revisão %d", deployment.Namespace, deployment.Name, previousRevision)
	
	// Como DeploymentRollback foi removido da API, vamos simular um rollback atualizando o deployment
	// para usar a especificação da revisão anterior
	
	// Obter a revisão anterior
	rsListOpts := metav1.ListOptions{
		LabelSelector: labels.SelectorFromSet(deployment.Spec.Selector.MatchLabels).String(),
	}
	rsList, err := c.kubeClient.AppsV1().ReplicaSets(deployment.Namespace).List(context.TODO(), rsListOpts)
	if err != nil {
		return fmt.Errorf("erro ao listar ReplicaSets: %v", err)
	}
	
	// Encontrar o ReplicaSet correspondente à revisão anterior
	var targetRS *appsv1.ReplicaSet
	for _, rs := range rsList.Items {
		// Verificar se este RS corresponde à revisão que queremos
		if rs.Annotations["deployment.kubernetes.io/revision"] == fmt.Sprintf("%d", previousRevision) {
			targetRS = &rs
			break
		}
	}
	
	if targetRS == nil {
		return fmt.Errorf("não foi possível encontrar o ReplicaSet correspondente à revisão %d", previousRevision)
	}
	
	// Atualizar o deployment para usar a especificação do ReplicaSet alvo
	deployment.Spec.Template = targetRS.Spec.Template
	
	// Adicionar anotação para indicar rollback
	if deployment.Annotations == nil {
		deployment.Annotations = make(map[string]string)
	}
	deployment.Annotations["rollback.autocura-cognitiva.io/timestamp"] = time.Now().Format(time.RFC3339)
	deployment.Annotations["rollback.autocura-cognitiva.io/revision"] = fmt.Sprintf("%d", previousRevision)
	
	// Atualizar o deployment
	_, err = c.kubeClient.AppsV1().Deployments(deployment.Namespace).Update(context.TODO(), deployment, metav1.UpdateOptions{})
	if err != nil {
		return fmt.Errorf("erro ao atualizar deployment para rollback: %v", err)
	}
	
	klog.Infof("Rollback do deployment %s/%s para revisão %d concluído com sucesso", deployment.Namespace, deployment.Name, previousRevision)
	
	return nil
}
