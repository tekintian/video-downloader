"""YouTube平台实现"""

import asyncio
from typing import Dict, List, Any, Optional
from ..base_platform import BasePlatform, VideoPlatformMixin


class YouTubePlatform(BasePlatform, VideoPlatformMixin):
    """YouTube平台实现"""
    
    def __init__(self):
        super().__init__()
        self._name = "youtube"
        self._supported_domains = ["youtube.com", "youtu.be"]
        self._supported_qualities = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p"]
        self._features = {
            'video_download': True,
            'audio_download': True,
            'subtitle_download': True,
            'playlist_download': True,
            'live_download': False,
            'dash_support': True,
            'chunked_download': True,
            'resume_download': True
        }
        self._description = "YouTube - 全球最大的视频分享平台"
        self._platform_type = "video"
        self._requires_auth = False
        self._rate_limit = None
    
    @property
    def name(self) -> str:
        """平台名称"""
        return self._name
        self._supported_qualities = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p"]
        self._features = {
            'video_download': True,
            'audio_download': True,
            'subtitle_download': True,
            'playlist_download': True,
            'live_download': False,
            'dash_support': True,
            'chunked_download': True,
            'resume_download': True
        }
        self._description = "YouTube - 全球最大的视频分享平台"
        self._platform_type = "video"
        self._requires_auth = False
    
    def is_supported_url(self, url: str) -> bool:
        """检查URL是否支持"""
        if not url:
            return False
        
        url = url.lower()
        patterns = [
            r'youtube\.com/watch\?v=[a-zA-Z0-9_-]+',
            r'youtu\.be/[a-zA-Z0-9_-]+',
            r'youtube\.com/embed/[a-zA-Z0-9_-]+',
            r'youtube\.com/shorts/[a-zA-Z0-9_-]+',
        ]
        
        import re
        return any(re.search(pattern, url) for pattern in patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从URL提取视频ID"""
        import re
        from urllib.parse import urlparse, parse_qs
        
        # 标准格式：youtube.com/watch?v=VIDEO_ID
        if 'youtube.com/watch' in url:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            if 'v' in query and query['v']:
                return query['v'][0]
        
        # 短格式：youtu.be/VIDEO_ID
        elif 'youtu.be/' in url:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        # 嵌入格式：youtube.com/embed/VIDEO_ID
        elif 'youtube.com/embed/' in url:
            match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        # Shorts格式：youtube.com/shorts/VIDEO_ID
        elif 'youtube.com/shorts/' in url:
            match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        return None
    
    async def extract_video_info(self, url: str) -> Dict[str, Any]:
        """提取视频信息"""
        try:
            # 使用yt-dlp获取YouTube信息
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': False,
                'extract_flat': False,
            }
            
            def _extract_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await asyncio.to_thread(_extract_info)
            
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
                'url': url,
                'platform': self.name,
                'api_source': 'ytdlp',
                'formats': info.get('formats', []),
                'subtitles': info.get('subtitles', {}),
                'tags': info.get('tags', []),
                'categories': info.get('categories', []),
                'channel_id': info.get('channel_id', ''),
                'channel_url': info.get('channel_url', ''),
                'age_limit': info.get('age_limit', 0),
            }
            
        except Exception as e:
            raise Exception(f"YouTube视频信息提取失败: {str(e)}")
    
    def get_download_urls(self, video_info: Dict[str, Any], quality: str = 'best') -> List[Dict[str, Any]]:
        """获取下载链接"""
        try:
            formats = video_info.get('formats', [])
            if not formats:
                return []
            
            # 选择最佳格式
            selected_format = self._select_best_format(formats, quality)
            
            if selected_format:
                return [{
                    'url': selected_format.get('url', ''),
                    'format_id': selected_format.get('format_id', ''),
                    'quality': selected_format.get('format_note', ''),
                    'file_size': selected_format.get('filesize', 0),
                    'ext': selected_format.get('ext', 'mp4'),
                    'vcodec': selected_format.get('vcodec', ''),
                    'acodec': selected_format.get('acodec', ''),
                    'fps': selected_format.get('fps', 0),
                    'width': selected_format.get('width', 0),
                    'height': selected_format.get('height', 0),
                    'protocol': selected_format.get('protocol', 'https'),
                }]
            
            return []
            
        except Exception as e:
            raise Exception(f"YouTube下载链接获取失败: {str(e)}")
    
    async def get_subtitle_info(self, video_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取字幕信息"""
        try:
            subtitles = video_info.get('subtitles', {})
            subtitle_info = []
            
            for lang, subtitle_data in subtitles.items():
                if isinstance(subtitle_data, list):
                    for sub in subtitle_data:
                        subtitle_info.append({
                            'language': lang,
                            'url': sub.get('url', ''),
                            'format': sub.get('ext', 'srt'),
                            'label': sub.get('name', lang)
                        })
                elif isinstance(subtitle_data, dict):
                    subtitle_info.append({
                        'language': lang,
                        'url': subtitle_data.get('url', ''),
                        'format': subtitle_data.get('ext', 'srt'),
                        'label': subtitle_data.get('name', lang)
                    })
            
            return subtitle_info
            
        except Exception as e:
            print(f"获取YouTube字幕失败: {e}")
            return []
    
    async def get_playlist_info(self, url: str) -> Dict[str, Any]:
        """获取播放列表信息"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': False,
                'extract_flat': True,
            }
            
            def _extract_playlist():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            playlist_info = await asyncio.to_thread(_extract_playlist)
            
            return {
                'id': playlist_info.get('id', ''),
                'title': playlist_info.get('title', ''),
                'description': playlist_info.get('description', ''),
                'uploader': playlist_info.get('uploader', ''),
                'uploader_id': playlist_info.get('uploader_id', ''),
                'uploader_url': playlist_info.get('uploader_url', ''),
                'url': url,
                'platform': self.name,
                'type': 'playlist',
                'entries': playlist_info.get('entries', []),
                'entry_count': len(playlist_info.get('entries', [])),
            }
            
        except Exception as e:
            raise Exception(f"YouTube播放列表信息提取失败: {str(e)}")
    
    def _select_best_format(self, formats: List[Dict], quality: str = 'best') -> Optional[Dict]:
        """选择最佳格式"""
        # 过滤出包含视频和音频的格式
        valid_formats = [f for f in formats if 
                        f.get('vcodec') != 'none' and 
                        f.get('acodec') != 'none' and
                        f.get('url')]
        
        if not valid_formats:
            # 如果没有完整的格式，选择视频格式
            valid_formats = [f for f in formats if 
                           f.get('vcodec') != 'none' and 
                           f.get('url')]
        
        if not valid_formats:
            return None
        
        if quality == 'best':
            # 选择分辨率最高的
            valid_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)
        elif quality == 'worst':
            # 选择分辨率最低的
            valid_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)))
        else:
            # 尝试匹配指定质量
            for fmt in valid_formats:
                if quality.lower() in fmt.get('format_note', '').lower():
                    return fmt
            # 如果没有匹配，选择最佳
            valid_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)
        
        return valid_formats[0]
    
    def get_quality_mapping(self) -> Dict[str, str]:
        """获取质量映射"""
        return {
            '2160p': '4K',
            '1440p': '2K',
            '1080p': 'FHD',
            '720p': 'HD',
            '480p': 'SD',
            '360p': '360P',
            '240p': '240P',
        }
    
    def format_quality_string(self, quality: str) -> str:
        """格式化质量字符串"""
        mapping = {
            '2160p': '4K 超清',
            '1440p': '2K 超清',
            '1080p': '1080P 全高清',
            '720p': '720P 高清',
            '480p': '480P 标清',
            '360p': '360P 流畅',
            '240p': '240P 流畅',
        }
        return mapping.get(quality.lower(), quality)
    
    def get_platform_features_description(self) -> str:
        """获取平台特性描述"""
        return (
            "✅ 基于yt-dlp引擎，支持YouTube所有功能\n"
            "✅ 支持各种视频格式和质量选择\n"
            "✅ 支持字幕和自动生成字幕\n"
            "✅ 支持播放列表批量下载\n"
            "✅ 支持视频和音频分离下载\n"
            "✅ 支持断点续传和分段下载"
        )