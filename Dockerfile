# Dockerfile
# Stage 1: Build Frontend
FROM node:23-alpine as react_frontend-builder
WORKDIR /react_frontend
COPY react_frontend/package*.json ./
RUN npm install
COPY react_frontend/ ./
RUN npm run build

# Stage 2: Build Backend
FROM golang:1.23.4-alpine as go_server-builder
WORKDIR /go_server
COPY go_server/go.* ./
RUN go mod download
COPY go_server/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Stage 3: Final Image
FROM nginx:alpine
# Copy react_frontend build
COPY --from=react_frontend-builder /react_frontend/dist /usr/share/nginx/html
# Copy go_server binary
COPY --from=go_server-builder /go_server/main /app/main
# Stage 2: COPY PYTHON SERVICE
COPY face_recognition_service ./face_recognition_service
# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
# Install supervisor to manage multiple processes
RUN apk add --no-cache supervisor

# Create supervisor configuration
RUN mkdir -p /etc/supervisor.d/
COPY supervisor/supervisord.conf /etc/supervisord.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

