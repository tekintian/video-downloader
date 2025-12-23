"""Tests for configuration management."""

import pytest
import tempfile
import json
from pathlib import Path
from src.core.config import ConfigManager, DownloadConfig


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"
        self.config_manager = ConfigManager(self.config_file)
    
    def test_default_config_creation(self):
        """Test default configuration creation."""
        assert self.config_file.exists()
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        assert "download_dir" in config
        assert "max_threads" in config
    
    def test_get_default_value(self):
        """Test getting default configuration value."""
        value = self.config_manager.get("non_existent_key", "default_value")
        assert value == "default_value"
    
    def test_set_and_get_value(self):
        """Test setting and getting configuration value."""
        self.config_manager.set("test_key", "test_value")
        
        value = self.config_manager.get("test_key")
        assert value == "test_value"
    
    def test_persistence(self):
        """Test configuration persistence."""
        self.config_manager.set("persistent_key", "persistent_value")
        
        # Create new instance
        new_manager = ConfigManager(self.config_file)
        value = new_manager.get("persistent_key")
        assert value == "persistent_value"


class TestDownloadConfig:
    """Test cases for DownloadConfig."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = DownloadConfig()
        
        assert config.max_threads == 4
        assert config.chunk_size == 1024 * 1024
        assert config.timeout == 30
        assert config.retry_times == 3
        assert config.default_download_dir == "./downloads"
        assert config.video_quality == "best"
        assert not config.audio_only
        assert config.subtitle
    
    def test_validation(self):
        """Test configuration validation."""
        # Valid values should work
        config = DownloadConfig(max_threads=8)
        assert config.max_threads == 8
        
        # Invalid values should raise validation error
        with pytest.raises(ValueError):
            DownloadConfig(max_threads=0)  # Should be >= 1
        
        with pytest.raises(ValueError):
            DownloadConfig(max_threads=20)  # Should be <= 16