package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// RollbackPolicySpec define a especificação desejada para uma política de rollback
type RollbackPolicySpec struct {
	// Seletor para os recursos a serem monitorados
	Selector metav1.LabelSelector `json:"selector"`

	// Condições que devem ser satisfeitas para acionar o rollback
	Conditions []RollbackCondition `json:"conditions,omitempty"`

	// Intervalo de verificação em segundos
	CheckInterval int32 `json:"checkInterval,omitempty"`

	// Versão para a qual fazer rollback
	RollbackToRevision string `json:"rollbackToRevision,omitempty"`
}

// RollbackCondition define uma condição para acionar o rollback
type RollbackCondition struct {
	// Tipo da condição
	Type string `json:"type"`

	// Valor da condição
	Value string `json:"value"`

	// Operador de comparação
	Operator string `json:"operator"`
}

// RollbackPolicyStatus define o status observado de uma política de rollback
type RollbackPolicyStatus struct {
	// Última vez que o rollback foi aplicado
	LastAppliedTime *metav1.Time `json:"lastAppliedTime,omitempty"`

	// Status da última aplicação
	LastAppliedStatus string `json:"lastAppliedStatus,omitempty"`

	// Mensagem da última aplicação
	LastAppliedMessage string `json:"lastAppliedMessage,omitempty"`

	// Número de vezes que o rollback foi aplicado
	AppliedCount int32 `json:"appliedCount,omitempty"`

	// Recursos sendo monitorados
	MonitoredResources []string `json:"monitoredResources,omitempty"`

	// Revisões atuais dos recursos
	CurrentRevisions map[string]int32 `json:"currentRevisions,omitempty"`

	// Revisões para rollback dos recursos
	RollbackRevisions map[string]int32 `json:"rollbackRevisions,omitempty"`
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

// +kubebuilder:object:root=true

// RollbackPolicyList é uma lista de RollbackPolicy
type RollbackPolicyList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`

	Items []RollbackPolicy `json:"items"`
}
