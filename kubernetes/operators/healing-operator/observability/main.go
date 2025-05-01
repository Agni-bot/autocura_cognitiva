package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type ObservabilityServer struct {
	clientset *kubernetes.Clientset
	metrics   map[string]interface{}
}

func NewObservabilityServer() (*ObservabilityServer, error) {
	config, err := rest.InClusterConfig()
	if err != nil {
		return nil, fmt.Errorf("erro ao criar configuração in-cluster: %v", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("erro ao criar clientset: %v", err)
	}

	return &ObservabilityServer{
		clientset: clientset,
		metrics:   make(map[string]interface{}),
	}, nil
}

func (s *ObservabilityServer) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("erro ao atualizar para websocket: %v", err)
		return
	}
	defer conn.Close()

	// Loop de atualização de métricas
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			// Coletar métricas
			s.collectMetrics()

			// Enviar métricas para o cliente
			if err := conn.WriteJSON(s.metrics); err != nil {
				log.Printf("erro ao enviar métricas: %v", err)
				return
			}
		}
	}
}

func (s *ObservabilityServer) collectMetrics() {
	// Coletar métricas do cluster
	pods, err := s.clientset.CoreV1().Pods("").List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		log.Printf("erro ao listar pods: %v", err)
		return
	}

	// Contar pods por status
	podStatus := map[string]int{
		"running":  0,
		"pending":  0,
		"failed":   0,
		"unknown":  0,
	}

	for _, pod := range pods.Items {
		switch pod.Status.Phase {
		case "Running":
			podStatus["running"]++
		case "Pending":
			podStatus["pending"]++
		case "Failed":
			podStatus["failed"]++
		default:
			podStatus["unknown"]++
		}
	}

	// Coletar métricas de recursos
	nodes, err := s.clientset.CoreV1().Nodes().List(context.TODO(), metav1.ListOptions{})
	if err != nil {
		log.Printf("erro ao listar nodes: %v", err)
		return
	}

	// Calcular uso de recursos
	var totalCPU, totalMemory, usedCPU, usedMemory int64
	for _, node := range nodes.Items {
		totalCPU += node.Status.Capacity.Cpu().MilliValue()
		totalMemory += node.Status.Capacity.Memory().Value()
		usedCPU += node.Status.Allocatable.Cpu().MilliValue()
		usedMemory += node.Status.Allocatable.Memory().Value()
	}

	// Atualizar métricas
	s.metrics["timestamp"] = time.Now().Unix()
	s.metrics["pods"] = map[string]interface{}{
		"total":    len(pods.Items),
		"status":   podStatus,
	}
	s.metrics["resources"] = map[string]interface{}{
		"cpu": map[string]interface{}{
			"total": totalCPU,
			"used":  usedCPU,
			"usage": float64(usedCPU) / float64(totalCPU) * 100,
		},
		"memory": map[string]interface{}{
			"total": totalMemory,
			"used":  usedMemory,
			"usage": float64(usedMemory) / float64(totalMemory) * 100,
		},
	}
}

func main() {
	server, err := NewObservabilityServer()
	if err != nil {
		log.Fatalf("erro ao criar servidor: %v", err)
	}

	// Servir arquivos estáticos
	fs := http.FileServer(http.Dir("./web"))
	http.Handle("/", fs)

	// Endpoints da API
	http.HandleFunc("/ws", server.handleWebSocket)
	http.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		server.collectMetrics()
		json.NewEncoder(w).Encode(server.metrics)
	})

	log.Println("Servidor de observabilidade iniciado na porta 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
} 