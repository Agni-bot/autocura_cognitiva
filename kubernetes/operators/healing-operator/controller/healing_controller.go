package controller

import (
	"context"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	healingv1 "healing-operator/api/v1"
)

// HealingReconciler reconcilia um objeto Healing
type HealingReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healingpolicies,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healingpolicies/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=healing.autocura-cognitiva.io,resources=healingpolicies/finalizers,verbs=update
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;update;patch
// +kubebuilder:rbac:groups=core,resources=pods,verbs=get;list;watch;delete

// Reconcile é o loop principal do controller
func (r *HealingReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)
	logger.Info("Reconciling Healing", "request", req)

	// Buscar o objeto Healing
	var healing healingv1.Healing
	if err := r.Get(ctx, req.NamespacedName, &healing); err != nil {
		logger.Error(err, "unable to fetch Healing")
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	// Lógica de healing aqui
	// Por enquanto apenas um log
	logger.Info("Healing check completed", "healing", healing.Name)

	// Reagendar próxima verificação em 5 minutos
	return ctrl.Result{RequeueAfter: time.Minute * 5}, nil
}

// SetupWithManager configura o controller com o Manager
func (r *HealingReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&healingv1.Healing{}).
		Complete(r)
}
