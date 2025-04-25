FROM golang:1.18-alpine AS builder

WORKDIR /app

# 1. Copia arquivos de dependências
COPY go.mod go.sum ./
# 2. Baixa e sincroniza dependências
RUN go mod download && go mod tidy

# 3. Copia o código-fonte
COPY . .

# 4. Compila o projeto (AGORA na raiz, pois main.go foi movido)
RUN go build -o healing-operator ./main.go

# 5. Etapa de execução leve
FROM alpine:3.16
WORKDIR /app
COPY --from=builder /app/healing-operator .

EXPOSE 8080
CMD ["./healing-operator"]