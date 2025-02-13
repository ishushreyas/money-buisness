# Money Business

This repository contains a full-stack application for face recognition. The application is composed of a React frontend, a Go backend, and a Python microservice for face recognition. The services are orchestrated using Docker and Nginx.

## Services

### React Frontend

The frontend is built using React and Vite. It allows users to upload images for face recognition.

- **Directory**: `react_frontend`
- **Entry Point**: `react_frontend/src/main.jsx`
- **Build Command**: `npm run build`
- **Development Command**: `npm run dev`

### Go Backend

The backend is built using Go. It handles file uploads and forwards them to the Python microservice for face recognition.

- **Directory**: `go_server`
- **Entry Point**: `go_server/main.go`
- **Build Command**: `go build -o main .`
- **Run Command**: `./main`

### Python Microservice

The microservice is built using Flask and the `face_recognition` library. It processes images and returns recognized faces.

- **Directory**: `face_recognition_service`
- **Entry Point**: `face_recognition_service/face_recognition_service.py`
- **Run Command**: `python3 face_recognition_service.py`

### Nginx

Nginx is used as a reverse proxy to route requests to the appropriate services.

- **Directory**: `nginx`
- **Configuration**: `nginx/nginx.conf`

### Supervisor

Supervisor is used to manage multiple processes within the Docker container.

- **Directory**: `supervisor`
- **Configuration**: `supervisor/supervisord.conf`

## Docker

The application is containerized using Docker. The `Dockerfile` defines a multi-stage build to create the final image.

- **Build Command**: `docker build -t money-business .`
- **Run Command**: `docker run -p 80:80 money-business`

## Getting Started

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/money-business.git
    cd money-business
    ```

2. **Build and run the Docker container**:
    ```sh
    docker build -t money-business .
    docker run -p 80:80 money-business
    ```

3. **Access the application**:
    Open your browser and navigate to [http://localhost](http://_vscodecontentref_/13).

## License

This project is licensed under the MIT License.