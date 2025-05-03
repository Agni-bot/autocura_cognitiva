FROM golang:1.18-alpine AS builder

WORKDIR /workspace

# Copiar arquivos Go Modules
COPY go.mod go.sum ./
RUN go mod download

# Criar diretórios necessários
RUN mkdir -p controller api/v1

# Copiar o código-fonte
COPY api/ api/
COPY controller/ controller/

# Compilar
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o rollback-operator controller/main.go

# Imagem final
FROM alpine:3.16

WORKDIR /
COPY --from=builder /workspace/rollback-operator .
USER 65532:65532

ENTRYPOINT ["/rollback-operator"]
