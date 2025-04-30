FROM python:3.9-slim

WORKDIR /app

# Definir a variável de ambiente para o protobuf
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Instalar primeiro o protobuf e depois o tensorflow
RUN pip install --no-cache-dir protobuf==3.20.3 tensorflow==2.7.0

COPY requirements.txt .
# Remover tensorflow e protobuf do requirements.txt antes de instalar
RUN sed -i '/tensorflow/d; /protobuf/d' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "gerador_acoes.py"]
