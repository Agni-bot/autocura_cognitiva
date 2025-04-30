FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configura o ambiente Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

EXPOSE 8080

CMD ["python", "-u", "monitoramento.py"]
