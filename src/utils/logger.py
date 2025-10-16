"""
Loguru logger configuration for the application.
"""

import sys
import os
from loguru import logger


def setup_logger(log_level: str = None):
    """
    Configure Loguru logger with appropriate format and level.
    Call this at application startup.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
                  Defaults to LOG_LEVEL env var or INFO
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Remove default handler
    logger.remove()
    
    # Add custom handler with format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Optionally add file handler (create logs directory if needed)
    try:
        os.makedirs("logs", exist_ok=True)
        logger.add(
            "logs/f1_service_{time}.log",
            rotation="10 MB",
            retention="7 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
    except Exception:
        pass  # File logging is optional
    
    logger.info(f"Logger initialized with level: {log_level}")
    
    return logger
