FROM golang:1.18-alpine

WORKDIR /app

COPY . .

RUN go mod download
RUN go build -o healing-operator ./controller/

EXPOSE 8080

CMD ["./healing-operator"]
