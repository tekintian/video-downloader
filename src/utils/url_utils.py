"""URL utility functions."""

import re
from urllib.parse import urlparse, unquote
from typing import Optional, Dict, List
from ..core.exceptions import URLParseError
from ..core.logger import logger


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_video_id(url: str, platform: str = 'bilibili') -> Optional[str]:
    """Extract video ID from URL based on platform."""
    platform_patterns = {
        'bilibili': [
            r'bilibili\.com/video/([A-Za-z0-9]+)',
            r'b23\.tv/([A-Za-z0-9]+)',
            r'm\.bilibili\.com/video/([A-Za-z0-9]+)',
        ],
        'youtube': [
            r'youtube\.com/watch\?v=([A-Za-z0-9_-]+)',
            r'youtu\.be/([A-Za-z0-9_-]+)',
        ],
    }
    
    if platform not in platform_patterns:
        raise URLParseError(f"Unsupported platform: {platform}")
    
    for pattern in platform_patterns[platform]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def normalize_url(url: str) -> str:
    """Normalize URL by decoding and cleaning."""
    try:
        # Decode URL-encoded characters
        decoded_url = unquote(url)
        
        # Remove fragments
        parsed = urlparse(decoded_url)
        clean_url = parsed._replace(fragment="").geturl()
        
        return clean_url
        
    except Exception as e:
        logger.error(f"Failed to normalize URL: {e}")
        return url


def get_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def is_bilibili_url(url: str) -> bool:
    """Check if URL is from Bilibili."""
    domain = get_domain(url)
    return domain in ['www.bilibili.com', 'bilibili.com', 'b23.tv', 'm.bilibili.com']


def is_youtube_url(url: str) -> bool:
    """Check if URL is from YouTube."""
    domain = get_domain(url)
    return domain in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']


def extract_url_params(url: str) -> Dict[str, str]:
    """Extract query parameters from URL."""
    try:
        parsed = urlparse(url)
        params = {}
        
        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = unquote(value)
        
        return params
        
    except Exception as e:
        logger.error(f"Failed to extract URL params: {e}")
        return {}


def clean_url(url: str) -> str:
    """Clean URL by removing tracking parameters."""
    try:
        parsed = urlparse(url)
        params = extract_url_params(url)
        
        # Remove common tracking parameters
        tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'msclkid', '_ga', '_gid', 'from', 'seid', 'spm_id_from'
        ]
        
        cleaned_params = {
            k: v for k, v in params.items() 
            if k not in tracking_params
        }
        
        # Reconstruct URL
        if cleaned_params:
            query_string = '&'.join([f"{k}={v}" for k, v in cleaned_params.items()])
            cleaned_url = parsed._replace(query=query_string).geturl()
        else:
            cleaned_url = parsed._replace(query="").geturl()
        
        return cleaned_url
        
    except Exception as e:
        logger.error(f"Failed to clean URL: {e}")
        return url