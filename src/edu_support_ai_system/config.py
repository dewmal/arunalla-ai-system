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

# API Keys Configuration
# Load API keys from environment variable (comma-separated)
# Example: VALID_API_KEYS=key1,key2,key3
_api_keys_env = os.getenv("VALID_API_KEYS", "demo-key-123,test-key-456,dev-key-789")
VALID_API_KEYS: Set[str] = set(key.strip() for key in _api_keys_env.split(",") if key.strip())

# Allow all keys in development
ALLOW_ALL_API_KEYS = os.getenv("ALLOW_ALL_API_KEYS", "true").lower() == "true"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", None)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))


# Settings object for easier access
class Settings:
    """Settings object for configuration"""
    HOST = HOST
    PORT = PORT
    CORS_ORIGINS = CORS_ORIGINS
    SESSION_EXPIRATION_SECONDS = SESSION_EXPIRATION_SECONDS
    DEFAULT_PAGE_SIZE = DEFAULT_PAGE_SIZE
    MAX_PAGE_SIZE = MAX_PAGE_SIZE
    VALID_API_KEYS = VALID_API_KEYS
    ALLOW_ALL_API_KEYS = ALLOW_ALL_API_KEYS
    DATABASE_URL = DATABASE_URL
    DB_POOL_SIZE = DB_POOL_SIZE
    DB_MAX_OVERFLOW = DB_MAX_OVERFLOW
    DB_POOL_TIMEOUT = DB_POOL_TIMEOUT
    DB_POOL_RECYCLE = DB_POOL_RECYCLE


settings = Settings()

