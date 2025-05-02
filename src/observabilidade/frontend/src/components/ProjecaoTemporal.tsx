import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface ProjecaoTemporalProps {
  dados: {
    timestamp: number;
    valor: number;
    projecao: number;
  }[];
}

const ProjecaoTemporal: React.FC<ProjecaoTemporalProps> = ({ dados }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !dados.length) return;

    const margin = { top: 20, right: 30, bottom: 30, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Limpa o SVG anterior
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Escalas
    const x = d3.scaleTime()
      .domain(d3.extent(dados, d => new Date(d.timestamp)) as [Date, Date])
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(dados, d => Math.max(d.valor, d.projecao)) as number])
      .range([height, 0]);

    // Adiciona eixos
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    svg.append('g')
      .call(d3.axisLeft(y));

    // Linha para dados reais
    svg.append('path')
      .datum(dados)
      .attr('fill', 'none')
      .attr('stroke', 'steelblue')
      .attr('stroke-width', 1.5)
      .attr('d', d3.line()
        .x(d => x(new Date(d.timestamp)))
        .y(d => y(d.valor))
      );

    // Linha para projeções
    svg.append('path')
      .datum(dados)
      .attr('fill', 'none')
      .attr('stroke', 'red')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '5,5')
      .attr('d', d3.line()
        .x(d => x(new Date(d.timestamp)))
        .y(d => y(d.projecao))
      );

    // Adiciona pontos para dados reais
    svg.selectAll('.dot')
      .data(dados)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => x(new Date(d.timestamp)))
      .attr('cy', d => y(d.valor))
      .attr('r', 3)
      .style('fill', 'steelblue');

    // Adiciona pontos para projeções
    svg.selectAll('.projecao-dot')
      .data(dados)
      .enter()
      .append('circle')
      .attr('class', 'projecao-dot')
      .attr('cx', d => x(new Date(d.timestamp)))
      .attr('cy', d => y(d.projecao))
      .attr('r', 3)
      .style('fill', 'red');

    // Adiciona legenda
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 100}, 0)`);

    legend.append('rect')
      .attr('width', 10)
      .attr('height', 10)
      .attr('fill', 'steelblue');

    legend.append('text')
      .attr('x', 20)
      .attr('y', 10)
      .text('Dados Reais')
      .style('font-size', '12px');

    legend.append('rect')
      .attr('y', 20)
      .attr('width', 10)
      .attr('height', 10)
      .attr('fill', 'red');

    legend.append('text')
      .attr('x', 20)
      .attr('y', 30)
      .text('Projeções')
      .style('font-size', '12px');

  }, [dados]);

  return <svg ref={svgRef} />;
};

export default ProjecaoTemporal; 