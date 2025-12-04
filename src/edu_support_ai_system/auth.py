"""Authentication utilities for API key validation"""
from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

from . import config

# API Key header scheme (optional, for header-based auth)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key
    
    Args:
        api_key: The API key to validate
    
    Returns:
        True if valid, False otherwise
    """
    if config.ALLOW_ALL_API_KEYS:
        return True
    
    return api_key in config.VALID_API_KEYS


def require_valid_api_key(api_key: str) -> str:
    """
    Validate API key and raise exception if invalid
    
    Args:
        api_key: The API key to validate
    
    Returns:
        The validated API key
    
    Raises:
        HTTPException: If API key is invalid
    """
    if not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key


def get_api_key_from_header(api_key: Optional[str] = None) -> str:
    """
    Dependency to get and validate API key from header
    
    Args:
        api_key: API key from header
    
    Returns:
        Validated API key
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    return require_valid_api_key(api_key)
