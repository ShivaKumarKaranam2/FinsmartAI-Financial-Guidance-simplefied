"""
Centralized logging configuration for FinSmart AI Backend.
Provides structured, colored console logging and file logging.
"""

import logging
import os
import sys
from typing import Optional

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure root logger once
_configured = False


def setup_logger(name: str = "finsmart", level: Optional[int] = None) -> logging.Logger:
    """
    Configures and returns a structured logger with both console and file handlers.
    """
    global _configured

    if level is None:
        log_level_env = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, log_level_env, logging.INFO)

    if not _configured:
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Clear any existing root handlers to prevent duplicate lines
        if not root_logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

            # File handler (writes to finsmart.log)
            try:
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                log_file = os.path.join(backend_dir, "finsmart.log")
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setLevel(level)
                file_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
            except Exception:
                pass

        _configured = True

    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

