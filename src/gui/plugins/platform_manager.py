"""平台管理器 - 管理所有视频平台插件"""

from typing import Dict, List, Optional
from .base_platform import BasePlatform
from .platforms.bilibili_platform import BilibiliPlatform
from .platforms.youtube_platform import YouTubePlatform
from .platforms.douyin_platform import DouyinPlatform


class PlatformManager:
    """平台管理器"""
    
    def __init__(self):
        self.platforms: Dict[str, BasePlatform] = {}
        self.domain_mapping: Dict[str, BasePlatform] = {}
        self.load_platforms()
    
    def load_platforms(self):
        """加载所有平台插件"""
        platforms = [
            BilibiliPlatform(),
            YouTubePlatform(),
            DouyinPlatform(),
        ]
        
        for platform in platforms:
            self.register_platform(platform)
    
    def register_platform(self, platform: BasePlatform):
        """注册平台"""
        # 检查平台名称是否已存在
        if platform.name in self.platforms:
            print(f"警告: 平台 {platform.name} 已存在，将被覆盖")
        
        # 注册平台
        self.platforms[platform.name] = platform
        
        # 注册域名映射
        for domain in platform.supported_domains:
            if domain in self.domain_mapping:
                print(f"警告: 域名 {domain} 已被平台 {self.domain_mapping[domain].name} 使用")
            else:
                self.domain_mapping[domain] = platform
        
        print(f"已注册平台: {platform.name} (支持域名: {platform.supported_domains})")
    
    def unregister_platform(self, platform_name: str) -> bool:
        """注销平台"""
        if platform_name not in self.platforms:
            return False
        
        platform = self.platforms[platform_name]
        
        # 从域名映射中移除
        for domain in platform.supported_domains:
            if domain in self.domain_mapping:
                del self.domain_mapping[domain]
        
        # 从平台列表中移除
        del self.platforms[platform_name]
        print(f"已注销平台: {platform_name}")
        return True
    
    def get_platform_by_name(self, name: str) -> Optional[BasePlatform]:
        """根据名称获取平台"""
        return self.platforms.get(name)
    
    def get_platform_by_url(self, url: str) -> Optional[BasePlatform]:
        """根据URL获取对应平台"""
        # 提取域名
        from urllib.parse import urlparse
        parsed_url = urlparse(url.lower())
        hostname = parsed_url.netloc
        
        # 移除www前缀
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        
        # 查找匹配的域名
        for domain, platform in self.domain_mapping.items():
            if domain in hostname:
                return platform
        
        # 如果没有直接匹配，尝试URL模式匹配
        for platform in self.platforms.values():
            if platform.is_supported_url(url):
                return platform
        
        return None
    
    def get_all_platforms(self) -> List[BasePlatform]:
        """获取所有平台"""
        return list(self.platforms.values())
    
    def get_supported_domains(self) -> List[str]:
        """获取所有支持的域名"""
        return list(self.domain_mapping.keys())
    
    def is_url_supported(self, url: str) -> bool:
        """检查URL是否被支持"""
        return self.get_platform_by_url(url) is not None
    
    def get_platform_info(self) -> Dict[str, Dict]:
        """获取所有平台信息"""
        info = {}
        for name, platform in self.platforms.items():
            info[name] = {
                'name': platform.name,
                'supported_domains': platform.supported_domains,
                'supported_qualities': getattr(platform, 'supported_qualities', []),
                'features': getattr(platform, 'features', {}),
                'description': getattr(platform, 'description', '')
            }
        return info
    
    async def extract_video_info(self, url: str) -> Optional[Dict]:
        """提取视频信息"""
        platform = self.get_platform_by_url(url)
        if not platform:
            raise ValueError(f"不支持的视频平台或URL: {url}")
        
        return await platform.extract_video_info(url)
    
    async def get_download_urls(self, url: str, quality: str = 'best') -> List[Dict]:
        """获取下载链接"""
        platform = self.get_platform_by_url(url)
        if not platform:
            raise ValueError(f"不支持的视频平台或URL: {url}")
        
        video_info = await platform.extract_video_info(url)
        return platform.get_download_urls(video_info, quality)
    
    def get_platform_statistics(self) -> Dict[str, int]:
        """获取平台统计信息"""
        stats = {
            'total_platforms': len(self.platforms),
            'total_domains': len(self.domain_mapping),
            'platforms_by_type': {}
        }
        
        for platform in self.platforms.values():
            platform_type = getattr(platform, 'platform_type', 'unknown')
            stats['platforms_by_type'][platform_type] = stats['platforms_by_type'].get(platform_type, 0) + 1
        
        return stats
    
    def validate_platform_config(self, platform_config: Dict) -> List[str]:
        """验证平台配置"""
        errors = []
        
        required_fields = ['name', 'class_path', 'supported_domains']
        for field in required_fields:
            if field not in platform_config:
                errors.append(f"缺少必需字段: {field}")
        
        if 'class_path' in platform_config:
            class_path = platform_config['class_path']
            if not isinstance(class_path, str) or '.' not in class_path:
                errors.append("class_path 必须是有效的Python模块路径")
        
        if 'supported_domains' in platform_config:
            domains = platform_config['supported_domains']
            if not isinstance(domains, list) or not domains:
                errors.append("supported_domains 必须是非空列表")
        
        return errors
    
    async def load_external_platforms(self, config_file: str) -> bool:
        """从配置文件加载外部平台"""
        import json
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            platforms_config = config.get('platforms', [])
            loaded_count = 0
            
            for platform_config in platforms_config:
                # 验证配置
                errors = self.validate_platform_config(platform_config)
                if errors:
                    print(f"平台配置错误: {platform_config.get('name', 'unknown')}: {errors}")
                    continue
                
                # 动态导入平台类
                try:
                    module_path, class_name = platform_config['class_path'].rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    platform_class = getattr(module, class_name)
                    
                    # 创建平台实例
                    platform = platform_class()
                    self.register_platform(platform)
                    loaded_count += 1
                    
                except Exception as e:
                    print(f"加载外部平台失败 {platform_config.get('name', 'unknown')}: {e}")
            
            print(f"成功加载 {loaded_count} 个外部平台")
            return loaded_count > 0
            
        except Exception as e:
            print(f"加载外部平台配置失败: {e}")
            return False


# 全局平台管理器实例
platform_manager = PlatformManager()