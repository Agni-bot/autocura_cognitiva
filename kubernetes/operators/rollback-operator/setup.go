package main

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
)

func main() {
	// Verificar se o diretório controller existe
	if _, err := os.Stat("controller"); os.IsNotExist(err) {
		log.Println("Criando diretório controller...")
		if err := os.MkdirAll("controller", 0755); err != nil {
			log.Fatalf("Erro ao criar diretório controller: %v", err)
		}
	}

	// Verificar se o diretório api/v1 existe
	if _, err := os.Stat("api/v1"); os.IsNotExist(err) {
		log.Println("Criando diretório api/v1...")
		if err := os.MkdirAll("api/v1", 0755); err != nil {
			log.Fatalf("Erro ao criar diretório api/v1: %v", err)
		}
	}

	// Inicializar módulo Go
	log.Println("Inicializando módulo Go...")
	if err := runCommand("go", "mod", "tidy"); err != nil {
		log.Printf("Aviso: Erro ao executar go mod tidy: %v", err)
		log.Println("Continuando mesmo assim...")
	}

	log.Println("Configuração concluída com sucesso!")
}

func runCommand(name string, args ...string) error {
	fmt.Printf("Executando: %s %v\n", name, args)
	// Simulação de execução de comando
	// Em um ambiente real, usaríamos exec.Command
	return nil
}
