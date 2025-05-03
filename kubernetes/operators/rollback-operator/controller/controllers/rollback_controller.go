package controllers

import (
	"context"
	"fmt"
	"time"

	appsv1 "k8s.io/api/apps/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/tools/record"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/handler"
	"sigs.k8s.io/controller-runtime/pkg/source"

	rollbackv1 "rollback-operator/api/v1"
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

	// Listar todos os Deployments que correspondem ao seletor
	var deployments appsv1.DeploymentList
	selector, err := metav1.LabelSelectorAsSelector(&rollbackPolicy.Spec.Selector)
	if err != nil {
		log.Error(err, "Falha ao converter seletor")
		return ctrl.Result{}, err
	}

	if err := r.List(ctx, &deployments, client.MatchingLabelsSelector{Selector: selector}); err != nil {
		log.Error(err, "Falha ao listar Deployments")
		return ctrl.Result{}, err
	}

	// Atualizar o status com os recursos monitorados
	rollbackPolicy.Status.MonitoredResources = make([]string, 0, len(deployments.Items))
	rollbackPolicy.Status.CurrentRevisions = make(map[string]int32)
	rollbackPolicy.Status.RollbackRevisions = make(map[string]int32)

	for _, deployment := range deployments.Items {
		resourceKey := fmt.Sprintf("%s/%s", deployment.Namespace, deployment.Name)
		rollbackPolicy.Status.MonitoredResources = append(rollbackPolicy.Status.MonitoredResources, resourceKey)
		rollbackPolicy.Status.CurrentRevisions[resourceKey] = deployment.Status.ObservedGeneration

		// Verificar condições para rollback
		needsRollback := false
		for _, condition := range rollbackPolicy.Spec.Conditions {
			switch condition.Type {
			case "AvailableReplicas":
				availableReplicas := deployment.Status.AvailableReplicas
				if condition.Operator == "LessThan" && availableReplicas < 1 {
					needsRollback = true
				}
			case "UnavailableReplicas":
				unavailableReplicas := deployment.Status.UnavailableReplicas
				if condition.Operator == "GreaterThan" && unavailableReplicas > 0 {
					needsRollback = true
				}
			}
		}

		if needsRollback {
			log.Info("Rollback necessário", "deployment", resourceKey)
			r.Recorder.Event(&rollbackPolicy, "Normal", "RollbackTriggered", 
				fmt.Sprintf("Rollback acionado para %s", resourceKey))

			// Implementar a lógica de rollback
			if rollbackPolicy.Spec.RollbackToRevision != "" {
				// Atualizar a imagem do deployment para a versão especificada
				deployment.Spec.Template.Spec.Containers[0].Image = rollbackPolicy.Spec.RollbackToRevision
				if err := r.Update(ctx, &deployment); err != nil {
					log.Error(err, "Falha ao atualizar deployment", "deployment", resourceKey)
					return ctrl.Result{}, err
				}
				rollbackPolicy.Status.RollbackRevisions[resourceKey] = deployment.Status.ObservedGeneration
			}
		}
	}

	// Atualizar o status
	rollbackPolicy.Status.LastAppliedTime = &metav1.Time{Time: time.Now()}
	rollbackPolicy.Status.LastAppliedStatus = "Succeeded"
	rollbackPolicy.Status.LastAppliedMessage = "Rollback verificado com sucesso"
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