"""平台基类 - 所有视频平台插件的基础接口"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio


class BasePlatform(ABC):
    """视频平台基类，定义所有平台插件必须实现的接口"""
    
    def __init__(self):
        self._name = ""
        self._supported_domains = []
        self._supported_qualities = []
        self._features = {}
        self._description = ""
        self._platform_type = "video"
        self._requires_auth = False
        self._rate_limit = None
    
    @property
    @abstractmethod
    def name(self) -> str:
        """平台名称（必须唯一）"""
        pass
    
    @property
    def supported_domains(self) -> List[str]:
        """支持的域名列表"""
        return self._supported_domains
    
    @property
    def supported_qualities(self) -> List[str]:
        """支持的视频质量列表"""
        return self._supported_qualities
    
    @property
    def features(self) -> Dict[str, Any]:
        """平台特性"""
        default_features = {
            'video_download': True,
            'audio_download': True,
            'subtitle_download': False,
            'playlist_download': False,
            'live_download': False,
            'dash_support': False,
            'chunked_download': False,
            'resume_download': False
        }
        return {**default_features, **self._features}
    
    @property
    def description(self) -> str:
        """平台描述"""
        return self._description
    
    @property
    def platform_type(self) -> str:
        """平台类型：video, music, live, etc."""
        return self._platform_type
    
    @property
    def requires_auth(self) -> bool:
        """是否需要认证"""
        return self._requires_auth
    
    @property
    def rate_limit(self) -> Optional[int]:
        """请求频率限制（每秒请求数）"""
        return self._rate_limit
    
    @abstractmethod
    def is_supported_url(self, url: str) -> bool:
        """检查URL是否支持"""
        pass
    
    @abstractmethod
    async def extract_video_info(self, url: str) -> Dict[str, Any]:
        """提取视频信息"""
        pass
    
    @abstractmethod
    def get_download_urls(self, video_info: Dict[str, Any], quality: str = 'best') -> List[Dict[str, Any]]:
        """获取下载链接"""
        pass
    
    # 可选实现的接口
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """认证接口（可选）"""
        if not self.requires_auth:
            return True
        raise NotImplementedError(f"平台 {self.name} 需要实现认证接口")
    
    async def get_playlist_info(self, url: str) -> Dict[str, Any]:
        """获取播放列表信息（可选）"""
        if not self.features.get('playlist_download', False):
            raise NotImplementedError(f"平台 {self.name} 不支持播放列表下载")
        raise NotImplementedError(f"平台 {self.name} 需要实现播放列表接口")
    
    async def get_subtitle_info(self, video_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取字幕信息（可选）"""
        if not self.features.get('subtitle_download', False):
            return []
        raise NotImplementedError(f"平台 {self.name} 需要实现字幕接口")
    
    async def get_live_info(self, url: str) -> Dict[str, Any]:
        """获取直播信息（可选）"""
        if not self.features.get('live_download', False):
            raise NotImplementedError(f"平台 {self.name} 不支持直播下载")
        raise NotImplementedError(f"平台 {self.name} 需要实现直播接口")
    
    # 工具方法
    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        if not url or not isinstance(url, str):
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        return self.is_supported_url(url)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """从URL提取视频ID（可选实现）"""
        return None
    
    def normalize_url(self, url: str) -> str:
        """标准化URL（可选实现）"""
        return url
    
    def format_quality_string(self, quality: str) -> str:
        """格式化质量字符串（可选实现）"""
        return quality
    
    # 统计和监控方法
    def get_usage_statistics(self) -> Dict[str, Any]:
        """获取使用统计（可选实现）"""
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'last_used': None
        }
    
    def reset_statistics(self):
        """重置统计信息（可选实现）"""
        pass
    
    # 配置相关方法
    def get_config(self) -> Dict[str, Any]:
        """获取平台配置（可选实现）"""
        return {}
    
    def set_config(self, config: Dict[str, Any]):
        """设置平台配置（可选实现）"""
        pass
    
    # 调试和日志方法
    def get_debug_info(self) -> Dict[str, Any]:
        """获取调试信息（可选实现）"""
        return {
            'name': self.name,
            'version': getattr(self, 'version', '1.0.0'),
            'supported_domains': self.supported_domains,
            'features': self.features,
            'config': self.get_config()
        }
    
    # 生命周期方法
    async def initialize(self):
        """初始化平台（可选实现）"""
        pass
    
    async def cleanup(self):
        """清理资源（可选实现）"""
        pass


class VideoPlatformMixin:
    """视频平台混入类，提供视频平台的通用功能"""
    
    def get_standard_video_info_fields(self) -> List[str]:
        """获取标准视频信息字段"""
        return [
            'id', 'title', 'description', 'duration', 'uploader',
            'upload_date', 'view_count', 'like_count', 'thumbnail',
            'formats', 'subtitles', 'tags', 'categories'
        ]
    
    def format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if not seconds or seconds <= 0:
            return "00:00"
        
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if not size_bytes or size_bytes <= 0:
            return "未知"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"
    
    def extract_thumbnail_url(self, video_info: Dict[str, Any]) -> str:
        """提取缩略图URL"""
        # 常见的缩略图字段名
        thumbnail_fields = ['thumbnail', 'cover', 'poster', 'image_url']
        
        for field in thumbnail_fields:
            if field in video_info and video_info[field]:
                return video_info[field]
        
        return ""
    
    def validate_quality(self, quality: str, available_qualities: List[str]) -> str:
        """验证和标准化质量"""
        if quality == 'best':
            return available_qualities[0] if available_qualities else 'best'
        elif quality == 'worst':
            return available_qualities[-1] if available_qualities else 'worst'
        
        # 精确匹配
        if quality in available_qualities:
            return quality
        
        # 模糊匹配
        for available_quality in available_qualities:
            if quality.lower() in available_quality.lower():
                return available_quality
        
        # 返回默认质量
        return 'best'


class APIBasedPlatform(BasePlatform):
    """基于API的平台基类"""
    
    def __init__(self):
        super().__init__()
        self._base_url = ""
        self._headers = {}
        self._timeout = 30
        self._session = None
    
    @property
    def base_url(self) -> str:
        """API基础URL"""
        return self._base_url
    
    @property
    def headers(self) -> Dict[str, str]:
        """默认请求头"""
        return self._headers.copy()
    
    async def initialize(self):
        """初始化会话"""
        import aiohttp
        
        self._session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self._timeout)
        )
    
    async def cleanup(self):
        """清理会话"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送API请求"""
        if not self._session:
            await self.initialize()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self._session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise Exception(f"API请求失败 {url}: {str(e)}")
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """GET请求"""
        return await self.make_request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Dict = None, json: Dict = None) -> Dict[str, Any]:
        """POST请求"""
        return await self.make_request('POST', endpoint, data=data, json=json)