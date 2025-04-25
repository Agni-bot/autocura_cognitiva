// Package v1 contém as definições de API para o operador rollback
// +kubebuilder:object:generate=true
// +groupName=rollback.autocura-cognitiva.io
package v1

import (
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

var (
	// GroupVersion é a versão da API para o pacote rollback
	GroupVersion = schema.GroupVersion{Group: "rollback.autocura-cognitiva.io", Version: "v1"}

	// SchemeBuilder é usado para adicionar tipos Go ao esquema
	SchemeBuilder = &scheme.Builder{GroupVersion: GroupVersion}

	// AddToScheme adiciona os tipos deste grupo ao esquema fornecido
	AddToScheme = SchemeBuilder.AddToScheme
)

func init() {
	SchemeBuilder.Register(&RollbackPolicy{}, &RollbackPolicyList{})
}
