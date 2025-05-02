FROM python:3.9-slim

WORKDIR /app

# Cria diretório para visualizações
RUN mkdir -p /app/visualizacoes && chmod 777 /app/visualizacoes

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configura logging para arquivo
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/observabilidade.log

# Cria diretório de logs
RUN mkdir -p /app/logs && chmod 777 /app/logs

EXPOSE 8080

CMD ["python", "observabilidade.py"]
