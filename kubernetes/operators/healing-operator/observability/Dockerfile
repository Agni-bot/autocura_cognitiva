FROM golang:1.18-alpine as builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o observability-server

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/observability-server .
COPY --from=builder /app/web ./web

EXPOSE 8080

CMD ["./observability-server"] 