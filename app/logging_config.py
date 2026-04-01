"""Logging configuration for the service."""

import logging
import sys
from app.config import settings


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    
    # Create logger
    logger = logging.getLogger("capability_service")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Console handler with structured format
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # JSON-like format for production
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()
