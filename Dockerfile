
# Stage 1: Build Frontend
FROM node:23-alpine as react_frontend-builder
WORKDIR /react_frontend
COPY react_frontend/package*.json ./
RUN npm install
COPY react_frontend/ ./
RUN npm run build

# Stage 2: Install Python Dependencies
FROM python:3.11 as python_service-builder
RUN apt-get update && apt-get install -y \
    cmake \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    libgl1-mesa-glx
RUN pip install --no-cache-dir face_recognition dlib

WORKDIR /face_recognition_service
COPY face_recognition_service/ /face_recognition_service

# Stage 3: Build Backend
FROM golang:1.23.4-alpine as go_server-builder
WORKDIR /go_server
COPY go_server/go.* ./
RUN go mod download
COPY go_server/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Stage 4: Final Image
FROM nginx:alpine
RUN apk add --no-cache supervisor

# Copy React build
COPY --from=react_frontend-builder /react_frontend/dist /usr/share/nginx/html

# Copy Python environment and service
COPY --from=python_service-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=python_service-builder /face_recognition_service /face_recognition_service

# Copy Go server
COPY --from=go_server-builder /go_server/main /app/main

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy Supervisor config
COPY supervisor/supervisord.conf /etc/supervisord.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]