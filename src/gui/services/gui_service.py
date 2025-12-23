"""GUI服务 - GUI相关的业务逻辑服务"""

import asyncio
from typing import Dict, Any, List, Optional
import json
import os

from src.core.config import config_manager


class GUIService:
    """GUI服务类，处理GUI相关的业务逻辑"""
    
    def __init__(self):
        self.config_file = "gui_config.json"
        self.default_config = {
            'theme_mode': 'dark',
            'language': 'zh_CN',
            'download_dir': './downloads',
            'window_size': {'width': 1000, 'height': 700},
            'window_position': {'x': None, 'y': None},
            'auto_save': True,
            'show_notifications': True,
            'compact_mode': False,
            'default_quality': 'best',
            'max_concurrent_downloads': 3,
            'auto_clear_completed': False,
            'remember_window_state': True
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载GUI配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"加载GUI配置失败: {e}")
            return self.default_config.copy()
    
    async def save_config(self):
        """保存GUI配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存GUI配置失败: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    async def set_config(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value
        await self.save_config()
    
    async def reset_config(self):
        """重置配置"""
        self.config = self.default_config.copy()
        await self.save_config()
    
    # 窗口管理相关方法
    def get_window_size(self) -> Dict[str, int]:
        """获取窗口大小"""
        return self.config.get('window_size', {'width': 1000, 'height': 700})
    
    async def set_window_size(self, width: int, height: int):
        """设置窗口大小"""
        if self.config.get('remember_window_state', True):
            self.config['window_size'] = {'width': width, 'height': height}
            await self.save_config()
    
    def get_window_position(self) -> Dict[str, Optional[int]]:
        """获取窗口位置"""
        return self.config.get('window_position', {'x': None, 'y': None})
    
    async def set_window_position(self, x: Optional[int], y: Optional[int]):
        """设置窗口位置"""
        if self.config.get('remember_window_state', True) and x is not None and y is not None:
            self.config['window_position'] = {'x': x, 'y': y}
            await self.save_config()
    
    # 下载设置相关方法
    def get_download_dir(self) -> str:
        """获取下载目录"""
        return self.config.get('download_dir', './downloads')
    
    async def set_download_dir(self, directory: str):
        """设置下载目录"""
        # 确保目录存在
        os.makedirs(directory, exist_ok=True)
        self.config['download_dir'] = directory
        await self.save_config()
    
    def get_default_quality(self) -> str:
        """获取默认视频质量"""
        return self.config.get('default_quality', 'best')
    
    async def set_default_quality(self, quality: str):
        """设置默认视频质量"""
        self.config['default_quality'] = quality
        await self.save_config()
    
    def get_max_concurrent_downloads(self) -> int:
        """获取最大并发下载数"""
        return self.config.get('max_concurrent_downloads', 3)
    
    async def set_max_concurrent_downloads(self, count: int):
        """设置最大并发下载数"""
        self.config['max_concurrent_downloads'] = max(1, min(count, 10))
        await self.save_config()
    
    # 主题相关方法
    def get_theme_mode(self) -> str:
        """获取主题模式"""
        return self.config.get('theme_mode', 'dark')
    
    async def set_theme_mode(self, theme: str):
        """设置主题模式"""
        if theme in ['light', 'dark', 'system']:
            self.config['theme_mode'] = theme
            await self.save_config()
    
    # 语言相关方法
    def get_language(self) -> str:
        """获取语言设置"""
        return self.config.get('language', 'zh_CN')
    
    async def set_language(self, language: str):
        """设置语言"""
        self.config['language'] = language
        await self.save_config()
    
    # 通知相关方法
    def show_notifications_enabled(self) -> bool:
        """是否显示通知"""
        return self.config.get('show_notifications', True)
    
    async def set_notifications_enabled(self, enabled: bool):
        """设置通知开关"""
        self.config['show_notifications'] = enabled
        await self.save_config()
    
    # UI模式相关方法
    def is_compact_mode(self) -> bool:
        """是否紧凑模式"""
        return self.config.get('compact_mode', False)
    
    async def set_compact_mode(self, compact: bool):
        """设置紧凑模式"""
        self.config['compact_mode'] = compact
        await self.save_config()
    
    # 数据管理相关方法
    async def get_download_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取下载历史"""
        # 这里可以从数据库或文件中读取历史记录
        # 暂时返回空列表
        return []
    
    async def add_to_history(self, video_info: Dict[str, Any]):
        """添加到历史记录"""
        # 实现历史记录保存逻辑
        pass
    
    async def clear_history(self):
        """清空历史记录"""
        # 实现历史记录清空逻辑
        pass
    
    # 统计相关方法
    async def get_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        stats = {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size_downloaded': 0,
            'favorite_platform': 'bilibili',
            'download_time_saved': 0
        }
        
        # 这里应该从数据库中读取实际统计信息
        # 暂时返回模拟数据
        return stats
    
    # 备份和恢复
    async def export_settings(self, file_path: str) -> bool:
        """导出设置到文件"""
        try:
            export_data = {
                'config': self.config,
                'version': '1.0.0',
                'export_time': str(asyncio.get_event_loop().time())
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False
    
    async def import_settings(self, file_path: str) -> bool:
        """从文件导入设置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'config' in import_data:
                self.config.update(import_data['config'])
                await self.save_config()
                return True
            return False
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False
    
    # 应用更新相关
    async def check_for_updates(self) -> Dict[str, Any]:
        """检查应用更新"""
        # 这里可以实现更新检查逻辑
        return {
            'has_update': False,
            'current_version': '1.0.0',
            'latest_version': '1.0.0',
            'update_url': None
        }
    
    def get_app_info(self) -> Dict[str, Any]:
        """获取应用信息"""
        return {
            'name': 'Video Downloader',
            'version': '1.0.0',
            'author': 'Video Downloader Team',
            'description': '现代化的视频下载工具',
            'homepage': 'https://github.com/tekintian/video-downloader',
            'platforms_supported': ['Windows', 'macOS', 'Linux', 'Android', 'iOS', 'Web']
        }


# 全局GUI服务实例
gui_service = GUIService()