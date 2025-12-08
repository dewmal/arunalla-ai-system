# RAG Data Curator Tool

A desktop GUI application for preparing Sri Lankan A/L & O/L exam materials for a Retrieval-Augmented Generation (RAG) pipeline.

> **Website:** <https://arunalla.help/>

## Features

- 📁 **File Browser** - Browse and navigate PDF files in any folder
- 👁️ **PDF Preview** - View PDF pages with navigation controls
- 📥 **Google Drive Download** - Download files/folders directly from Google Drive URLs
- 📝 **Text Extraction** - Extract text from PDFs (quick 3-page or full extraction)
- 🔤 **Unicode Detection** - Detect Sinhala, Tamil, English text and legacy font encoding
- 🏷️ **Metadata Tagging** - Tag files with subject, year, exam level, paper type
- 💾 **Export** - Save metadata to JSON and export to CSV for Google Sheets

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/AdhiDevX369/arunalla-ai-system.git
   cd arunalla-ai-system
   ```

1. Create a virtual environment (recommended):

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Application

Run the main application:

```bash
python app.py
```

### CLI Tools

The data feeder module provides command-line tools:

```bash
# Extract text from a PDF
python -m tools.data_feeder.app extract <pdf_file>

# Download from Google Drive
python -m tools.data_feeder.app download <google_drive_url> [output_folder]

# Get PDF info
python -m tools.data_feeder.app info <pdf_file>
```

### Standalone Downloader

Run the interactive Google Drive downloader:

```bash
python tools/data_feeder/downloader.py
```

## Project Structure

```text
arunalla-ai-system/
├── app.py                      # Main GUI application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # License file
├── .gitignore                  # Git ignore rules
└── tools/
    └── data_feeder/
        ├── __init__.py         # Package exports
        ├── app.py              # CLI entry point
        ├── downloader.py       # Google Drive downloader
        └── pdf_extractor.py    # PDF text extraction
```

## Dependencies

| Package | Purpose |
|---------|---------|
| PyMuPDF | PDF rendering and quick text extraction |
| Pillow | Image processing for preview |
| pdfplumber | Full text extraction (better accuracy) |
| PyPDF2 | Fallback PDF text extraction |
| gdown | Google Drive downloads |
| requests | HTTP requests |
| beautifulsoup4 | HTML parsing |

## Supported Content

- **Exam Levels:** A/L (Advanced Level), O/L (Ordinary Level)
- **Languages:** Sinhala (Unicode), Tamil (Unicode), English
- **Paper Types:** Past Papers, Model Papers, Notes, Tutorials, Marking Schemes, Syllabi

## Unicode Detection

The tool detects:

- ✅ Valid Sinhala Unicode (U+0D80 to U+0DFF)
- ✅ Valid Tamil Unicode (U+0B80 to U+0BFF)
- ✅ English/Latin text
- ❌ Legacy Sinhala fonts (FM, DL, Kaputa) - These are NOT usable for RAG

## License

See [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
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

## Admin Panel

The admin panel allows you to configure AI agent system prompts and settings without code changes.

### Accessing the Admin Panel

1. **Set Admin API Key** in your `.env` file:

   ```bash
   # Generate a secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"

   # Add to .env
   ADMIN_API_KEY=your-generated-key-here
   ```

2. **Access the Panel**: Navigate to `http://localhost:8000/admin/ui`

3. **Login**: Enter your admin API key

### Features

- 🎨 **Modern UI** - Beautiful glassmorphism design with dark mode
- 🤖 **Agent Management** - Create, edit, and delete AI agents
- 📝 **System Prompts** - Configure agent behavior and personality
- ⚙️ **Model Settings** - Adjust temperature, max tokens, and model selection
- 📊 **Change History** - Track all prompt modifications
- 🔄 **Hot Reload** - Changes take effect without restart (when using database)

### Admin API Endpoints

- `GET /admin/agents` - List all agents
- `GET /admin/agents/{name}` - Get agent configuration
- `POST /admin/agents/{name}` - Create new agent
- `PUT /admin/agents/{name}` - Update agent configuration
- `DELETE /admin/agents/{name}` - Delete agent
- `GET /admin/agents/{name}/history` - Get prompt change history

## Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Docker Setup**: [deployments/docker/DOCKER.md](deployments/docker/DOCKER.md)

