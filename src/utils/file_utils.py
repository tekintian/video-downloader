"""File utility functions."""

import os
import re
from pathlib import Path
from typing import Optional
from pathvalidate import sanitize_filename, sanitize_filepath
from ..core.exceptions import FileOperationError
from ..core.logger import logger


def safe_filename(filename: str, replacement: str = "_") -> str:
    """Create safe filename by removing invalid characters."""
    try:
        # Remove or replace invalid characters using pathvalidate
        safe_name = sanitize_filename(filename)
        
        # Replace invalid characters with replacement
        invalid_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(invalid_chars, replacement, safe_name)
        
        # Remove multiple consecutive replacement characters
        safe_name = re.sub(f'{re.escape(replacement)}+', replacement, safe_name)
        
        # Remove leading/trailing replacement characters and dots
        safe_name = safe_name.strip(f'{replacement}.')
        
        # Ensure filename is not empty
        if not safe_name:
            safe_name = "untitled"
        
        return safe_name
        
    except Exception as e:
        logger.error(f"Failed to create safe filename: {e}")
        return "untitled"


def ensure_directory(path: Path) -> None:
    """Ensure directory exists."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise FileOperationError(f"Failed to create directory: {e}")


def get_unique_filename(path: Path) -> Path:
    """Get unique filename if file already exists."""
    if not path.exists():
        return path
    
    counter = 1
    while True:
        new_path = path.with_stem(f"{path.stem}_{counter}")
        if not new_path.exists():
            return new_path
        counter += 1


def format_filesize(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_video_extension(url: str, default_ext: str = "mp4") -> str:
    """Get video file extension from URL or format."""
    # Common video extensions
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    
    # Try to extract from URL
    parsed_url = Path(url)
    if parsed_url.suffix.lower() in video_extensions:
        return parsed_url.suffix.lower()
    
    # Return default
    return f".{default_ext.lstrip('.')}"


def clean_temp_files(directory: Path, pattern: str = "*.part*") -> None:
    """Clean up temporary files in directory."""
    try:
        for temp_file in directory.glob(pattern):
            temp_file.unlink()
            logger.debug(f"Removed temp file: {temp_file}")
    except Exception as e:
        logger.warning(f"Failed to clean temp files: {e}")


def validate_path(path: Path) -> bool:
    """Validate if path is safe to use."""
    try:
        # Convert to absolute path
        abs_path = path.resolve()
        
        # Check if path is within reasonable bounds
        # (Prevents path traversal attacks)
        if not str(abs_path).startswith(os.path.expanduser("~")) and not str(abs_path).startswith(os.getcwd()):
            logger.warning(f"Path outside user directory: {abs_path}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Invalid path {path}: {e}")
        return False