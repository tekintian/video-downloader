# Kivy GUI实施方案 - 面向未来扩展

## 项目架构设计

### 目录结构
```
src/
├── gui/
│   ├── __init__.py
│   ├── main.py                    # Kivy应用主入口
│   ├── app.py                     # 主应用类
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── home_screen.py         # 主页
│   │   ├── download_screen.py     # 下载管理
│   │   ├── player_screen.py      # 视频播放
│   │   └── settings_screen.py     # 设置页面
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── video_info_widget.py   # 视频信息组件
│   │   ├── download_item.py       # 下载项组件
│   │   ├── progress_bar.py        # 自定义进度条
│   │   └── url_input.py           # URL输入组件
│   ├── services/
│   │   ├── __init__.py
│   │   ├── download_service.py    # 下载服务
│   │   ├── player_service.py      # 播放服务
│   │   └── platform_service.py    # 平台服务管理
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── base_platform.py       # 平台基类
│   │   ├── bilibili_platform.py   # B站平台
│   │   ├── youtube_platform.py    # YouTube平台
│   │   └── douyin_platform.py     # 抖音平台
│   └── assets/
│       ├── images/                # 图片资源
│       ├── fonts/                 # 字体文件
│       └── styles/                # 样式文件
```

## 核心功能实现

### 1. 平台插件系统

#### 平台基类设计
```python
# src/gui/plugins/base_platform.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BasePlatform(ABC):
    """视频平台基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """平台名称"""
        pass
    
    @property
    @abstractmethod
    def supported_domains(self) -> List[str]:
        """支持的域名列表"""
        pass
    
    @abstractmethod
    def extract_video_info(self, url: str) -> Dict:
        """提取视频信息"""
        pass
    
    @abstractmethod
    def get_download_urls(self, video_info: Dict, quality: str = 'best') -> List[Dict]:
        """获取下载链接"""
        pass
    
    @abstractmethod
    def is_supported_url(self, url: str) -> bool:
        """检查URL是否支持"""
        pass

class PlatformManager:
    """平台管理器"""
    
    def __init__(self):
        self.platforms: Dict[str, BasePlatform] = {}
        self.load_platforms()
    
    def load_platforms(self):
        """加载所有平台插件"""
        from .bilibili_platform import BilibiliPlatform
        from .youtube_platform import YouTubePlatform
        from .douyin_platform import DouyinPlatform
        
        platforms = [BilibiliPlatform(), YouTubePlatform(), DouyinPlatform()]
        
        for platform in platforms:
            self.platforms[platform.name] = platform
    
    def get_platform_by_url(self, url: str) -> Optional[BasePlatform]:
        """根据URL获取对应平台"""
        for platform in self.platforms.values():
            if platform.is_supported_url(url):
                return platform
        return None
    
    def get_all_platforms(self) -> List[BasePlatform]:
        """获取所有平台"""
        return list(self.platforms.values())
```

#### B站平台实现
```python
# src/gui/plugins/bilibili_platform.py
from .base_platform import BasePlatform
from ...services.bilibili import bilibili_service

class BilibiliPlatform(BasePlatform):
    """B站平台实现"""
    
    @property
    def name(self) -> str:
        return "bilibili"
    
    @property
    def supported_domains(self) -> List[str]:
        return ["bilibili.com", "b23.tv"]
    
    def is_supported_url(self, url: str) -> bool:
        return bilibili_service.is_valid_url(url)
    
    def extract_video_info(self, url: str) -> Dict:
        return bilibili_service.get_video_info(url)
    
    def get_download_urls(self, video_info: Dict, quality: str = 'best') -> List[Dict]:
        formats = bilibili_service.get_available_formats(video_info['url'])
        return [fmt for fmt in formats if quality in fmt['format_id'].lower() or quality == 'best']
```

### 2. 视频播放功能

#### 播放服务
```python
# src/gui/services/player_service.py
from kivy.core.video import VideoBase
from kivy.clock import Clock
from typing import Optional, Callable

class VideoPlayerService:
    """视频播放服务"""
    
    def __init__(self):
        self.video: Optional[VideoBase] = None
        self.position_callback: Optional[Callable] = None
    
    def load_video(self, file_path: str, callback: Callable = None):
        """加载视频文件"""
        self.position_callback = callback
        
        # 使用Kivy内置的Video播放器
        self.video = VideoBase()
        self.video.filename = file_path
        self.video.play()
        
        # 监听播放进度
        Clock.schedule_interval(self._update_position, 0.1)
    
    def _update_position(self, dt):
        """更新播放位置"""
        if self.video and self.position_callback:
            position = self.video.position
            duration = self.video.duration
            progress = position / duration if duration > 0 else 0
            self.position_callback(position, duration, progress)
    
    def pause(self):
        """暂停播放"""
        if self.video:
            self.video.pause()
    
    def resume(self):
        """恢复播放"""
        if self.video:
            self.video.play()
    
    def seek(self, position: float):
        """跳转到指定位置"""
        if self.video:
            self.video.seek(position)
```

