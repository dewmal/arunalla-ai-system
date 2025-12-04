# Educational Support AI System - Docker Setup

This guide provides instructions for running the edu_support_ai_system using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### 1. Navigate to the Docker deployment directory

```bash
cd deployments/docker
```

### 2. Create environment file (optional)

```bash
cp .env.example .env
```

Edit `.env` to customize your configuration if needed.

### 3. Build and run with Docker Compose

```bash
docker-compose up -d
```

This will:

- Build the Docker image
- Start the FastAPI application on port 8000
- Set up networking and health checks

### 4. Verify the application is running

```bash
docker-compose ps
```

Access the application:

- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Commands

### Build the image

```bash
docker-compose build
```

### Start the services

```bash
docker-compose up -d
```

### Stop the services

```bash
docker-compose down
```

### View logs

```bash
docker-compose logs -f api
```

### Restart the application

```bash
docker-compose restart api
```

### Check health status

```bash
docker-compose exec api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

## Development Mode

For development with hot reload, you can modify the `docker-compose.yml` to add the `--reload` flag:

```yaml
command:
  [
    "uv",
    "run",
    "edu-support-ai-system",
    "--host",
    "0.0.0.0",
    "--port",
    "8000",
    "--reload",
  ]
```

The source code is already mounted as a read-only volume, so changes to your code will trigger a reload.

## Environment Variables

All environment variables can be configured in the `.env` file:

| Variable                     | Default | Description                                  |
| ---------------------------- | ------- | -------------------------------------------- |
| `API_PORT`                   | `8000`  | External port to expose the API              |
| `CORS_ORIGINS`               | `*`     | Comma-separated list of allowed CORS origins |
| `SESSION_EXPIRATION_SECONDS` | `3600`  | Session expiration time in seconds           |
| `DEFAULT_PAGE_SIZE`          | `20`    | Default pagination page size                 |
| `MAX_PAGE_SIZE`              | `100`   | Maximum pagination page size                 |
| `ALLOW_ALL_API_KEYS`         | `true`  | Allow any API key (development only)         |

## Building for Production

For production deployment, consider:

1. **Set `ALLOW_ALL_API_KEYS=false`** in your `.env` file
2. **Configure specific CORS origins** instead of using `*`
3. **Remove the volume mount** in `docker-compose.yml` for the source code
4. **Use proper API key management** (database or secrets manager)
5. **Set up HTTPS** with a reverse proxy like Nginx or Traefik

## Adding a Database

The `docker-compose.yml` includes a commented-out PostgreSQL service. To enable it:

1. Uncomment the `db` service and `volumes` section
2. Update your application code to connect to the database
3. Add database connection environment variables:
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `DB_HOST=db`
   - `DB_PORT=5432`

## Troubleshooting

### Container won't start

Check logs:

```bash
docker-compose logs api
```

### Port already in use

Change the `API_PORT` in `.env` file:

```
API_PORT=8001
```

### Permission issues

Ensure the application user has proper permissions:

```bash
docker-compose exec api ls -la /app
```

## Cleaning Up

Remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

Remove the built image:

```bash
docker rmi edu_rag_app-api
```

## Support

For issues and questions, please refer to the main README.md or create an issue in the repository.
