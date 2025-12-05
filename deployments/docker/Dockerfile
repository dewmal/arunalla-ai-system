# Multi-stage Dockerfile for edu_support_ai_system

# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src ./src

# Install dependencies and the package using uv
RUN uv sync --frozen --no-dev && \
    uv pip install -e .

# Stage 2: Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files and dependencies from builder
COPY --from=builder /app/pyproject.toml /app/uv.lock ./
COPY --from=builder /app/src ./src
COPY --from=builder /app/.venv ./.venv

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application using the venv's uvicorn directly
CMD [".venv/bin/python", "-m", "uvicorn", "edu_support_ai_system.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
