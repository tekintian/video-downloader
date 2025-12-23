"""Logging configuration for video downloader."""

import sys
from pathlib import Path
from loguru import logger
from .config import config_manager


def setup_logger(log_level: str = "INFO", log_file: Path = None) -> None:
    """Setup logger configuration."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | "
                   "{level: <8} | "
                   "{name}:{function}:{line} - "
                   "{message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )


# Initialize logger with default settings
log_dir = Path.home() / ".video_downloader" / "logs"
setup_logger(log_level="INFO", log_file=log_dir / "video_downloader.log")

# Export logger instance
__all__ = ["logger"]