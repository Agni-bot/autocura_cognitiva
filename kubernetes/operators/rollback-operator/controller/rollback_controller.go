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

	rollbackv1 "github.com/autocura-cognitiva/rollback-operator/api/v1"
)

// RollbackReconciler reconcilia um objeto RollbackPolicy
type RollbackReconciler struct {
	client.Client
	Scheme   *runtime.Scheme
	Recorder record.EventRecorder
}

// +kubebuilder:rbac:groups=rollback.autocura-cognitiva.io,resources=rollbackpolicies,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=rollback.autocura-cognitiva.io,resources=rollbackpolicies/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=rollback.autocura-cognitiva.io,resources=rollbackpolicies/finalizers,verbs=update
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;update;patch
// +kubebuilder:rbac:groups=core,resources=events,verbs=create;patch

// Reconcile é parte da interface reconcile.Reconciler
func (r *RollbackReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := ctrl.LoggerFrom(ctx)
	log.Info("Reconciliando RollbackPolicy", "namespacedName", req.NamespacedName)

	// Obter o objeto RollbackPolicy
	var rollbackPolicy rollbackv1.RollbackPolicy
	if err := r.Get(ctx, req.NamespacedName, &rollbackPolicy); err != nil {
		if errors.IsNotFound(err) {
			// O objeto foi excluído, nada a fazer
			return ctrl.Result{}, nil
		}
		log.Error(err, "Falha ao obter RollbackPolicy")
		return ctrl.Result{}, err
	}

	// Implementar a lógica de rollback aqui
	// ...

	// Atualizar o status
	rollbackPolicy.Status.LastAppliedTime = &metav1.Time{Time: time.Now()}
	rollbackPolicy.Status.LastAppliedStatus = "Succeeded"
	rollbackPolicy.Status.LastAppliedMessage = "Rollback aplicado com sucesso"
	rollbackPolicy.Status.AppliedCount++

	if err := r.Status().Update(ctx, &rollbackPolicy); err != nil {
		log.Error(err, "Falha ao atualizar status do RollbackPolicy")
		return ctrl.Result{}, err
	}

	// Reagendar a reconciliação com base no intervalo de verificação
	interval := time.Duration(rollbackPolicy.Spec.CheckInterval) * time.Second
	if interval == 0 {
		interval = 5 * time.Minute // Valor padrão
	}

	return ctrl.Result{RequeueAfter: interval}, nil
}

// SetupWithManager configura o controller com o Manager
func (r *RollbackReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&rollbackv1.RollbackPolicy{}).
		Watches(&source.Kind{Type: &appsv1.Deployment{}}, &handler.EnqueueRequestForObject{}).
		Complete(r)
}
