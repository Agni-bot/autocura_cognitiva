package v1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    "k8s.io/apimachinery/pkg/runtime/schema"
)

// GroupVersion é a versão da API para o pacote healing
var GroupVersion = schema.GroupVersion{Group: "healing.autocura-cognitiva.io", Version: "v1"}

// SchemeBuilder é usado para adicionar tipos Go ao esquema
var SchemeBuilder = runtime.NewSchemeBuilder(addKnownTypes)

// AddToScheme adiciona os tipos deste grupo ao esquema fornecido
var AddToScheme = SchemeBuilder.AddToScheme

// addKnownTypes adiciona os tipos definidos neste pacote ao esquema
func addKnownTypes(scheme *runtime.Scheme) error {
    scheme.AddKnownTypes(
        GroupVersion,
        &HealingPolicy{},
        &HealingPolicyList{},
    )
    metav1.AddToGroupVersion(scheme, GroupVersion)
    return nil
}

// HealingPolicy define uma política de healing para recursos Kubernetes
type HealingPolicy struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   HealingPolicySpec   `json:"spec,omitempty"`
	Status HealingPolicyStatus `json:"status,omitempty"`
}
// +kubebuilder:object:root=true
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type HealingPolicy struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    // ... (campos existentes)
}

// +kubebuilder:object:root=true
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
type HealingPolicyList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []HealingPolicy `json:"items"`
}
// HealingPolicySpec define a especificação desejada para uma HealingPolicy
type HealingPolicySpec struct {
	// Seletor para os recursos alvo desta política
	Selector metav1.LabelSelector `json:"selector"`

	// Tipo de recurso alvo (Pod, Deployment, etc.)
	TargetKind string `json:"targetKind"`

	// Namespace alvo (vazio para todos os namespaces)
	TargetNamespace string `json:"targetNamespace,omitempty"`

	// Condições que acionam o healing
	Conditions []HealingCondition `json:"conditions"`

	// Ações a serem executadas quando as condições são atendidas
	Actions []HealingAction `json:"actions"`

	// Intervalo de verificação em segundos
	CheckInterval int32 `json:"checkInterval,omitempty"`

	// Número máximo de tentativas de healing
	MaxAttempts int32 `json:"maxAttempts,omitempty"`
}

// HealingCondition define uma condição que aciona o healing
type HealingCondition struct {
	// Tipo de condição (Ready, Available, etc.)
	Type string `json:"type"`

	// Status esperado (True, False, Unknown)
	Status string `json:"status"`

	// Duração mínima da condição antes de acionar o healing (em segundos)
	MinDuration int32 `json:"minDuration,omitempty"`
}

// HealingAction define uma ação de healing a ser executada
type HealingAction struct {
	// Tipo de ação (Restart, Scale, Recreate, etc.)
	Type string `json:"type"`

	// Parâmetros específicos da ação
	Params map[string]string `json:"params,omitempty"`
}

// HealingPolicyStatus define o status observado de uma HealingPolicy
type HealingPolicyStatus struct {
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
}

// HealingPolicyList é uma lista de HealingPolicy
type HealingPolicyList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`

	Items []HealingPolicy `json:"items"`
}
