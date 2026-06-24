"""Logging configuration and utilities"""
import logging
import sys
from app.config import get_settings


def setup_logging():
    """Configure logging for the application"""
    settings = get_settings()

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(console_handler)

    return logger


# Create logger instance
logger = setup_logging()
