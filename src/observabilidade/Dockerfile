FROM python:3.9-slim

WORKDIR /app

# Cria diretórios necessários
RUN mkdir -p /app/visualizacoes && \
    mkdir -p /app/logs && \
    mkdir -p /app/templates && \
    chmod 777 /app/visualizacoes && \
    chmod 777 /app/logs && \
    chmod 777 /app/templates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configura logging para arquivo
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/observabilidade.log

EXPOSE 8080

CMD ["python", "observabilidade.py"]
