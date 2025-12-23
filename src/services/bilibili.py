"""Bilibili video service."""

import re
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, quote
import requests
import yt_dlp
from ..core.exceptions import URLParseError, NetworkError, DownloadError
from ..core.logger import logger


class BilibiliService:
    """Bilibili video service with official API and yt-dlp fallback."""
    
    def __init__(self):
        self.session_options = {
            'quiet': True,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        # Official API settings
        self.api_base = "https://api.bilibili.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # Request session for API calls
        self.api_session = requests.Session()
        self.api_session.headers.update(self.headers)
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is a valid Bilibili URL."""
        patterns = [
            r'https?://www\.bilibili\.com/video/[A-Za-z0-9]+',
            r'https?://b23\.tv/[A-Za-z0-9]+',
            r'https?://m\.bilibili\.com/video/[A-Za-z0-9]+',
            r'https?://www\.bilibili\.com/bangumi/play/[a-zA-Z]+[0-9]+',
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    def _get_bvid_from_url(self, url: str) -> Optional[str]:
        """Extract BV ID from Bilibili URL."""
        patterns = [
            r'/video/([A-Za-z0-9]+)',
            r'BV([A-Za-z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                bvid = match.group(1) if match.group(1).startswith('BV') else f"BV{match.group(1)}"
                return bvid
        
        # Handle short URL b23.tv
        if 'b23.tv' in url:
            # Need to resolve short URL first
            try:
                response = self.api_session.get(url, allow_redirects=True, timeout=10)
                return self._get_bvid_from_url(response.url)
            except Exception as e:
                logger.warning(f"Failed to resolve short URL {url}: {e}")
                return None
        
        return None
    
    def _call_bilibili_api(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API call to Bilibili."""
        try:
            url = f"{self.api_base}{endpoint}"
            response = self.api_session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                return data.get('data')
            else:
                logger.warning(f"API returned error: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None
    
    def _get_video_info_via_api(self, bvid: str) -> Optional[Dict[str, Any]]:
        """Get video info using Bilibili official API."""
        # Get basic video information
        video_info = self._call_bilibili_api('/x/web-interface/view', {'bvid': bvid})
        if not video_info:
            return None
        
        # Get play URL for each part
        cid = video_info.get('cid')
        if not cid:
            logger.error(f"No CID found for video {bvid}")
            return None
        
        play_info = self._call_bilibili_api('/x/player/playurl', {
            'bvid': bvid,
            'cid': cid,
            'fourk': 1,
            'otype': 'json',
            'fnver': 0,
            'fnval': 976  # Support DASH format
        })
        
        if not play_info:
            return None
        
        # Transform API response to yt-dlp format for compatibility
        return {
            'id': bvid,
            'title': video_info.get('title', ''),
            'description': video_info.get('desc', ''),
            'duration': video_info.get('duration', 0),
            'uploader': video_info.get('owner', {}).get('name', ''),
            'upload_date': str(video_info.get('pubdate', '')),
            'view_count': video_info.get('stat', {}).get('view', 0),
            'like_count': video_info.get('stat', {}).get('like', 0),
            'thumbnail': video_info.get('pic', ''),
            'formats': self._extract_formats_from_api(play_info),
            'subtitles': {},
            'api_source': 'official',  # Mark as API source
            'cid': cid,
            'bvid': bvid,
        }
    
    def _extract_formats_from_api(self, play_info: Dict) -> List[Dict]:
        """Extract video formats from Bilibili API response."""
        formats = []
        
        # Handle DASH format (preferred)
        if 'dash' in play_info:
            dash_data = play_info['dash']
            
            # Video streams
            for video in dash_data.get('video', []):
                formats.append({
                    'format_id': f"dash-{video['id']}",
                    'ext': 'mp4',
                    'format_note': f"{video['width']}x{video['height']} {video.get('id', '')}",
                    'width': video.get('width', 0),
                    'height': video.get('height', 0),
                    'fps': video.get('frame_rate', 0),
                    'filesize': video.get('size', 0),
                    'vcodec': video.get('codecid', ''),
                    'acodec': 'none',  # Video only stream
                    'url': video.get('baseUrl', ''),
                    'protocol': 'https_dash',
                })
            
            # Audio streams
            for audio in dash_data.get('audio', []):
                formats.append({
                    'format_id': f"dash-audio-{audio['id']}",
                    'ext': 'm4a',
                    'format_note': f"Audio {audio.get('id', '')}",
                    'filesize': audio.get('size', 0),
                    'vcodec': 'none',
                    'acodec': audio.get('codecid', ''),
                    'url': audio.get('baseUrl', ''),
                    'protocol': 'https_dash',
                })
        
        # Handle legacy format (fallback)
        elif 'durl' in play_info:
            for i, durl in enumerate(play_info['durl']):
                formats.append({
                    'format_id': f"durl-{i}",
                    'ext': 'flv',
                    'format_note': f"Part {i+1}",
                    'filesize': durl.get('size', 0),
                    'url': durl.get('url', ''),
                    'protocol': 'http',
                })
        
        return formats
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information from Bilibili URL with API priority."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        bvid = self._get_bvid_from_url(url)
        
        # First try official API
        if bvid:
            logger.info(f"Trying official Bilibili API for {bvid}")
            try:
                api_info = self._get_video_info_via_api(bvid)
                if api_info:
                    logger.info("Successfully retrieved video info via official API")
                    return api_info
                else:
                    logger.warning("Official API failed, falling back to yt-dlp")
            except Exception as e:
                logger.warning(f"Official API error: {e}, falling back to yt-dlp")
        
        # Fallback to yt-dlp
        logger.info("Using yt-dlp as fallback")
        try:
            with yt_dlp.YoutubeDL(self.session_options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                result = {
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
                    'api_source': 'ytdlp',  # Mark as yt-dlp source
                }
                
                logger.info("Successfully retrieved video info via yt-dlp")
                return result
                
        except Exception as e:
            logger.error(f"Both API and yt-dlp failed: {e}")
            raise NetworkError(f"Failed to retrieve video information: {e}")
    
    def get_download_url(self, url: str, quality: str = 'best') -> str:
        """Get direct download URL for video with API priority."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        # First try with video info that includes API source info
        try:
            video_info = self.get_video_info(url)
            formats = video_info.get('formats', [])
            
            if not formats:
                raise DownloadError("No formats available")
            
            # Format selection logic
            selected_format = self._select_format(formats, quality)
            if selected_format and 'url' in selected_format:
                logger.info(f"Selected format: {selected_format.get('format_id', 'unknown')}")
                return selected_format['url']
            else:
                raise DownloadError("No valid format URL found")
                
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            raise DownloadError(f"Failed to get download URL: {e}")
    
    def _select_format(self, formats: List[Dict], quality: str = 'best') -> Optional[Dict]:
        """Select the best format based on quality preference."""
        if not formats:
            return None
        
        # Filter out formats without URLs
        valid_formats = [f for f in formats if 'url' in f and f['url']]
        if not valid_formats:
            return None
        
        # Preference: DASH video > legacy formats > audio only
        video_formats = [f for f in valid_formats if f.get('vcodec') != 'none']
        audio_formats = [f for f in valid_formats if f.get('acodec') != 'none']
        
        if quality == 'best':
            # Select highest quality video format
            if video_formats:
                # Sort by resolution (height) then by file size
                video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)
                return video_formats[0]
            elif valid_formats:
                return valid_formats[0]
        elif quality == 'worst':
            # Select lowest quality
            if video_formats:
                video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)))
                return video_formats[0]
            elif valid_formats:
                return valid_formats[0]
        elif quality.startswith('dash'):
            # Handle specific DASH quality requests
            # quality format: "dash-120", "dash-116", etc.
            for fmt in valid_formats:
                if fmt.get('format_id') == quality:
                    return fmt
            # Fallback to best video
            if video_formats:
                video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
                return video_formats[0]
        
        # Default: return first valid format
        return valid_formats[0]
    
    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """Get available video formats with API priority."""
        try:
            video_info = self.get_video_info(url)
            formats = video_info.get('formats', [])
            
            # Enhanced format information
            available_formats = []
            api_source = video_info.get('api_source', 'unknown')
            
            for fmt in formats:
                format_info = {
                    'format_id': fmt.get('format_id', ''),
                    'ext': fmt.get('ext', ''),
                    'resolution': fmt.get('format_note', ''),
                    'fps': fmt.get('fps', 0),
                    'filesize': fmt.get('filesize', 0),
                    'vcodec': fmt.get('vcodec', ''),
                    'acodec': fmt.get('acodec', ''),
                    'width': fmt.get('width', 0),
                    'height': fmt.get('height', 0),
                    'protocol': fmt.get('protocol', ''),
                    'source': api_source,  # Add source info
                }
                
                # Add quality description for DASH formats
                if fmt.get('format_id', '').startswith('dash-'):
                    if fmt.get('vcodec') != 'none':
                        format_info['type'] = 'video'
                        format_info['quality_desc'] = f"{fmt.get('height', 0)}p {fmt.get('fps', 0)}fps"
                    elif fmt.get('acodec') != 'none':
                        format_info['type'] = 'audio'
                        format_info['quality_desc'] = f"Audio {fmt.get('format_id', '')}"
                else:
                    format_info['type'] = 'legacy'
                    format_info['quality_desc'] = fmt.get('format_note', '')
                
                available_formats.append(format_info)
            
            # Sort by quality (video first, then audio, then legacy)
            available_formats.sort(key=lambda x: (
                0 if x['type'] == 'video' else 1 if x['type'] == 'audio' else 2,
                -x['height'] if x['type'] == 'video' else 0,
                -x['filesize'] if x['filesize'] else 0
            ))
            
            return available_formats
            
        except Exception as e:
            logger.error(f"Failed to get formats: {e}")
            raise NetworkError(f"Failed to get available formats: {e}")
    
    def get_api_source_info(self, url: str) -> Dict[str, Any]:
        """Get information about which API source is being used."""
        try:
            video_info = self.get_video_info(url)
            api_source = video_info.get('api_source', 'unknown')
            
            return {
                'url': url,
                'api_source': api_source,
                'bvid': video_info.get('bvid', ''),
                'cid': video_info.get('cid', ''),
                'title': video_info.get('title', ''),
                'has_dash': any(fmt.get('protocol') == 'https_dash' for fmt in video_info.get('formats', [])),
                'format_count': len(video_info.get('formats', [])),
            }
        except Exception as e:
            logger.error(f"Failed to get API source info: {e}")
            return {'error': str(e)}
    
    def get_video_id(self, url: str) -> str:
        """Extract video ID from URL."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        bvid = self._get_bvid_from_url(url)
        if bvid:
            return bvid
        
        raise URLParseError(f"Cannot extract video ID from URL: {url}")
    
    def test_api_availability(self) -> Dict[str, Any]:
        """Test if Bilibili official API is available."""
        try:
            # Test with a known video
            test_bvid = "BV1GJ411x7h7"  # A common test video
            result = self._call_bilibili_api('/x/web-interface/view', {'bvid': test_bvid})
            
            if result:
                return {
                    'status': 'available',
                    'test_video': test_bvid,
                    'response_time': 'fast',  # Could measure actual time
                }
            else:
                return {
                    'status': 'unavailable',
                    'error': 'API returned no data',
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
            }
    
    def force_use_ytdlp(self, url: str) -> Dict[str, Any]:
        """Force using yt-dlp instead of API."""
        if not self.is_valid_url(url):
            raise URLParseError(f"Invalid Bilibili URL: {url}")
        
        logger.info("Force using yt-dlp")
        try:
            with yt_dlp.YoutubeDL(self.session_options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                result = {
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
                    'api_source': 'ytdlp_forced',
                }
                
                logger.info("Successfully retrieved video info via forced yt-dlp")
                return result
                
        except Exception as e:
            logger.error(f"Force yt-dlp failed: {e}")
            raise NetworkError(f"Failed to retrieve video information: {e}")


# Create global instance
bilibili_service = BilibiliService()