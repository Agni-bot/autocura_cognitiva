import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import { promisify } from 'util';
import { exec } from 'child_process';

const execAsync = promisify(exec);

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Função para obter métricas do sistema
async function getSystemMetrics() {
  try {
    // Exemplo: obtendo uso de CPU
    const { stdout: cpuOutput } = await execAsync('kubectl top pod -n monitoring');
    
    // Exemplo: obtendo métricas do Prometheus
    const prometheusResponse = await fetch('http://prometheus.monitoring:9090/api/v1/query?query=up');
    const prometheusData = await prometheusResponse.json();
    
    return {
      timestamp: Date.now(),
      cpu: cpuOutput,
      prometheus: prometheusData
    };
  } catch (error) {
    console.error('Erro ao obter métricas:', error);
    return null;
  }
}

// Função para gerar projeções temporais
function generateTemporalProjections(currentData: any) {
  // Simulação de projeções baseadas em dados atuais
  return {
    timestamp: Date.now(),
    valor: currentData?.cpu || 0,
    projecao: (currentData?.cpu || 0) * (1 + Math.random() * 0.1) // Simulação de crescimento
  };
}

// Intervalo para atualização de dados
setInterval(async () => {
  const metrics = await getSystemMetrics();
  if (metrics) {
    io.emit('dadosSistema', metrics);
    
    const projections = generateTemporalProjections(metrics);
    io.emit('dadosTemporais', projections);
  }
}, 5000); // Atualiza a cada 5 segundos

// Inicia o servidor
const PORT = 3001;
server.listen(PORT, () => {
  console.log(`Servidor WebSocket rodando na porta ${PORT}`);
}); 