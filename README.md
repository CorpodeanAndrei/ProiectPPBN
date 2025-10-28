# Chat Application - Java EE Server + Python Client

A real-time chat application demonstrating client-server architecture with Java EE backend and Python GUI client.

## 🏗️ Architecture
- **Backend**: Java EE 8 + JAX-RS + Tomcat
- **Frontend**: Python + Tkinter
- **Containerization**: Docker
- **Deployment**: Play with Docker

## 🚀 Quick Start

### Server
```bash
cd server
docker build -t chat-server .
docker run -p 8080:8080 chat-server