## Configuration

Environment variables can be configured in `.env` file (copy from `.env.example`):

### Server Configuration

- `API_HOST` - Server host (default: 0.0.0.0)
- `API_PORT` - Server port (default: 8000)
- `CORS_ORIGINS` - Allowed CORS origins (default: \*)
- `SESSION_EXPIRATION_SECONDS` - Session timeout (default: 3600)
- `DEFAULT_PAGE_SIZE` - Default pagination size (default: 20)
- `MAX_PAGE_SIZE` - Maximum pagination size (default: 100)

### API Key Configuration

- `ALLOW_ALL_API_KEYS` - Allow any API key for development (default: `true`)
  - Set to `false` in production to enforce API key validation
- `VALID_API_KEYS` - Comma-separated list of valid API keys (default: `demo-key-123,test-key-456,dev-key-789`)
  - Example: `VALID_API_KEYS=your-key-1,your-key-2,your-key-3`
  - Only used when `ALLOW_ALL_API_KEYS=false`
  - **⚠️ Important:** Use strong, unique keys in production!

**Creating API Keys:**

```bash
# Generate a secure random API key (Linux/Mac)
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env file
VALID_API_KEYS=key1,key2,key3
ALLOW_ALL_API_KEYS=false
```

### Google API Configuration

The application uses Google Gemini AI for the agent mesh. You **must** configure your Google API key:

- `GOOGLE_API_KEY` - Google API key for Gemini models (required)
  - Get your key from: https://makersuite.google.com/app/apikey
  - Example: `GOOGLE_API_KEY=AIzaSy...`
  - **⚠️ Required:** The application will not start without this key

**Setting up Google API Key:**

```bash
# 1. Get your API key from Google AI Studio
# Visit: https://makersuite.google.com/app/apikey

# 2. Add to .env file
echo "GOOGLE_API_KEY=your-api-key-here" >> .env

# 3. Restart the application
docker-compose restart api  # If using Docker
# OR
uv run edu-support-ai-system --reload  # If running locally
```

### Database Configuration

- `DATABASE_URL` - PostgreSQL connection string (optional, defaults to in-memory storage)
  - Format: `postgresql://username:password@host:port/database`
  - Example: `postgresql://eduai:changeme@localhost:5432/eduai_db`
- `DB_USER` - Database username (default: eduai)
- `DB_PASSWORD` - Database password (default: changeme) ⚠️ **Change in production!**
- `DB_NAME` - Database name (default: eduai_db)
- `DB_PORT` - Database port (default: 5432)

**Note:** If `DATABASE_URL` is not set, the application will use in-memory storage. Data will be lost when the application restarts.

## Database Setup

### With Docker Compose (Recommended)

PostgreSQL is automatically included in the Docker Compose setup:

```bash
# Start both API and PostgreSQL
cd deployments/docker
docker-compose up -d

# Verify PostgreSQL is running
docker-compose logs db

# Initialize database (tables are created automatically on first run)
# Or manually:
docker-compose exec api python -m edu_support_ai_system.init_db
```

### Local PostgreSQL

If running the API locally (not in Docker), you'll need a PostgreSQL instance:

```bash
# 1. Install and start PostgreSQL (or use Docker for just the database)
docker run -d \
  --name edu-support-db \
  -e POSTGRES_USER=eduai \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=eduai_db \
  -p 5432:5432 \
  postgres:15-alpine

# 2. Set DATABASE_URL in your environment
export DATABASE_URL="postgresql://eduai:changeme@localhost:5432/eduai_db"

# 3. Run the application
uv run edu-support-ai-system
```

### Troubleshooting Database Connection

If you encounter database connection issues:

1. **Check PostgreSQL is running:**

   ```bash
   docker-compose logs db
   ```

2. **Verify DATABASE_URL is set correctly:**

   ```bash
   docker-compose exec api env | grep DATABASE_URL
   ```

3. **Check application logs:**

   ```bash
   docker-compose logs api
   # Look for "✓ Using PostgreSQL database backend"
   ```

4. **Manually initialize database:**
   ```bash
   docker-compose exec api python -m edu_support_ai_system.init_db
   ```

## License

Apache 2.0

## More Information

Visit: https://arunalla.help/
