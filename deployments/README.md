# Deployments

This directory contains deployment configurations for the Educational Support AI System.

## Available Deployment Methods

### Docker (Local/Cloud)

The `docker` directory contains:

- **Dockerfile**: Multi-stage Docker build configuration
- **docker-compose.yml**: Docker Compose setup for local development and deployment
- **.dockerignore**: Files to exclude from Docker build context
- **.env.example**: Environment variable template
- **DOCKER.md**: Comprehensive Docker deployment documentation

**Quick Start**:

```bash
cd docker
docker-compose up -d
```

See [docker/DOCKER.md](docker/DOCKER.md) for detailed instructions.

---

## Deployment Recommendations

### Development

- Use Docker Compose for consistent local development environment
- Mount source volumes for hot reloading (already configured)

### Production

- Use Docker with proper environment variables
- Deploy to container platforms (AWS ECS, Google Cloud Run, Azure Container Instances)
- Set up reverse proxy (Nginx, Traefik) for HTTPS
- Use managed databases instead of containerized ones
- Implement proper secrets management

---

## Adding New Deployment Methods

To add new deployment configurations (e.g., Kubernetes, AWS Lambda):

1. Create a new directory: `deployments/<deployment-type>/`
2. Add necessary configuration files
3. Include a README with setup instructions
4. Update this main deployments README

---

## Current Structure

```
deployments/
├── README.md          # This file
└── docker/            # Docker deployment
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .dockerignore
    ├── .env.example
    └── DOCKER.md
```
