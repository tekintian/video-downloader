"""Tests for Bilibili service."""

import pytest
from unittest.mock import Mock, patch
from src.services.bilibili import BilibiliService
from src.core.exceptions import URLParseError, NetworkError


class TestBilibiliService:
    """Test cases for BilibiliService."""
    
    def setup_method(self):
        """Setup test environment."""
        self.service = BilibiliService()
    
    def test_is_valid_url_valid_urls(self):
        """Test valid Bilibili URLs."""
        valid_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "https://b23.tv/abc123",
            "https://m.bilibili.com/video/BV1yy411c7mD",
        ]
        
        for url in valid_urls:
            assert self.service.is_valid_url(url), f"URL should be valid: {url}"
    
    def test_is_valid_url_invalid_urls(self):
        """Test invalid Bilibili URLs."""
        invalid_urls = [
            "https://www.youtube.com/watch?v=abc123",
            "https://github.com/user/repo",
            "not-a-url",
            "",
            "ftp://example.com/file.mp4",
        ]
        
        for url in invalid_urls:
            assert not self.service.is_valid_url(url), f"URL should be invalid: {url}"
    
    def test_get_video_id(self):
        """Test video ID extraction."""
        test_cases = [
            ("https://www.bilibili.com/video/BV1xx411c7mD", "BV1xx411c7mD"),
            ("https://b23.tv/abc123", "abc123"),
            ("https://m.bilibili.com/video/BV1yy411c7mD", "BV1yy411c7mD"),
        ]
        
        for url, expected_id in test_cases:
            assert self.service.get_video_id(url) == expected_id
    
    def test_get_video_id_invalid_url(self):
        """Test video ID extraction with invalid URL."""
        with pytest.raises(URLParseError):
            self.service.get_video_id("https://www.youtube.com/watch?v=abc123")
    
    @patch('src.services.bilibili.yt_dlp.YoutubeDL')
    def test_get_video_info_success(self, mock_ydl_class):
        """Test successful video info retrieval."""
        # Mock response
        mock_info = {
            'id': 'BV1xx411c7mD',
            'title': 'Test Video',
            'description': 'Test Description',
            'duration': 300,
            'uploader': 'Test Uploader',
            'upload_date': '20231201',
            'view_count': 1000000,
            'thumbnail': 'https://example.com/thumb.jpg',
            'formats': [],
            'subtitles': {},
        }
        
        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        # Test
        result = self.service.get_video_info("https://www.bilibili.com/video/BV1xx411c7mD")
        
        assert result['id'] == 'BV1xx411c7mD'
        assert result['title'] == 'Test Video'
        assert result['duration'] == 300
    
    @patch('src.services.bilibili.yt_dlp.YoutubeDL')
    def test_get_video_info_failure(self, mock_ydl_class):
        """Test video info retrieval failure."""
        mock_ydl = Mock()
        mock_ydl.extract_info.side_effect = Exception("Network error")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        with pytest.raises(NetworkError):
            self.service.get_video_info("https://www.bilibili.com/video/BV1xx411c7mD")
    
    def test_get_video_info_invalid_url(self):
        """Test video info with invalid URL."""
        with pytest.raises(URLParseError):
            self.service.get_video_info("invalid-url")
    
    @patch('src.services.bilibili.yt_dlp.YoutubeDL')
    def test_get_download_url_success(self, mock_ydl_class):
        """Test successful download URL retrieval."""
        mock_info = {'url': 'https://example.com/video.mp4'}
        mock_ydl = Mock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        result = self.service.get_download_url("https://www.bilibili.com/video/BV1xx411c7mD")
        
        assert result == 'https://example.com/video.mp4'
    
    def test_get_download_url_invalid_url(self):
        """Test download URL with invalid URL."""
        with pytest.raises(URLParseError):
            self.service.get_download_url("invalid-url")