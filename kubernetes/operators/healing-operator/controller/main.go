package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/kubernetes/scheme"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/klog/v2"

	healingv1 "autocura_cognitiva/kubernetes/operators/healing-operator/api/v1" // <-- CORRIGIDO (verifique se este também está assim)
	"autocura_cognitiva/kubernetes/operators/healing-operator/controllers" // <-- CORRIGIDO
)

var (
	masterURL  string
	kubeconfig string
)

func main() {
	klog.InitFlags(nil)
	flag.Parse()

	// Configuração do cliente Kubernetes
	cfg, err := getConfig()
	if err != nil {
		klog.Fatalf("Error building kubeconfig: %s", err.Error())
	}

	kubeClient, err := kubernetes.NewForConfig(cfg)
	if err != nil {
		klog.Fatalf("Error building kubernetes clientset: %s", err.Error())
	}

	// Registrar o CRD HealingPolicy no esquema
	schemeBuilder := runtime.NewSchemeBuilder(func(scheme *runtime.Scheme) error {
		scheme.AddKnownTypes(healingv1.GroupVersion,
			&healingv1.HealingPolicy{},
			&healingv1.HealingPolicyList{},
		)
		return nil
	})
	
	err = schemeBuilder.AddToScheme(scheme.Scheme)
	if err != nil {
		klog.Fatalf("Error adding HealingPolicy to scheme: %s", err.Error())
	}

	// Criar o controlador
	controller := controllers.NewHealingController(kubeClient, cfg)

	// Configurar canal para sinais de término
	stopCh := setupSignalHandler()

	// Iniciar o controlador
	if err = controller.Run(2, stopCh); err != nil {
		klog.Fatalf("Error running controller: %s", err.Error())
	}
}

// getConfig retorna a configuração do cliente Kubernetes
func getConfig() (*rest.Config, error) {
	if len(kubeconfig) > 0 {
		return clientcmd.BuildConfigFromFlags(masterURL, kubeconfig)
	}
	return rest.InClusterConfig()
}

// setupSignalHandler configura um canal para capturar sinais de término
func setupSignalHandler() <-chan struct{} {
	stopCh := make(chan struct{})
	c := make(chan os.Signal, 2)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		close(stopCh)
		<-c
		os.Exit(1) // segundo sinal, saída forçada
	}()

	return stopCh
}

func init() {
	flag.StringVar(&kubeconfig, "kubeconfig", "", "Path to a kubeconfig. Only required if out-of-cluster.")
	flag.StringVar(&masterURL, "master", "", "The address of the Kubernetes API server. Overrides any value in kubeconfig. Only required if out-of-cluster.")
}
