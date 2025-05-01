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
	// Implementar coleta de métricas do cluster
	// Por enquanto, apenas um exemplo
	s.metrics["timestamp"] = time.Now().Unix()
	s.metrics["pods"] = map[string]interface{}{
		"total":    10,
		"running":  8,
		"pending":  1,
		"failed":   1,
	}
}

func main() {
	server, err := NewObservabilityServer()
	if err != nil {
		log.Fatalf("erro ao criar servidor: %v", err)
	}

	http.HandleFunc("/ws", server.handleWebSocket)
	http.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		server.collectMetrics()
		json.NewEncoder(w).Encode(server.metrics)
	})

	log.Println("Servidor de observabilidade iniciado na porta 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
} 