FROM golang:1.18-alpine

WORKDIR /app

# Copiar módulo e baixar dependências
COPY go.mod go.sum ./
RUN go mod download

# Copiar código-fonte
COPY . .

# Compilar o operador
RUN go build -o healing-operator ./controller/main.go

EXPOSE 8080

CMD ["./healing-operator"]