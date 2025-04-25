package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
)

// GroupVersion é a versão da API para o pacote rollback
var GroupVersion = schema.GroupVersion{Group: "rollback.autocura-cognitiva.io", Version: "v1"}

// SchemeBuilder é usado para adicionar tipos Go ao esquema
var SchemeBuilder = runtime.NewSchemeBuilder(addKnownTypes)

// AddToScheme adiciona os tipos deste grupo ao esquema fornecido
var AddToScheme = SchemeBuilder.AddToScheme

// addKnownTypes adiciona os tipos definidos neste pacote ao esquema
func addKnownTypes(scheme *runtime.Scheme) error {
	scheme.AddKnownTypes(GroupVersion,
		&RollbackPolicy{},
		&RollbackPolicyList{},
	)
	metav1.AddToGroupVersion(scheme, GroupVersion)
	return nil
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:scope=Cluster,shortName=rp
// +kubebuilder:printcolumn:name="Status",type="string",JSONPath=".status.lastAppliedStatus"
// +kubebuilder:printcolumn:name="Age",type="date",JSONPath=".metadata.creationTimestamp"

// RollbackPolicy define uma política de rollback para recursos Kubernetes
type RollbackPolicy struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   RollbackPolicySpec   `json:"spec,omitempty"`
	Status RollbackPolicyStatus `json:"status,omitempty"`
}

// RollbackPolicySpec define a especificação desejada para uma RollbackPolicy
type RollbackPolicySpec struct {
	// Seletor para os recursos alvo desta política
	Selector metav1.LabelSelector `json:"selector"`

	// Namespace alvo (vazio para todos os namespaces)
	TargetNamespace string `json:"targetNamespace,omitempty"`

	// Condições que acionam o rollback
	Conditions []RollbackCondition `json:"conditions"`

	// Revisão para a qual fazer rollback (0 para a revisão anterior)
	TargetRevision int32 `json:"targetRevision,omitempty"`

	// Intervalo de verificação em segundos
	CheckInterval int32 `json:"checkInterval,omitempty"`

	// Número máximo de tentativas de rollback
	MaxAttempts int32 `json:"maxAttempts,omitempty"`

	// Tempo de espera após rollback antes de permitir nova verificação (em segundos)
	CooldownPeriod int32 `json:"cooldownPeriod,omitempty"`
}

// RollbackCondition define uma condição que aciona o rollback
type RollbackCondition struct {
	// Tipo de condição (Progressing, Available, etc.)
	Type string `json:"type"`

	// Status esperado (True, False, Unknown)
	Status string `json:"status"`

	// Duração mínima da condição antes de acionar o rollback (em segundos)
	MinDuration int32 `json:"minDuration,omitempty"`

	// Porcentagem mínima de pods não disponíveis para acionar rollback
	MinUnavailablePercent int32 `json:"minUnavailablePercent,omitempty"`

	// Número máximo de reinícios de contêiner antes de acionar rollback
	MaxContainerRestarts int32 `json:"maxContainerRestarts,omitempty"`
}

// RollbackPolicyStatus define o status observado de uma RollbackPolicy
type RollbackPolicyStatus struct {
	// Número de vezes que esta política foi aplicada
	AppliedCount int32 `json:"appliedCount,omitempty"`

	// Última vez que esta política foi aplicada
	LastAppliedTime *metav1.Time `json:"lastAppliedTime,omitempty"`

	// Status da última aplicação (Succeeded, Failed)
	LastAppliedStatus string `json:"lastAppliedStatus,omitempty"`

	// Mensagem da última aplicação
	LastAppliedMessage string `json:"lastAppliedMessage,omitempty"`

	// Recursos atualmente monitorados por esta política
	MonitoredResources []string `json:"monitoredResources,omitempty"`

	// Revisão atual dos recursos monitorados
	CurrentRevisions map[string]int32 `json:"currentRevisions,omitempty"`

	// Revisões para as quais foi feito rollback
	RollbackRevisions map[string]int32 `json:"rollbackRevisions,omitempty"`
}

// +kubebuilder:object:root=true

// RollbackPolicyList é uma lista de RollbackPolicy
type RollbackPolicyList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`

	Items []RollbackPolicy `json:"items"`
}
