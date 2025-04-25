package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// DeepCopyInto copia todos os campos de uma RollbackPolicy para outra
func (in *RollbackPolicy) DeepCopyInto(out *RollbackPolicy) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	in.Spec.DeepCopyInto(&out.Spec)
	in.Status.DeepCopyInto(&out.Status)
}

// DeepCopy cria uma nova RollbackPolicy copiando a original
func (in *RollbackPolicy) DeepCopy() *RollbackPolicy {
	if in == nil {
		return nil
	}
	out := new(RollbackPolicy)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject cria uma cópia do objeto
func (in *RollbackPolicy) DeepCopyObject() Object {
	return in.DeepCopy()
}

// DeepCopyInto copia todos os campos de uma RollbackPolicyList para outra
func (in *RollbackPolicyList) DeepCopyInto(out *RollbackPolicyList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]RollbackPolicy, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

// DeepCopy cria uma nova RollbackPolicyList copiando a original
func (in *RollbackPolicyList) DeepCopy() *RollbackPolicyList {
	if in == nil {
		return nil
	}
	out := new(RollbackPolicyList)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject cria uma cópia do objeto
func (in *RollbackPolicyList) DeepCopyObject() Object {
	return in.DeepCopy()
}

// DeepCopyInto copia todos os campos de uma RollbackPolicySpec para outra
func (in *RollbackPolicySpec) DeepCopyInto(out *RollbackPolicySpec) {
	*out = *in
	in.Selector.DeepCopyInto(&out.Selector)
	if in.Conditions != nil {
		in, out := &in.Conditions, &out.Conditions
		*out = make([]RollbackCondition, len(*in))
		copy(*out, *in)
	}
}

// DeepCopyInto copia todos os campos de uma RollbackPolicyStatus para outra
func (in *RollbackPolicyStatus) DeepCopyInto(out *RollbackPolicyStatus) {
	*out = *in
	if in.LastAppliedTime != nil {
		in, out := &in.LastAppliedTime, &out.LastAppliedTime
		*out = (*in).DeepCopy()
	}
	if in.MonitoredResources != nil {
		in, out := &in.MonitoredResources, &out.MonitoredResources
		*out = make([]string, len(*in))
		copy(*out, *in)
	}
	if in.CurrentRevisions != nil {
		in, out := &in.CurrentRevisions, &out.CurrentRevisions
		*out = make(map[string]int32, len(*in))
		for key, val := range *in {
			(*out)[key] = val
		}
	}
	if in.RollbackRevisions != nil {
		in, out := &in.RollbackRevisions, &out.RollbackRevisions
		*out = make(map[string]int32, len(*in))
		for key, val := range *in {
			(*out)[key] = val
		}
	}
}

// Object é uma interface para objetos que podem ser copiados
type Object interface {
	metav1.Object
	runtime.Object
}

// runtime é um pacote fictício para satisfazer a interface Object
type runtime struct{}

// Object é uma interface para objetos runtime
type Object interface {
	DeepCopyObject() Object
}
