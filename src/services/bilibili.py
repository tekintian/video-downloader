"""Bilibili video service."""

import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import yt_dlp
from ..core.exceptions import URLParseError, NetworkError, DownloadError
from ..core.logger import logger


class BilibiliService:
    """Bilibili video service."""
    
    def __init__(self):
        self.session_options = {
            'quiet': True,
            'no_warnings': False,
            'extract_flat': False,
        }
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is a valid Bilibili URL."""
        patterns = [
            r'https?://www\.bilibili\.com/video/[A-Za-z0-9]+',
            r'https?://b23\.tv/[A-Za-z0-9]+',
            r'https?://m\.bilibili\.com/video/[A-Za-z0-9]+',
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information from Bilibili URL."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        try:
            with yt_dlp.YoutubeDL(self.session_options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'id': info.get('id', ''),
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'subtitles': info.get('subtitles', {}),
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise NetworkError(f"Failed to retrieve video information: {e}")
    
    def get_download_url(self, url: str, quality: str = 'best') -> str:
        """Get direct download URL for video."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        try:
            ydl_opts = {
                'quiet': True,
                'format': quality,
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Handle different response formats
                if 'url' in info and info['url']:
                    return info['url']
                elif 'formats' in info:
                    # Try to get the first format with URL
                    for fmt in info['formats']:
                        if 'url' in fmt and fmt['url']:
                            return fmt['url']
                    raise DownloadError("No valid format URL found")
                elif 'entries' in info:
                    # For playlists, return first entry
                    if info['entries'] and info['entries'][0]:
                        entry = info['entries'][0]
                        if 'url' in entry:
                            return entry['url']
                    raise DownloadError("No valid entry in playlist")
                else:
                    raise DownloadError("No download URL found")
                    
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            raise DownloadError(f"Failed to get download URL: {e}")
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """Get available video formats."""
        try:
            with yt_dlp.YoutubeDL(self.session_options) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # Filter and sort formats
                available_formats = []
                for fmt in formats:
                    if fmt.get('vcodec') != 'none':  # Video formats only
                        available_formats.append({
                            'format_id': fmt.get('format_id', ''),
                            'ext': fmt.get('ext', ''),
                            'resolution': fmt.get('format_note', ''),
                            'fps': fmt.get('fps', 0),
                            'filesize': fmt.get('filesize', 0),
                            'vcodec': fmt.get('vcodec', ''),
                            'acodec': fmt.get('acodec', ''),
                        })
                
                return available_formats
        except Exception as e:
            logger.error(f"Failed to get formats: {e}")
            raise NetworkError(f"Failed to get available formats: {e}")
    
    def get_video_id(self, url: str) -> str:
        """Extract video ID from URL."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        # Handle different URL formats
        if 'b23.tv' in url:
            # Short URL
            return url.split('/')[-1]
        elif 'bilibili.com/video' in url:
            # Full URL
            match = re.search(r'/video/([A-Za-z0-9]+)', url)
            if match:
                return match.group(1)
        
        raise URLParseError(f"Cannot extract video ID from URL: {url}")


# Create global instance
bilibili_service = BilibiliService()