"""Configuration management for video downloader."""

from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
import json


class DownloadConfig(BaseSettings):
    """Download configuration settings."""
    
    model_config = ConfigDict(
        env_prefix="VIDEO_DOWNLOADER_",
        env_file=".env"
    )
    
    # Download settings
    max_threads: int = Field(default=4, ge=1, le=16)
    chunk_size: int = Field(default=1024 * 1024, ge=1024)  # 1MB
    timeout: int = Field(default=30, ge=5)
    retry_times: int = Field(default=3, ge=0)
    
    # Path settings
    default_download_dir: str = Field(default="./downloads")
    temp_dir: str = Field(default="./temp")
    
    # Quality settings
    video_quality: str = Field(default="best")
    audio_only: bool = Field(default=False)
    subtitle: bool = Field(default=True)
    
    # User agent
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )


class ConfigManager:
    """Configuration file manager."""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path.home() / ".video_downloader" / "config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}
        else:
            self._config = self._get_default_config()
            self.save()
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self.save()
    
    def delete(self, key: str) -> None:
        """Delete configuration key."""
        if key in self._config:
            del self._config[key]
            self.save()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "download_dir": "./downloads",
            "max_threads": 4,
            "video_quality": "best",
            "subtitle": True,
            "theme": "dark"
        }


# Global configuration instances
download_config = DownloadConfig()
config_manager = ConfigManager()