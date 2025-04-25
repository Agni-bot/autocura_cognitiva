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

	healingv1 "https://github.com/Agni-bot/autocura_cognitiva/tree/main/kubernetes/operators/healing-operator/api/v1"
)

// HealingController é o controlador para recursos HealingPolicy
type HealingController struct {
	kubeClient kubernetes.Interface
	config     *rest.Config
	
	// Informers para observar recursos Kubernetes
	deploymentInformer cache.SharedIndexInformer
	podInformer        cache.SharedIndexInformer
	
	// Fila de trabalho para processar eventos
	workqueue workqueue.RateLimitingInterface
	
	// Recorder para eventos Kubernetes
	recorder record.EventRecorder
}

// NewHealingController cria um novo controlador HealingController
func NewHealingController(kubeClient kubernetes.Interface, config *rest.Config) *HealingController {
	// Criar informers factory
	informerFactory := informers.NewSharedInformerFactory(kubeClient, time.Minute*30)
	
	// Criar informers para deployments e pods
	deploymentInformer := informerFactory.Apps().V1().Deployments().Informer()
	podInformer := informerFactory.Core().V1().Pods().Informer()
	
	// Criar controlador
	controller := &HealingController{
		kubeClient:        kubeClient,
		config:            config,
		deploymentInformer: deploymentInformer,
		podInformer:        podInformer,
		workqueue:         workqueue.NewNamedRateLimitingQueue(workqueue.DefaultControllerRateLimiter(), "HealingPolicies"),
	}
	
	// Configurar handlers para eventos
	deploymentInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: controller.handleObject,
		UpdateFunc: func(old, new interface{}) {
			controller.handleObject(new)
		},
		DeleteFunc: controller.handleObject,
	})
	
	podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
		AddFunc: controller.handleObject,
		UpdateFunc: func(old, new interface{}) {
			controller.handleObject(new)
		},
		DeleteFunc: controller.handleObject,
	})
	
	return controller
}

// Run inicia o controlador
func (c *HealingController) Run(threadiness int, stopCh <-chan struct{}) error {
	defer runtime.HandleCrash()
	defer c.workqueue.ShutDown()
	
	klog.Info("Iniciando o controlador HealingController")
	
	// Iniciar informers
	go c.deploymentInformer.Run(stopCh)
	go c.podInformer.Run(stopCh)
	
	// Aguardar cache sincronizado
	if !cache.WaitForCacheSync(stopCh, c.deploymentInformer.HasSynced, c.podInformer.HasSynced) {
		return fmt.Errorf("falha ao aguardar caches sincronizarem")
	}
	
	klog.Info("Caches de informers sincronizados com sucesso")
	
	// Iniciar workers
	for i := 0; i < threadiness; i++ {
		go wait.Until(c.runWorker, time.Second, stopCh)
	}
	
	klog.Info("Workers iniciados")
	<-stopCh
	klog.Info("Parando o controlador HealingController")
	
	return nil
}

// runWorker é um loop de processamento de itens da fila
func (c *HealingController) runWorker() {
	for c.processNextWorkItem() {
	}
}

