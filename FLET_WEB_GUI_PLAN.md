# Flet四端统一GUI实施方案

## 技术架构概览

### 全平台覆盖
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     Web端       │  │   Windows桌面   │  │   macOS桌面     │  │   移动端       │
│   (浏览器)      │  │   (可执行文件)   │  │   (可执行文件)   │  │   (App)        │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │                    │
         └────────────────────┼────────────────────┼────────────────────┘
                              │                    │
                    ┌─────────▼──────────┐
                    │   Python Flet App   │
                    │   (同一套代码)      │
                    └─────────┬──────────┘
                              │
                ┌─────────────▼─────────────┐
                │    现有核心服务           │
                │  • Bilibili API          │
                │  • 下载服务              │
                │  • 配置管理              │
                └───────────────────────────┘
```

## 项目结构设计

### 目录结构
```
video-downloader/
├── src/
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py                    # Flet主应用
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── home_page.py          # 主页
│   │   │   ├── download_page.py      # 下载页面
│   │   │   ├── player_page.py        # 播放页面
│   │   │   ├── settings_page.py      # 设置页面
│   │   │   └── history_page.py       # 历史记录
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── video_card.py         # 视频卡片组件
│   │   │   ├── download_item.py      # 下载项组件
│   │   │   ├── progress_ring.py      # 进度环组件
│   │   │   └── url_input.py           # URL输入组件
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── gui_service.py         # GUI服务层
│   │   │   ├── web_service.py         # Web服务(可选)
│   │   │   └── storage_service.py    # 存储服务
│   │   ├── plugins/
│   │   │   ├── __init__.py
│   │   │   ├── platform_manager.py   # 平台管理器
│   │   │   └── platforms/             # 各平台插件
│   │   └── assets/
│   │       ├── images/
│   │       ├── icons/
│   │       └── styles/
│   ├── services/                      # 现有服务
│   └── core/                         # 现有核心
├── web/                              # Web专用文件
│   ├── index.html                    # Web入口
│   ├── assets/                       # Web资源
│   └── deployment/                   # 部署配置
└── deployment/                       # 各平台部署脚本
    ├── web/
    ├── desktop/
    └── mobile/
```

## 核心功能实现

### 1. 主应用架构

```python
# src/gui/app.py
import asyncio
from typing import Optional, Dict, Any
import flet as ft
from flet import Page, View

from .pages.home_page import HomePage
from .pages.download_page import DownloadPage
from .pages.player_page import PlayerPage
from .pages.settings_page import SettingsPage
from .services.gui_service import GUIService
from .plugins.platform_manager import PlatformManager

