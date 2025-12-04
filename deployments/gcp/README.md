# Google Cloud Platform Deployment

This directory contains configuration files for deploying the Educational Support AI System to Google Cloud Platform.

## Files

- **cloudbuild.yaml**: Cloud Build configuration for CI/CD pipeline
- **app.yaml**: Cloud Run service configuration
- **.gcloudignore**: Files to exclude from GCP deployments
- **README.md**: This file

---

## Prerequisites

1. **Google Cloud Project**: Create a GCP project
2. **gcloud CLI**: Install and configure the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Enable APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```
4. **Authentication**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

---

## Deployment Options

### Option 1: Manual Cloud Build + Cloud Run

#### Step 1: Build and push the image

```bash
# From project root
gcloud builds submit \
  --config deployments/gcp/cloudbuild.yaml \
  --timeout=20m
```

This will:

- Build the Docker image using `deployments/docker/Dockerfile`
- Push to Google Container Registry as `gcr.io/YOUR_PROJECT_ID/edu-support-ai-system`

#### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy edu-support-ai-system \
  --image gcr.io/YOUR_PROJECT_ID/edu-support-ai-system:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "API_HOST=0.0.0.0,API_PORT=8000,CORS_ORIGINS=*,ALLOW_ALL_API_KEYS=false"
```

#### Step 3: Get the service URL

```bash
gcloud run services describe edu-support-ai-system \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

---

### Option 2: Automated Cloud Build with Cloud Run Deployment

Uncomment the Cloud Run deployment step in `cloudbuild.yaml`:

```yaml
# Step 4: Deploy to Cloud Run (optional - uncomment to enable)
- name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
  entrypoint: gcloud
  args:
    - "run"
    - "deploy"
    # ... rest of the configuration
```

Then submit the build:

```bash
gcloud builds submit --config deployments/gcp/cloudbuild.yaml
```

This will automatically build, push, and deploy in one step.

---

### Option 3: Continuous Deployment from GitHub

Set up a Cloud Build trigger connected to your GitHub repository:

1. **Connect Repository**:

   ```bash
   # Via Console: Cloud Build > Triggers > Connect Repository
   # Or use gcloud:
   gcloud beta builds triggers create github \
     --repo-name=edu_rag_app \
     --repo-owner=YOUR_GITHUB_USERNAME \
     --branch-pattern="^main$" \
     --build-config=deployments/gcp/cloudbuild.yaml
   ```

2. **Configure Trigger**: Set the trigger to run on push to `main` branch

3. **Auto-deploy**: Every push to main will automatically build and deploy

---

## Environment Variables

Update environment variables in Cloud Run:

```bash
gcloud run services update edu-support-ai-system \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=https://yourdomain.com,ALLOW_ALL_API_KEYS=false"
```

Or use Secret Manager for sensitive values:

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create API_KEY --data-file=-

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding API_KEY \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update service to use secret
gcloud run services update edu-support-ai-system \
  --region us-central1 \
  --update-secrets=API_KEY=API_KEY:latest
```

---

## Monitoring & Logs

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read edu-support-ai-system \
  --region us-central1 \
  --limit 50

# Cloud Build logs
gcloud builds list --limit 10
gcloud builds log BUILD_ID
```

### Metrics

Access metrics in Cloud Console:

- Cloud Run: [Console → Cloud Run → Your Service → Metrics](https://console.cloud.google.com/run)
- Cloud Build: [Console → Cloud Build → History](https://console.cloud.google.com/cloud-build)

---

## Scaling Configuration

Cloud Run automatically scales based on traffic. Adjust settings:

```bash
gcloud run services update edu-support-ai-system \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10 \
  --cpu 1 \
  --memory 512Mi \
  --concurrency 80
```

---

## Cost Optimization

1. **Set minimum instances to 0** (default) - no cost when idle
2. **Use appropriate CPU/memory** - start with 1 CPU, 512Mi RAM
3. **Enable request timeout** to prevent long-running requests
4. **Use Cloud Scheduler** for health checks if needed

---

## Custom Domain

Map a custom domain to your Cloud Run service:

```bash
gcloud run domain-mappings create \
  --service edu-support-ai-system \
  --domain api.yourdomain.com \
  --region us-central1
```

---

## Troubleshooting

### Build Fails

```bash
# Check build logs
gcloud builds list --limit 5
gcloud builds log BUILD_ID

# Test build locally with Cloud Build Local
cloud-build-local --dryrun=false --config=deployments/gcp/cloudbuild.yaml .
```

### Deployment Issues

```bash
# Check service status
gcloud run services describe edu-support-ai-system --region us-central1

# View recent revisions
gcloud run revisions list --service edu-support-ai-system --region us-central1

# Rollback to previous revision
gcloud run services update-traffic edu-support-ai-system \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

### Health Check Failures

Ensure `/health` endpoint is accessible and returns 200 OK.

---

## Cleanup

Remove all deployed resources:

```bash
# Delete Cloud Run service
gcloud run services delete edu-support-ai-system --region us-central1

# Delete Container Registry images
gcloud container images delete gcr.io/YOUR_PROJECT_ID/edu-support-ai-system:latest
```

---

## Additional Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Container Registry Documentation](https://cloud.google.com/container-registry/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
