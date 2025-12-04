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

### Google Cloud Platform (GCP)

The `gcp` directory contains:

- **cloudbuild.yaml**: Cloud Build CI/CD pipeline configuration
- **app.yaml**: Cloud Run service configuration
- **.gcloudignore**: Files to exclude from GCP deployments
- **README.md**: Comprehensive GCP deployment documentation

**Quick Start**:

```bash
# Build and push to GCR
gcloud builds submit --config deployments/gcp/cloudbuild.yaml

# Deploy to Cloud Run
gcloud run deploy edu-support-ai-system \
  --image gcr.io/YOUR_PROJECT_ID/edu-support-ai-system:latest \
  --platform managed \
  --region us-central1
```

See [gcp/README.md](gcp/README.md) for detailed instructions.

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
├── docker/            # Docker deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   ├── .env.example
│   └── DOCKER.md
└── gcp/               # Google Cloud Platform deployment
    ├── cloudbuild.yaml
    ├── app.yaml
    ├── .gcloudignore
    └── README.md
```
