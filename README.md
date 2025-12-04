# Educational Support AI System

A FastAPI-based educational support chatbot system with session management, chat history, and Server-Sent Events (SSE) / WebSocket support.

## Features

- 🚀 FastAPI application with async support
- 🔐 API key-based authentication
- 💬 Chat endpoints with SSE and WebSocket support
- 📝 Session management
- 📊 Paginated chat history
- 🏥 Health check endpoints
- 🔄 CORS support

## Quick Start

### Local Development

```bash
# Install dependencies with uv
uv sync

# Run the application
uv run edu-support-ai-system

# With auto-reload for development
uv run edu-support-ai-system --reload
```

### Docker Setup

See [deployments/docker/DOCKER.md](deployments/docker/DOCKER.md) for comprehensive Docker and Docker Compose instructions.

Quick start with Docker:

```bash
# Navigate to the docker deployment directory
cd deployments/docker

# Build and run with Docker Compose
docker-compose up -d

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /init-session` - Initialize a chat session
- `POST /chat/sse` - Chat with Server-Sent Events
- `WS /chat/ws/{session_id}` - Chat with WebSocket
- `GET /history` - Get paginated chat history

## Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Docker Setup**: [deployments/docker/DOCKER.md](deployments/docker/DOCKER.md)

## Configuration

Environment variables can be configured in `.env` file:

- `API_HOST` - Server host (default: 0.0.0.0)
- `API_PORT` - Server port (default: 8000)
- `CORS_ORIGINS` - Allowed CORS origins (default: \*)
- `SESSION_EXPIRATION_SECONDS` - Session timeout (default: 3600)
- `DEFAULT_PAGE_SIZE` - Default pagination size (default: 20)
- `MAX_PAGE_SIZE` - Maximum pagination size (default: 100)
- `ALLOW_ALL_API_KEYS` - Allow any API key for development (default: true)

## License

Apache 2.0

## More Information

Visit: https://arunalla.help/
