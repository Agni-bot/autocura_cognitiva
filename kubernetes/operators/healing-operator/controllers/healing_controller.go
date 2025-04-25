package controllers

import (
	"context"
	"fmt"
	"time"

	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/record"
	"k8s.io/client-go/util/workqueue"
	"k8s.io/klog/v2"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller"
	"sigs.k8s.io/controller-runtime/pkg/handler"
	"sigs.k8s.io/controller-runtime/pkg/manager"
	"sigs.k8s.io/controller-runtime/pkg/reconcile"
	"sigs.k8s.io/controller-runtime/pkg/source"

	healingv1 "github.com/autocura-cognitiva/healing-operator/api/v1"
)

// HealingReconciler reconcilia um objeto HealingPolicy
type HealingReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

// +kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healingpolicies,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healingpolicies/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healingpolicies/finalizers,verbs=update
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;update;patch
// +kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch;delete

// Reconcile é parte da interface reconcile.Reconciler
func (r *HealingReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := ctrl.LoggerFrom(ctx)
	log.Info("Reconciliando HealingPolicy", "namespacedName", req.NamespacedName)

	// Obter o objeto HealingPolicy
	var healingPolicy healingv1.HealingPolicy
	if err := r.Get(ctx, req.NamespacedName, &healingPolicy); err != nil {
		if errors.IsNotFound(err) {
			// O objeto foi excluído, nada a fazer
			return ctrl.Result{}, nil
		}
		log.Error(err, "Falha ao obter HealingPolicy")
		return ctrl.Result{}, err
	}

	// Implementar a lógica de healing aqui
	// ...

	// Atualizar o status
	healingPolicy.Status.LastAppliedTime = &metav1.Time{Time: time.Now()}
	healingPolicy.Status.LastAppliedStatus = "Succeeded"
	healingPolicy.Status.LastAppliedMessage = "Healing aplicado com sucesso"
	healingPolicy.Status.AppliedCount++

	if err := r.Status().Update(ctx, &healingPolicy); err != nil {
		log.Error(err, "Falha ao atualizar status do HealingPolicy")
		return ctrl.Result{}, err
	}

	// Reagendar a reconciliação com base no intervalo de verificação
	interval := time.Duration(healingPolicy.Spec.CheckInterval) * time.Second
	if interval == 0 {
		interval = 5 * time.Minute // Valor padrão
	}

	return ctrl.Result{RequeueAfter: interval}, nil
}

// SetupWithManager configura o controller com o Manager
func (r *HealingReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&healingv1.HealingPolicy{}).
		Watches(&source.Kind{Type: &appsv1.Deployment{}}, &handler.EnqueueRequestForObject{}).
		Watches(&source.Kind{Type: &corev1.Pod{}}, &handler.EnqueueRequestForObject{}).
		Complete(r)
}
