FROM golang:1.18-alpine AS builder

WORKDIR /app

# 1. Copia apenas os arquivos de dependências primeiro (para aproveitar cache de camadas)
COPY go.mod go.sum ./
# 2. Baixa dependências e sincroniza módulos
RUN go mod download && go mod verify

# 3. Copia o restante do código
COPY . .

# 4. Compila o projeto
RUN go build -o healing-operator ./controller/

# 5. Cria etapa final leve
FROM alpine:3.16
WORKDIR /app
COPY --from=builder /app/healing-operator .

EXPOSE 8080
CMD ["./healing-operator"]