FROM golang:1.18-alpine

WORKDIR /app

COPY . .

RUN go mod download
RUN go build -o rollback-operator ./controller/

EXPOSE 8080

CMD ["./rollback-operator"]
