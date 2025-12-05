# Docker Deployment

This directory contains Docker and Docker Compose configuration for the Educational Support AI System.

## Quick Start

1. **Create environment file:**

   ```bash
   cp .env.example .env
   ```

2. **Customize your settings** (optional):
   Edit `.env` to customize API keys, database credentials, etc.

3. **Start services:**

   ```bash
   docker-compose up -d
   ```

4. **View logs:**

   ```bash
   docker-compose logs -f
   ```

5. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Environment Variables

All configuration is done via the `.env` file. See `.env.example` for available options:

### Google API Key (Required)

The application uses Google Gemini AI for the agent mesh. You **must** set your Google API key:

1. **Get your API key:**

   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key

2. **Set in `.env`:**
   ```bash
   GOOGLE_API_KEY=your-google-api-key-here
   ```

**⚠️ Without this key, the application will fail to start!**

### API Keys (Production)

To use API key validation in production:

1. Generate secure keys:

   ```bash
   # From the project root
   python generate_api_keys.py
   ```

2. Update `.env`:

   ```bash
   VALID_API_KEYS=your-generated-key-1,your-generated-key-2
   ALLOW_ALL_API_KEYS=false
   ```

3. Restart services:
   ```bash
   docker-compose restart api
   ```

### Database Configuration

PostgreSQL runs automatically with docker-compose. Data is persisted in the `postgres_data` volume.

**⚠️ Change default credentials in production:**

```bash
DB_USER=your_user
DB_PASSWORD=your_secure_password
DB_NAME=your_database
```

## Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# View logs
docker-compose logs -f api
docker-compose logs -f db

# Access PostgreSQL
docker-compose exec db psql -U eduai -d eduai_db

# Restart API only
docker-compose restart api

# Remove everything including volumes (⚠️ deletes data)
docker-compose down -v
```

## Troubleshooting

### API not connecting to database

1. Check database is healthy:

   ```bash
   docker-compose ps
   docker-compose logs db
   ```

2. Verify DATABASE_URL is set:

   ```bash
   docker-compose exec api env | grep DATABASE_URL
   ```

3. Check API logs:
   ```bash
   docker-compose logs api | grep -i "database\|postgresql"
   ```

### Port already in use

If port 8000 or 5432 is already in use, change in `.env`:

```bash
API_PORT=8001
DB_PORT=5433
```

Then update docker-compose port mapping to match.

## File Structure

```
deployments/docker/
├── .env.example          # Environment variables template
├── .env                  # Your local config (gitignored)
├── docker-compose.yml    # Service definitions
├── Dockerfile            # API container build
└── README.md            # This file
```