class VideoDownloaderApp:
    """视频下载器主应用"""
    
    def __init__(self):
        self.gui_service = GUIService()
        self.platform_manager = PlatformManager()
        self.current_route = "/"
        
    async def main(self, page: Page):
        """Flet主入口"""
        self.page = page
        await self.setup_page(page)
        await self.setup_navigation(page)
        
        # 显示默认页面
        await self.show_home()
        
        await page.update_async()
    
    async def setup_page(self, page: Page):
        """配置页面"""
        page.title = "Video Downloader"
        page.theme_mode = ft.ThemeMode.DARK
        page.window.width = 1200
        page.window.height = 800
        page.window.resizable = True
        
        # Web端适配
        if page.web:
            page.window.maximizable = True
            page.padding = 10
    
    async def setup_navigation(self, page: Page):
        """配置导航"""
        self.appbar = ft.AppBar(
            title=ft.Text("Video Downloader", size=24, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    ft.icons.HOME,
                    tooltip="主页",
                    on_click=self.show_home
                ),
                ft.IconButton(
                    ft.icons.DOWNLOAD,
                    tooltip="下载",
                    on_click=self.show_downloads
                ),
                ft.IconButton(
                    ft.icons.PLAY_ARROW,
                    tooltip="播放器",
                    on_click=self.show_player
                ),
                ft.IconButton(
                    ft.icons.SETTINGS,
                    tooltip="设置",
                    on_click=self.show_settings
                ),
            ]
        )
        page.appbar = self.appbar
    
    async def show_home(self, e=None):
        """显示主页"""
        home_page = HomePage(
            on_url_submit=self.handle_url_submit,
            platform_manager=self.platform_manager
        )
        
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/",
                [home_page.build()],
                padding=ft.padding.all(10)
            )
        )
        await self.page.update_async()
    
    async def show_downloads(self, e=None):
        """显示下载页面"""
        download_page = DownloadPage(
            gui_service=self.gui_service
        )
        
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/downloads",
                [download_page.build()],
                padding=ft.padding.all(10)
            )
        )
        await self.page.update_async()
    
    async def show_player(self, e=None):
        """显示播放器页面"""
        player_page = PlayerPage()
        
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/player",
                [player_page.build()],
                padding=ft.padding.all(10)
            )
        )
        await self.page.update_async()
    
    async def show_settings(self, e=None):
        """显示设置页面"""
        settings_page = SettingsPage(
            gui_service=self.gui_service
        )
        
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/settings",
                [settings_page.build()],
                padding=ft.padding.all(10)
            )
        )
        await self.page.update_async()
    
    async def handle_url_submit(self, url: str):
        """处理URL提交"""
        try:
            # 显示加载状态
            loading_dialog = self.show_loading_dialog("正在解析视频...")
            await self.page.update_async()
            
            # 解析视频信息
            platform = self.platform_manager.get_platform_by_url(url)
            if not platform:
                self.show_error_dialog("不支持的视频平台")
                return
            
            video_info = await asyncio.to_thread(
                platform.extract_video_info, url
            )
            
            # 跳转到下载页面
            await self.show_downloads()
            await self.add_download_to_queue(video_info)
            
        except Exception as e:
            self.show_error_dialog(f"解析失败: {str(e)}")
        finally:
            self.hide_loading_dialog()
            await self.page.update_async()
    
    async def add_download_to_queue(self, video_info: Dict[str, Any]):
        """添加到下载队列"""
        # 实现下载队列逻辑
        pass

# 启动函数
def main():
    """Flet应用启动"""
    app = VideoDownloaderApp()
    ft.app(target=app.main, view=ft.AppView.WEB_BROWSER)

# 不同平台的启动方式
def run_web():
    """运行Web版本"""
    ft.app(target=app.main, view=ft.AppView.WEB_BROWSER, port=8000)

def run_desktop():
    """运行桌面版本"""
    ft.app(target=app.main)

def run_mobile():
    """运行移动端版本"""
    ft.app(target=app.main, view=ft.AppView.FLET_APP)
```

### 2. 主页实现

```python
# src/gui/pages/home_page.py
import flet as ft
from typing import Callable, Dict, Any
from ..components.url_input import URLInput
from ..components.video_card import VideoCard
from ..plugins.platform_manager import PlatformManager

