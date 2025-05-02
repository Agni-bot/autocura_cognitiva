import React, { useState, useEffect } from 'react';
import VisualizacaoHolografica from './components/VisualizacaoHolografica';
import ProjecaoTemporal from './components/ProjecaoTemporal';
import io from 'socket.io-client';

const socket = io('http://localhost:3001'); // Ajuste a URL conforme necessário

const App: React.FC = () => {
  const [dadosSistema, setDadosSistema] = useState<any>(null);
  const [dadosTemporais, setDadosTemporais] = useState<any[]>([]);

  useEffect(() => {
    // Conecta ao WebSocket para receber dados em tempo real
    socket.on('dadosSistema', (dados) => {
      setDadosSistema(dados);
    });

    socket.on('dadosTemporais', (dados) => {
      setDadosTemporais(prev => [...prev, dados].slice(-100)); // Mantém os últimos 100 pontos
    });

    return () => {
      socket.off('dadosSistema');
      socket.off('dadosTemporais');
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header style={{ padding: '1rem', background: '#333', color: 'white' }}>
        <h1>Sistema de Observabilidade 4D</h1>
      </header>
      
      <main style={{ display: 'flex', flex: 1, gap: '1rem', padding: '1rem' }}>
        <div style={{ flex: 2 }}>
          <h2>Visualização Holográfica</h2>
          <VisualizacaoHolografica dados={dadosSistema} />
        </div>
        
        <div style={{ flex: 1 }}>
          <h2>Projeção Temporal</h2>
          <ProjecaoTemporal dados={dadosTemporais} />
        </div>
      </main>
    </div>
  );
};

export default App; 