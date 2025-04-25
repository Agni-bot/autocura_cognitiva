package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// DeepCopyInto copia todos os campos de uma HealingPolicy para outra
func (in *HealingPolicy) DeepCopyInto(out *HealingPolicy) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ObjectMeta.DeepCopyInto(&out.ObjectMeta)
	in.Spec.DeepCopyInto(&out.Spec)
	in.Status.DeepCopyInto(&out.Status)
}

// DeepCopy cria uma nova HealingPolicy copiando a original
func (in *HealingPolicy) DeepCopy() *HealingPolicy {
	if in == nil {
		return nil
	}
	out := new(HealingPolicy)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject cria uma cópia do objeto
func (in *HealingPolicy) DeepCopyObject() Object {
	return in.DeepCopy()
}

// DeepCopyInto copia todos os campos de uma HealingPolicyList para outra
func (in *HealingPolicyList) DeepCopyInto(out *HealingPolicyList) {
	*out = *in
	out.TypeMeta = in.TypeMeta
	in.ListMeta.DeepCopyInto(&out.ListMeta)
	if in.Items != nil {
		in, out := &in.Items, &out.Items
		*out = make([]HealingPolicy, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

// DeepCopy cria uma nova HealingPolicyList copiando a original
func (in *HealingPolicyList) DeepCopy() *HealingPolicyList {
	if in == nil {
		return nil
	}
	out := new(HealingPolicyList)
	in.DeepCopyInto(out)
	return out
}

// DeepCopyObject cria uma cópia do objeto
func (in *HealingPolicyList) DeepCopyObject() Object {
	return in.DeepCopy()
}

// DeepCopyInto copia todos os campos de uma HealingPolicySpec para outra
func (in *HealingPolicySpec) DeepCopyInto(out *HealingPolicySpec) {
	*out = *in
	in.Selector.DeepCopyInto(&out.Selector)
	if in.Conditions != nil {
		in, out := &in.Conditions, &out.Conditions
		*out = make([]HealingCondition, len(*in))
		copy(*out, *in)
	}
	if in.Actions != nil {
		in, out := &in.Actions, &out.Actions
		*out = make([]HealingAction, len(*in))
		for i := range *in {
			(*in)[i].DeepCopyInto(&(*out)[i])
		}
	}
}

// DeepCopyInto copia todos os campos de uma HealingAction para outra
func (in *HealingAction) DeepCopyInto(out *HealingAction) {
	*out = *in
	if in.Params != nil {
		in, out := &in.Params, &out.Params
		*out = make(map[string]string, len(*in))
		for key, val := range *in {
			(*out)[key] = val
		}
	}
}

// DeepCopyInto copia todos os campos de uma HealingPolicyStatus para outra
func (in *HealingPolicyStatus) DeepCopyInto(out *HealingPolicyStatus) {
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
