// Função para carregar métricas
async function carregarMetricas() {
    try {
        const response = await fetch('/api/metricas');
        const metricas = await response.json();
        
        const container = document.getElementById('metricas-container');
        container.innerHTML = `
            <div class="metric-item">
                <h5>Throughput</h5>
                <p class="metric-value">${metricas.throughput} ops/s</p>
            </div>
            <div class="metric-item">
                <h5>Taxa de Erro</h5>
                <p class="metric-value">${metricas.taxa_erro}%</p>
            </div>
            <div class="metric-item">
                <h5>Latência</h5>
                <p class="metric-value">${metricas.latencia} ms</p>
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar métricas:', error);
    }
}

// Função para carregar alertas
async function carregarAlertas() {
    try {
        const response = await fetch('/api/alertas');
        const alertas = await response.json();
        
        const container = document.getElementById('alertas-container');
        container.innerHTML = alertas.map(alerta => `
            <div class="alert ${alerta.severidade}">
                <h6>${alerta.titulo}</h6>
                <p>${alerta.descricao}</p>
                <small>${new Date(alerta.timestamp).toLocaleString()}</small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar alertas:', error);
    }
}

// Função para carregar ações
async function carregarAcoes() {
    try {
        const response = await fetch('/api/acoes');
        const acoes = await response.json();
        
        const container = document.getElementById('acoes-container');
        container.innerHTML = acoes.map(acao => `
            <div class="acao-item">
                <h6>${acao.tipo}</h6>
                <p>${acao.descricao}</p>
                <small>Prioridade: ${acao.prioridade}</small>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar ações:', error);
    }
}

// Função para inicializar o gráfico
function inicializarGrafico() {
    const ctx = document.getElementById('performance-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Throughput',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Função para atualizar o dashboard
async function atualizarDashboard() {
    await carregarMetricas();
    await carregarAlertas();
    await carregarAcoes();
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    inicializarGrafico();
    atualizarDashboard();
    
    // Atualizar a cada 30 segundos
    setInterval(atualizarDashboard, 30000);
}); 