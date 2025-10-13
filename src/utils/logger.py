"""
Loguru logger configuration for the application.
"""

import sys
from loguru import logger
from src.config.settings import settings


def setup_logger():
    """
    Configure Loguru logger with appropriate format and level.
    Call this at application startup.
    """
    # Remove default handler
    logger.remove()
    
    # Add custom handler with format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Optionally add file handler
    logger.add(
        "logs/f1_service_{time}.log",
        rotation="10 MB",
        retention="7 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info("Logger initialized with level: {}", settings.LOG_LEVEL)


# Initialize logger when module is imported
setup_logger()
