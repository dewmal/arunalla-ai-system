"""Logging configuration for edu_support_ai_system"""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses environment variable LOG_LEVEL or defaults to INFO
    """
    import os

    # Get log level from parameter, environment, or default to INFO
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()

    # Convert string to logging level
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,  # Override any existing configuration
    )

    # Set specific loggers to appropriate levels
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Ensure our application loggers use the configured level
    logging.getLogger("edu_support_ai_system").setLevel(numeric_level)
    logging.getLogger("agent_mesh").setLevel(numeric_level)

    # Log that logging has been configured
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
