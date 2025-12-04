"""Configuration management for edu_support_ai_system"""
import os
from typing import Set

# Server Configuration
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8000"))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Session Configuration
SESSION_EXPIRATION_SECONDS = int(os.getenv("SESSION_EXPIRATION_SECONDS", "3600"))

# Pagination Defaults
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

# Demo API Keys (In production, use a database or secrets manager)
VALID_API_KEYS: Set[str] = {
    "demo-key-123",
    "test-key-456",
    "dev-key-789",
}

# Allow all keys in development
ALLOW_ALL_API_KEYS = os.getenv("ALLOW_ALL_API_KEYS", "true").lower() == "true"
