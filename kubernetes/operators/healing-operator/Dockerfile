FROM golang:1.18-alpine AS builder

WORKDIR /workspace

# Copiar arquivos Go Modules
COPY go.mod go.sum ./
RUN go mod download

# Copiar o código-fonte
COPY main.go main.go
COPY api/ api/
COPY controllers/ controllers/

# Instalar controller-gen
RUN go install sigs.k8s.io/controller-tools/cmd/controller-gen@v0.9.0

# Gerar código CRD e DeepCopy
RUN controller-gen object:headerFile="hack/boilerplate.go.txt" paths="./..."
RUN controller-gen crd paths="./..." output:crd:artifacts:config=config/crd/bases

# Compilar
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o manager main.go

# Imagem final
FROM alpine:3.16

WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532

ENTRYPOINT ["/manager"]