// processNextWorkItem processa o próximo item da fila
func (c *HealingController) processNextWorkItem() bool {
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
func (c *HealingController) syncHandler(obj interface{}) error {
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
	
	// Implementar lógica de healing aqui
	klog.Infof("Processando objeto: %s/%s", namespace, name)
	
	// Exemplo: verificar pods com problemas
	c.checkUnhealthyPods(namespace)
	
	return nil
}

// handleObject adiciona objetos à fila para processamento
func (c *HealingController) handleObject(obj interface{}) {
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

// checkUnhealthyPods verifica pods com problemas e aplica ações de healing
func (c *HealingController) checkUnhealthyPods(namespace string) {
	// Listar pods no namespace
	pods, err := c.kubeClient.CoreV1().Pods(namespace).List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		klog.Errorf("Erro ao listar pods: %s", err.Error())
		return
	}
	
	// Verificar cada pod
	for _, pod := range pods.Items {
		// Verificar se o pod está em estado não saudável
		if isPodUnhealthy(&pod) {
			klog.Infof("Pod não saudável detectado: %s/%s", pod.Namespace, pod.Name)
			
			// Aplicar ação de healing (exemplo: reiniciar pod)
			err := c.healPod(&pod)
			if err != nil {
				klog.Errorf("Erro ao aplicar healing no pod %s/%s: %s", pod.Namespace, pod.Name, err.Error())
			}
		}
	}
}

// isPodUnhealthy verifica se um pod está em estado não saudável
func isPodUnhealthy(pod *corev1.Pod) bool {
	// Verificar se o pod está em estado de falha
	if pod.Status.Phase == corev1.PodFailed {
		return true
	}
	
	// Verificar se o pod está pendente por muito tempo
	if pod.Status.Phase == corev1.PodPending {
		// Verificar tempo de criação
		creationTime := pod.CreationTimestamp.Time
		if time.Since(creationTime) > time.Minute*5 {
			return true
		}
	}
	
	// Verificar containers em estado de erro
	for _, containerStatus := range pod.Status.ContainerStatuses {
		if !containerStatus.Ready && containerStatus.RestartCount > 3 {
			return true
		}
		
		// Verificar se o container está em estado de erro
		if containerStatus.State.Waiting != nil {
			reason := containerStatus.State.Waiting.Reason
			if reason == "CrashLoopBackOff" || reason == "ImagePullBackOff" || reason == "ErrImagePull" {
				return true
			}
		}
	}
	
	return false
}

// healPod aplica ações de healing em um pod
func (c *HealingController) healPod(pod *corev1.Pod) error {
	// Exemplo: excluir o pod para que seja recriado
	klog.Infof("Aplicando healing no pod %s/%s", pod.Namespace, pod.Name)
	
	// Verificar se o pod é gerenciado por um deployment
	if ownerRef := metav1.GetControllerOf(pod); ownerRef != nil && ownerRef.Kind == "ReplicaSet" {
		// Obter o ReplicaSet
		rs, err := c.kubeClient.AppsV1().ReplicaSets(pod.Namespace).Get(context.TODO(), ownerRef.Name, metav1.GetOptions{})
		if err != nil {
			return fmt.Errorf("erro ao obter ReplicaSet %s: %v", ownerRef.Name, err)
		}
		
		// Verificar se o ReplicaSet é gerenciado por um Deployment
		if rsOwnerRef := metav1.GetControllerOf(rs); rsOwnerRef != nil && rsOwnerRef.Kind == "Deployment" {
			// Obter o Deployment
			deployment, err := c.kubeClient.AppsV1().Deployments(pod.Namespace).Get(context.TODO(), rsOwnerRef.Name, metav1.GetOptions{})
			if err != nil {
				return fmt.Errorf("erro ao obter Deployment %s: %v", rsOwnerRef.Name, err)
			}
			
			// Aplicar healing no deployment (exemplo: reiniciar rollout)
			return c.restartDeployment(deployment)
		}
	}
	
	// Se não for gerenciado por um deployment, excluir o pod diretamente
	return c.kubeClient.CoreV1().Pods(pod.Namespace).Delete(context.TODO(), pod.Name, metav1.DeleteOptions{})
}

// restartDeployment reinicia um deployment
func (c *HealingController) restartDeployment(deployment *appsv1.Deployment) error {
	klog.Infof("Reiniciando rollout do deployment %s/%s", deployment.Namespace, deployment.Name)
	
	// Adicionar anotação para forçar rollout
	if deployment.Spec.Template.Annotations == nil {
		deployment.Spec.Template.Annotations = make(map[string]string)
	}
	deployment.Spec.Template.Annotations["kubectl.kubernetes.io/restartedAt"] = time.Now().Format(time.RFC3339)
	
	// Atualizar o deployment
	_, err := c.kubeClient.AppsV1().Deployments(deployment.Namespace).Update(context.TODO(), deployment, metav1.UpdateOptions{})
	return err
}
