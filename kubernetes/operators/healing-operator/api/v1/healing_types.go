package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// HealingSpec define o estado desejado do Healing
type HealingSpec struct {
	// Intervalo de verificação em segundos
	CheckInterval int32 `json:"checkInterval,omitempty"`
}

// HealingStatus define o estado observado do Healing
type HealingStatus struct {
	// Última vez que o healing foi aplicado
	LastAppliedTime *metav1.Time `json:"lastAppliedTime,omitempty"`
	// Status da última aplicação
	LastAppliedStatus string `json:"lastAppliedStatus,omitempty"`
	// Mensagem da última aplicação
	LastAppliedMessage string `json:"lastAppliedMessage,omitempty"`
	// Número de vezes que o healing foi aplicado
	AppliedCount int32 `json:"appliedCount,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// Healing é o Schema para a API healing
type Healing struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   HealingSpec   `json:"spec,omitempty"`
	Status HealingStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// HealingList contém uma lista de Healing
type HealingList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Healing `json:"items"`
} 