"""
logging_config.py

Central logging configuration for Discord Monitor Bot.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging():
    """Configure global logging."""
    logger = logging.getLogger("discord_monitor")
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Rotating file handler (10MB x 5 backups)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
