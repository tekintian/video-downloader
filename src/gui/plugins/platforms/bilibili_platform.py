"""B站平台实现"""

import asyncio
from typing import Dict, List, Any, Optional
from ..base_platform import BasePlatform, VideoPlatformMixin, APIBasedPlatform
from src.services.bilibili import bilibili_service


class BilibiliPlatform(APIBasedPlatform, VideoPlatformMixin):
    """B站平台实现"""
    
    def __init__(self):
        super().__init__()
        self._name = "bilibili"
        self._supported_domains = ["bilibili.com", "b23.tv"]
        self._supported_qualities = ["4K", "1080P+", "1080P", "720P", "480P", "360P"]
        self._features = {
            'video_download': True,
            'audio_download': True,
            'subtitle_download': True,
            'playlist_download': False,
            'live_download': False,
            'dash_support': True,
            'chunked_download': True,
            'resume_download': True
        }
        self._description = "Bilibili - 中国领先的视频分享网站"
        self._platform_type = "video"
        self._requires_auth = False
        self._rate_limit = None
    
    @property
    def name(self) -> str:
        """平台名称"""
        return self._name
        self._supported_qualities = ["4K", "1080P+", "1080P", "720P", "480P", "360P"]
        self._features = {
            'video_download': True,
            'audio_download': True,
            'subtitle_download': True,
            'playlist_download': False,
            'live_download': False,
            'dash_support': True,
            'chunked_download': True,
            'resume_download': True
        }
        self._description = "哔哩哔哩 (B站) - 中国最大的二次元文化社区"
        self._platform_type = "video"
        self._base_url = "https://api.bilibili.com"
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self._rate_limit = 2  # 每秒最多2个请求
    
    def is_supported_url(self, url: str) -> bool:
        """检查URL是否支持"""
        if not url:
            return False
        
        url = url.lower()
        patterns = [
            r'bilibili\.com/video/[a-zA-Z0-9]+',
            r'bilibili\.com/bangumi/play/[a-zA-Z]+[0-9]+',
            r'b23\.tv/[a-zA-Z0-9]+',
        ]
        
        import re
        return any(re.search(pattern, url) for pattern in patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从URL提取视频ID"""
        import re
        
        patterns = [
            r'/video/([a-zA-Z0-9]+)',
            r'BV([a-zA-Z0-9]+)',
            r'b23\.tv/([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if not video_id.startswith('BV'):
                    video_id = f"BV{video_id}"
                return video_id
        
        return None
    
    async def extract_video_info(self, url: str) -> Dict[str, Any]:
        """提取视频信息"""
        try:
            # 使用现有的bilibili_service
            video_info = await asyncio.to_thread(
                bilibili_service.get_video_info, url
            )
            
            # 标准化返回格式
            return {
                'id': video_info.get('id', ''),
                'title': video_info.get('title', ''),
                'description': video_info.get('description', ''),
                'duration': video_info.get('duration', 0),
                'uploader': video_info.get('uploader', ''),
                'upload_date': video_info.get('upload_date', ''),
                'view_count': video_info.get('view_count', 0),
                'like_count': video_info.get('like_count', 0),
                'thumbnail': video_info.get('thumbnail', ''),
                'url': url,
                'platform': self.name,
                'api_source': video_info.get('api_source', 'official'),
                'formats': video_info.get('formats', []),
                'subtitles': video_info.get('subtitles', {}),
                'cid': video_info.get('cid'),
                'bvid': video_info.get('bvid'),
            }
            
        except Exception as e:
            raise Exception(f"B站视频信息提取失败: {str(e)}")
    
    def get_download_urls(self, video_info: Dict[str, Any], quality: str = 'best') -> List[Dict[str, Any]]:
        """获取下载链接"""
        try:
            formats = video_info.get('formats', [])
            if not formats:
                return []
            
            # 根据质量选择格式
            selected_formats = self._select_formats_by_quality(formats, quality)
            
            download_urls = []
            for fmt in selected_formats:
                download_urls.append({
                    'url': fmt.get('url', ''),
                    'format_id': fmt.get('format_id', ''),
                    'quality': fmt.get('format_note', ''),
                    'file_size': fmt.get('filesize', 0),
                    'ext': fmt.get('ext', 'mp4'),
                    'vcodec': fmt.get('vcodec', ''),
                    'acodec': fmt.get('acodec', ''),
                    'fps': fmt.get('fps', 0),
                    'width': fmt.get('width', 0),
                    'height': fmt.get('height', 0),
                    'protocol': fmt.get('protocol', 'http'),
                })
            
            return download_urls
            
        except Exception as e:
            raise Exception(f"B站下载链接获取失败: {str(e)}")
    
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
            print(f"获取B站字幕失败: {e}")
            return []
    
    def _select_formats_by_quality(self, formats: List[Dict], quality: str) -> List[Dict]:
        """根据质量选择格式"""
        if not formats:
            return []
        
        # 分离视频和音频格式
        video_formats = [f for f in formats if f.get('vcodec') != 'none']
        audio_formats = [f for f in formats if f.get('acodec') != 'none']
        
        if quality == 'best':
            # 选择最高质量
            selected = []
            
            if video_formats:
                # 按分辨率排序
                video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)), reverse=True)
                selected.append(video_formats[0])
            
            if audio_formats:
                # 选择最好的音频
                audio_formats.sort(key=lambda x: x.get('filesize', 0), reverse=True)
                selected.append(audio_formats[0])
            
            return selected
        
        elif quality == 'worst':
            # 选择最低质量
            selected = []
            
            if video_formats:
                video_formats.sort(key=lambda x: (x.get('height', 0), x.get('filesize', 0)))
                selected.append(video_formats[0])
            
            if audio_formats:
                audio_formats.sort(key=lambda x: x.get('filesize', 0))
                selected.append(audio_formats[0])
            
            return selected
        
        else:
            # 指定质量
            # 首先尝试精确匹配
            for fmt in video_formats:
                if quality.lower() in fmt.get('format_note', '').lower():
                    selected = [fmt]
                    # 添加最佳音频
                    if audio_formats:
                        audio_formats.sort(key=lambda x: x.get('filesize', 0), reverse=True)
                        selected.append(audio_formats[0])
                    return selected
            
            # 如果没有精确匹配，返回best
            return self._select_formats_by_quality(formats, 'best')
    
    async def get_video_stats(self, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取视频统计信息"""
        bvid = video_info.get('bvid')
        if not bvid:
            return {}
        
        try:
            # 获取详细统计信息
            stats_data = await self.get('/x/web-interface/stat', {'bvid': bvid})
            
            return {
                'view': stats_data.get('view', 0),
                'danmaku': stats_data.get('danmaku', 0),
                'reply': stats_data.get('reply', 0),
                'favorite': stats_data.get('favorite', 0),
                'coin': stats_data.get('coin', 0),
                'share': stats_data.get('share', 0),
                'like': stats_data.get('like', 0),
            }
            
        except Exception as e:
            print(f"获取B站统计信息失败: {e}")
            return {}
    
    async def check_video_available(self, bvid: str) -> bool:
        """检查视频是否可用"""
        try:
            data = await self.get('/x/web-interface/view', {'bvid': bvid})
            return data is not None
            
        except Exception:
            return False
    
    def get_quality_mapping(self) -> Dict[str, int]:
        """获取质量等级映射"""
        return {
            '4K': 120,
            '1080P+': 116,
            '1080P': 112,
            '720P': 80,
            '480P': 74,
            '360P': 64,
        }
    
    def format_quality_string(self, quality: str) -> str:
        """格式化质量字符串"""
        mapping = {
            '4k': '4K 超清',
            '1080p+': '1080P+ 高清',
            '1080p': '1080P 高清',
            '720p': '720P 标清',
            '480p': '480P 流畅',
            '360p': '360P 流畅',
        }
        return mapping.get(quality.lower(), quality)
    
    def get_platform_features_description(self) -> str:
        """获取平台特性描述"""
        return (
            "✅ 官方API解析，速度快、准确性高\n"
            "✅ 支持DASH格式，音视频分离下载\n"
            "✅ 支持多种清晰度：4K、1080P+、1080P、720P等\n"
            "✅ 支持字幕下载\n"
            "✅ 支持断点续传\n"
            "✅ 自动回退到yt-dlp，确保高成功率"
        )