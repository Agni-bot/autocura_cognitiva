package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
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

// DeepCopyInto copia o receptor em out. in deve ser não-nulo.
func (in *Healing) DeepCopyInto(out *Healing) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	out.Spec = in.Spec
	out.Status = in.Status
}

// DeepCopy cria uma cópia profunda do Healing
func (in *Healing) DeepCopy() *Healing {
	if in == nil {
		return nil
	}
	out := new(Healing)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject cria uma cópia profunda do objeto
func (in *Healing) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
}

//+kubebuilder:object:root=true

// HealingList contém uma lista de Healing
type HealingList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Healing `json:"items"`
}

// DeepCopyInto copia o receptor em out. in deve ser não-nulo.
func (in *HealingList) DeepCopyInto(out *HealingList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]Healing, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

// DeepCopy cria uma cópia profunda do HealingList
func (in *HealingList) DeepCopy() *HealingList {
	if in == nil {
		return nil
	}
	out := new(HealingList)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject cria uma cópia profunda do objeto
func (in *HealingList) DeepCopyObject() runtime.Object {
	if c := in.DeepCopy(); c != nil {
		return c
	}
	return nil
} 