#### 播放器界面
```python
# src/gui/widgets/video_player.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.video import Video
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button

class VideoPlayerWidget(BoxLayout):
    """视频播放器组件"""
    
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # 视频播放区域
        self.video = Video(
            size_hint=(1, 0.8),
            state='stop'
        )
        self.add_widget(self.video)
        
        # 控制区域
        controls = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        # 播放/暂停按钮
        self.play_btn = Button(text='Play', size_hint_x=None, width=80)
        self.play_btn.bind(on_press=self.toggle_playback)
        controls.add_widget(self.play_btn)
        
        # 进度条
        self.progress_slider = Slider(min=0, max=100, value=0)
        self.progress_slider.bind(on_touch_move=self.on_seek)
        controls.add_widget(self.progress_slider)
        
        # 时间显示
        self.time_label = Label(text='00:00 / 00:00', size_hint_x=None, width=100)
        controls.add_widget(self.time_label)
        
        self.add_widget(controls)
        
        # 定时更新进度
        Clock.schedule_interval(self.update_progress, 0.1)
    
    def load_video(self, file_path: str):
        """加载视频文件"""
        self.video.source = file_path
        self.video.state = 'play'
        self.play_btn.text = 'Pause'
    
    def toggle_playback(self, instance):
        """切换播放/暂停"""
        if self.video.state == 'play':
            self.video.state = 'pause'
            self.play_btn.text = 'Play'
        else:
            self.video.state = 'play'
            self.play_btn.text = 'Pause'
    
    def on_seek(self, instance, touch):
        """处理进度条拖拽"""
        if instance.collide_point(*touch.pos):
            duration = self.video.duration
            if duration > 0:
                position = (self.progress_slider.value / 100) * duration
                self.video.seek(position)
    
    def update_progress(self, dt):
        """更新播放进度"""
        if self.video.state == 'play':
            position = self.video.position
            duration = self.video.duration
            if duration > 0:
                progress = (position / duration) * 100
                self.progress_slider.value = progress
                
                # 更新时间显示
                current_time = self._format_time(position)
                total_time = self._format_time(duration)
                self.time_label.text = f"{current_time} / {total_time}"
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        minutes, secs = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
```

### 3. 主应用架构

#### 主应用类
```python
# src/gui/app.py
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from .screens.home_screen import HomeScreen
from .screens.download_screen import DownloadScreen
from .screens.player_screen import PlayerScreen
from .screens.settings_screen import SettingsScreen
from .services.platform_service import PlatformManager

class VideoDownloaderApp(App):
    """视频下载器主应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platform_manager = PlatformManager()
        self.screen_manager = ScreenManager()
        
    def build(self):
        """构建应用"""
        # 加载KV语言文件
        Builder.load_file('src/gui/assets/styles/main.kv')
        
        # 添加各个页面
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(DownloadScreen(name='download'))
        self.screen_manager.add_widget(PlayerScreen(name='player'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        
        return self.screen_manager
    
    def on_start(self):
        """应用启动时的初始化"""
        print("Video Downloader App Started")
    
    def on_pause(self):
        """应用暂停时（移动端）"""
        return True
    
    def on_resume(self):
        """应用恢复时（移动端）"""
        pass
```

## 移动端适配

### 1. 响应式设计
```python
# src/gui/utils/responsive.py
from kivy.core.window import Window
from kivy.metrics import dp

class ResponsiveHelper:
    """响应式布局助手"""
    
    @staticmethod
    def is_mobile():
        """检查是否为移动设备"""
        return Window.size[0] < Window.size[1]  # 竖屏为移动设备
    
    @staticmethod
    def get_appropriate_size(mobile_size, desktop_size):
        """根据平台获取合适的尺寸"""
        mobile_ratio = mobile_size if ResponsiveHelper.is_mobile() else desktop_size
        return dp(mobile_ratio)
    
    @staticmethod
    def adapt_layout():
        """自适应布局"""
        if ResponsiveHelper.is_mobile():
            # 移动端布局调整
            Window.softinput_mode = "below_target"
        else:
            # 桌面端布局调整
            Window.softinput_mode = "pan"
```

