FROM golang:1.18-alpine AS builder

WORKDIR /app

# Copia primeiro os arquivos de módulo
COPY go.mod go.sum ./
RUN go mod download

# Copia o restante do código
COPY . .

# Compila o projeto
RUN go build -o healing-operator ./main.go

# Etapa final
FROM alpine:3.16
WORKDIR /app
COPY --from=builder /app/healing-operator .

EXPOSE 8080
CMD ["./healing-operator"]