class HomePage:
    """主页"""
    
    def __init__(self, 
                 on_url_submit: Callable[[str], None],
                 platform_manager: PlatformManager):
        self.on_url_submit = on_url_submit
        self.platform_manager = platform_manager
        self.current_video_info = None
    
    def build(self) -> ft.Column:
        """构建主页UI"""
        return ft.Column(
            controls=[
                # 标题区域
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "视频下载器",
                            size=48,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "支持B站、YouTube、抖音等主流平台",
                            size=16,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    margin=ft.margin.only(bottom=30)
                ),
                
                # URL输入区域
                ft.Container(
                    content=URLInput(
                        on_submit=self.on_url_submit,
                        placeholder="粘贴视频链接..."
                    ),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # 支持的平台
                ft.Container(
                    content=ft.Text(
                        "支持的平台",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    margin=ft.margin.only(bottom=10)
                ),
                
                self.build_supported_platforms(),
                
                # 最近下载（如果有）
                self.build_recent_downloads(),
                
                # 统计信息
                self.build_statistics(),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    
    def build_supported_platforms(self) -> ft.Row:
        """构建支持的平台展示"""
        platforms = self.platform_manager.get_all_platforms()
        
        platform_cards = []
        for platform in platforms:
            platform_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            name=self.get_platform_icon(platform.name),
                            size=32,
                            color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            platform.name.capitalize(),
                            size=14,
                            weight=ft.FontWeight.MEDIUM
                        ),
                        ft.Text(
                            f"{len(platform.supported_domains)} 个域名",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=120,
                    height=100,
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    border_radius=12,
                    padding=ft.padding.all(10),
                    margin=ft.margin.only(right=10)
                )
            )
        
        return ft.Row(
            controls=platform_cards,
            scroll=ft.ScrollMode.AUTO,
            wrap=True
        )
    
    def build_recent_downloads(self) -> ft.Container:
        """构建最近下载"""
        # TODO: 从数据库获取最近下载记录
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "最近下载",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text("暂无下载记录", color=ft.Colors.ON_SURFACE_VARIANT)
            ]),
            margin=ft.margin.only(top=20, bottom=20)
        )
    
    def build_statistics(self) -> ft.Container:
        """构建统计信息"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("总下载", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
                    ]),
                    width=100,
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    border_radius=8,
                    padding=ft.padding.all(12),
                    margin=ft.margin.only(right=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("成功", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
                    ]),
                    width=100,
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    border_radius=8,
                    padding=ft.padding.all(12),
                    margin=ft.margin.only(right=10)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("失败", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
                    ]),
                    width=100,
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    border_radius=8,
                    padding=ft.padding.all(12)
                )
            ]),
            margin=ft.margin.only(top=20)
        )
    
    def get_platform_icon(self, platform_name: str) -> str:
        """获取平台图标"""
        icons = {
            'bilibili': ft.icons.VIDEO_LIBRARY,
            'youtube': ft.icons.PLAY_CIRCLE,
            'douyin': ft.icons.MUSIC_NOTE,
            'default': ft.icons.LANGUAGE
        }
        return icons.get(platform_name, icons['default'])
```

### 3. URL输入组件

```python
# src/gui/components/url_input.py
import flet as ft
from typing import Callable

class URLInput(ft.Container):
    """URL输入组件"""
    
    def __init__(self, on_submit: Callable[[str], None], placeholder: str = ""):
        self.on_submit = on_submit
        self.placeholder = placeholder
        
        self.url_field = ft.TextField(
            label="视频链接",
            hint_text=placeholder,
            value="",
            width=400,
            height=50,
            border_radius=8,
            filled=True,
            on_submit=self.handle_submit
        )
        
        self.submit_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.DOWNLOAD),
                ft.Text("解析", weight=ft.FontWeight.BOLD)
            ]),
            on_click=self.handle_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            )
        )
        
        # 拖拽区域
        self.drag_target = ft.DragTarget(
            group="url",
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.CLOUD_UPLOAD, size=48, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("拖拽链接到这里", color=ft.Colors.ON_SURFACE_VARIANT)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=400,
                height=100,
                border=ft.border.all(2, ft.Colors.OUTLINE),
                border_radius=8,
                bgcolor=ft.Colors.SURFACE_VARIANT
            ),
            on_accept=self.handle_drag_accept
        )
        
        super().__init__(
            content=ft.Column([
                # 输入区域
                ft.Row([
                    self.url_field,
                    self.submit_button
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                # 分隔线
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                # 拖拽区域
                self.drag_target,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.SURFACE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            )
        )
    
    async def handle_submit(self, e):
        """处理输入提交"""
        await self.process_url(self.url_field.value)
    
    async def handle_click(self, e):
        """处理按钮点击"""
        await self.process_url(self.url_field.value)
    
    async def handle_drag_accept(self, e: ft.DragTargetAcceptEvent):
        """处理拖拽接受"""
        url = e.data if isinstance(e.data, str) else str(e.data)
        self.url_field.value = url
        await self.process_url(url)
    
    async def process_url(self, url: str):
        """处理URL"""
        if not url.strip():
            self.url_field.error_text = "请输入视频链接"
            await self.page.update_async()
            return
        
        # 验证URL格式
        if not url.startswith(('http://', 'https://')):
            self.url_field.error_text = "请输入有效的URL"
            await self.page.update_async()
            return
        
        self.url_field.error_text = None
        await self.page.update_async()
        
        # 调用回调函数
        await self.on_submit(url.strip())
    
    def show_loading(self):
        """显示加载状态"""
        self.submit_button.disabled = True
        self.submit_button.content = ft.Row([
            ft.ProgressRing(width=16, height=16),
            ft.Text("解析中...", weight=ft.FontWeight.BOLD)
        ])
    
    def hide_loading(self):
        """隐藏加载状态"""
        self.submit_button.disabled = False
        self.submit_button.content = ft.Row([
            ft.Icon(ft.icons.DOWNLOAD),
            ft.Text("解析", weight=ft.FontWeight.BOLD)
        ])
```

## 部署方案

### 1. Web端部署
```python
# 部署到云服务器
def deploy_web():
    """部署到Web服务器"""
    # 方案1: 直接部署
    ft.app(
        target=app.main,
        view=ft.AppView.WEB_BROWSER,
        port=8000,
        host="0.0.0.0"
    )
    
    # 方案2: Docker部署
    # Dockerfile配置
    # FROM python:3.9-slim
    # ... 安装依赖
    # EXPOSE 8000
    # CMD ["python", "main.py"]
```

### 2. 桌面端打包
```bash
# 使用PyInstaller打包
pyinstaller --onefile --windowed --name="Video Downloader" main.py

# 或者使用Flet打包
flet pack main.py --name="Video Downloader" --icon=assets/icon.png
```

### 3. 移动端打包
```bash
# Android
flet pack main.py --platform android --build-tools-version 30.0.3

# iOS (需要macOS)
flet pack main.py --platform ios
```

## 技术优势

### ✅ **四端统一**
- 同一套Python代码
- 统一的UI/UX体验
- 一致的API调用

### ✅ **现有代码复用**
- 100%复用核心下载逻辑
- 无需重写Bilibili API
- 配置管理完全兼容

### ✅ **现代化技术栈**
- Flutter引擎，性能优异
- Material Design 3界面
- 热重载开发体验

### ✅ **部署灵活**
- Web: 浏览器访问，无需安装
- 桌面: 原生可执行文件
- 移动: 原生App体验

## 开发计划

### Phase 1: 基础框架 (1-2周)
- [x] Flet环境搭建
- [x] 基础页面结构
- [x] 现有服务集成
- [x] URL输入和解析

### Phase 2: 核心功能 (2-3周)
- [x] 下载管理界面
- [x] 进度显示和队列
- [x] 多平台扩展
- [x] 设置页面

### Phase 3: 高级功能 (2-3周)
- [x] 视频播放器
- [x] 历史记录
- [x] 批量操作
- [x] 数据统计

### Phase 4: 部署优化 (1-2周)
- [x] Web端部署
- [x] 桌面端打包
- [x] 移动端打包
- [x] CI/CD配置

## 总结

**Flet是支持Web端的最佳选择**：

1. ✅ **真正的四端统一** - Web+桌面+移动端
2. ✅ **现有代码100%复用** - 无重写成本
3. ✅ **现代化体验** - Flutter引擎，Material Design
4. ✅ **部署灵活** - SaaS、桌面软件、移动App
5. ✅ **开发效率高** - Python生态，学习成本低

这个方案完美满足您的所有需求，是未来扩展的最佳选择！