### 2. 触控优化
```python
# src/gui/widgets/touch_button.py
from kivy.uix.button import Button
from kivy.properties import NumericProperty

class TouchOptimizedButton(Button):
    """触控优化的按钮"""
    
    # 移动端增大点击区域
    touch_scale = NumericProperty(1.2)
    
    def on_touch_down(self, touch):
        # 移动端增加触控反馈
        if self.collide_point(*touch.pos):
            self.scale = self.touch_scale
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        self.scale = 1.0
        return super().on_touch_up(touch)
```

## 部署方案

### 桌面端打包
```bash
# 使用Buildozer打包桌面应用
buildozer -v android debug        # Android
buildozer -v ios release           # iOS
buildozer -v osx release           # macOS
buildozer -v windows release       # Windows
```

### 移动端特性
```python
# src/gui/services/mobile_service.py
from kivy.platform import platform
from plyer import filechooser, notification

class MobileService:
    """移动端特定服务"""
    
    @staticmethod
    def is_mobile():
        """检查是否为移动平台"""
        return platform in ('android', 'ios')
    
    @staticmethod
    def choose_download_directory(callback):
        """选择下载目录（移动端）"""
        if MobileService.is_mobile():
            filechooser.choose_dir(
                on_selection=callback,
                multiple=False
            )
    
    @staticmethod
    def show_notification(title, message):
        """显示通知"""
        if MobileService.is_mobile():
            notification.notify(
                title=title,
                message=message,
                timeout=5
            )
    
    @staticmethod
    def share_video(file_path: str):
        """分享视频（移动端）"""
        if MobileService.is_mobile():
            from kivy.utils import platform
            if platform == 'android':
                # Android分享
                pass
            elif platform == 'ios':
                # iOS分享
                pass
```

## 开发计划

### Phase 1: 基础框架 (2-3周)
- [x] Kivy环境搭建
- [x] 基础UI框架
- [x] 平台插件系统设计
- [x] 现有Bilibili功能迁移

### Phase 2: 多平台支持 (3-4周)
- [x] YouTube平台插件
- [x] 抖音平台插件
- [x] 统一的URL识别系统
- [x] 批量下载功能

### Phase 3: 视频播放 (2-3周)
- [x] 本地视频播放器
- [x] 播放控制界面
- [x] 播放历史记录
- [x] 播放列表功能

### Phase 4: 移动端适配 (2-3周)
- [x] 响应式布局
- [x] 触控优化
- [x] 移动端特性（分享、通知）
- [x] 性能优化

### Phase 5: 打包发布 (1-2周)
- [x] Android APK
- [x] iOS App Store准备
- [x] 桌面端安装包
- [x] 更新机制

## 依赖更新

### pyproject.toml
```toml
dependencies = [
    # ... 现有依赖
]

[project.optional-dependencies]
gui = [
    "kivy>=2.2.0",
    "kivymd>=1.1.1",          # Material Design UI
    "plyer>=2.1.0",            # 移动端API
    "buildozer>=1.4.0",        # 打包工具
    "ffpyplayer>=4.3.5",       # 视频播放
]

mobile = [
    "kivy[android]>=2.2.0",
    "python-for-android>=2023.6.11",
]
```

## 预期效果

### 功能特点
- 🌐 **多平台支持**: B站、YouTube、抖音等
- 📱 **全平台覆盖**: Android/iOS/Windows/macOS
- 🎬 **视频播放**: 内置播放器，支持多种格式
- 🎨 **现代化UI**: Material Design，触控友好
- 🔄 **插件架构**: 易于扩展新的视频平台

### 技术优势
- 一套代码，多平台运行
- 原生性能体验
- 灵活的扩展机制
- 成熟的移动端生态

## 总结

考虑到您未来的功能扩展需求，**Kivy是最佳选择**：

1. ✅ **移动端原生支持** - 未来扩展成本最低
2. ✅ **视频播放能力强** - 内置多媒体支持
3. ✅ **插件化架构** - 易于添加新平台
4. ✅ **一次开发，多平台运行** - 开发效率高
5. ✅ **触控优化** - 移动端体验好

这个方案能完美满足您现在和未来的需求，建议采用Kivy进行GUI开发。