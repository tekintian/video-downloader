"""Flet主应用 - 四端统一视频下载器"""

import asyncio
import datetime as _datetime
from typing import Optional, Dict, Any, List
import flet as ft
from flet import Page, View, AppBar, IconButton, Text


# 导入页面
from .pages.home_page import HomePage
from .pages.download_page import DownloadPage
from .pages.player_page import PlayerPage
from .pages.settings_page import SettingsPage

# 导入服务
from .services.gui_service import GUIService
from .plugins.platform_manager import PlatformManager


class VideoDownloaderApp:
    """视频下载器主应用"""
    
    def __init__(self):
        self.gui_service = GUIService()
        self.platform_manager = PlatformManager()
        self.page: Optional[Page] = None
        self.appbar: Optional[AppBar] = None
        self.loading_dialog: Optional[ft.AlertDialog] = None
        
        # 应用状态
        self.current_route = "/"
        self.downloads: List[Dict[str, Any]] = []
        
    async def main(self, page: Page):
        """Flet主入口"""
        self.page = page
        # 记录启动日志以便排查 GUI 未出现的问题
        try:
            from pathlib import Path
            Path('flet-start.log').write_text(f"main started at {_datetime.datetime.now().isoformat()}, page.web={getattr(page, 'web', None)}\n")
        except Exception:
            pass

        try:
            await self.setup_page(page)
            from pathlib import Path
            Path('flet-start.log').write_text(Path('flet-start.log').read_text() + f"setup_page done at {_datetime.datetime.now().isoformat()}\n")

            await self.setup_navigation(page)
            Path('flet-start.log').write_text(Path('flet-start.log').read_text() + f"setup_navigation done at {_datetime.datetime.now().isoformat()}\n")
            
            # 显示默认页面
            await self.show_home()
            Path('flet-start.log').write_text(Path('flet-start.log').read_text() + f"show_home done at {_datetime.datetime.now().isoformat()}\n")
            
            page.update()
            Path('flet-start.log').write_text(Path('flet-start.log').read_text() + f"page.update called at {_datetime.datetime.now().isoformat()}\n")
        except Exception as e:
            import traceback
            from pathlib import Path
            Path('flet-start.log').write_text(Path('flet-start.log').read_text() + "EXCEPTION:\n" + traceback.format_exc())
            raise
    
    async def setup_page(self, page: Page):
        """配置页面"""
        page.title = "Video Downloader"
        page.theme_mode = ft.ThemeMode.DARK
        
        # 响应式布局
        if page.web:
            # Web端适配
            page.window.maximizable = True
            page.padding = 10
            page.window.width = 1200
            page.window.height = 800
        else:
            # 桌面端适配
            page.window.width = 1000
            page.window.height = 700
            page.window.resizable = True
            page.window.min_width = 800
            page.window.min_height = 600
        
        # 主题设置
        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            use_material3=True
        )
    
    async def setup_navigation(self, page: Page):
        """配置导航"""
        self.appbar = AppBar(
            title=Text(
                "Video Downloader", 
                size=24, 
                weight=ft.FontWeight.BOLD,
            ),
            
            actions=[
                IconButton(
                    "home",
                    tooltip="主页",
                    on_click=self.show_home
                ),
                IconButton(
                    "download",
                    tooltip="下载",
                    on_click=self.show_downloads
                ),
                IconButton(
                    "play_arrow",
                    tooltip="播放器",
                    on_click=self.show_player
                ),
                IconButton(
                    "settings",
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
        
        self.current_route = "/"
        await self._navigate_to_view(
            ft.View(
                "/",
                [home_page.build()],
                padding=ft.padding.all(10)
            )
        )
    
    async def show_downloads(self, e=None):
        """显示下载页面"""
        download_page = DownloadPage(
            gui_service=self.gui_service,
            downloads=self.downloads
        )
        
        self.current_route = "/downloads"
        await self._navigate_to_view(
            ft.View(
                "/downloads",
                [download_page.build()],
                padding=ft.padding.all(10)
            )
        )
    
    async def show_player(self, e=None):
        """显示播放器页面"""
        player_page = PlayerPage()
        
        self.current_route = "/player"
        await self._navigate_to_view(
            ft.View(
                "/player",
                [player_page.build()],
                padding=ft.padding.all(10)
            )
        )
    
    async def show_settings(self, e=None):
        """显示设置页面"""
        settings_page = SettingsPage(
            gui_service=self.gui_service
        )
        
        self.current_route = "/settings"
        await self._navigate_to_view(
            ft.View(
                "/settings",
                [settings_page.build()],
                padding=ft.padding.all(10)
            )
        )
    
    async def _navigate_to_view(self, view: View):
        """导航到指定视图"""
        if not self.page:
            return
        
        self.page.views.clear()
        self.page.views.append(view)
        self.page.route = view.route
        
        self.page.update()
    
    async def handle_url_submit(self, url: str):
        """处理URL提交"""
        if not url or not url.strip():
            await self.show_error("请输入有效的视频链接")
            return
        
        try:
            # 显示加载状态
            self.show_loading("正在解析视频...")
            self.page.update()
            
            # 验证并解析视频信息
            platform = self.platform_manager.get_platform_by_url(url)
            if not platform:
                await self.show_error("不支持的视频平台")
                return
            
            # 异步获取视频信息
            video_info = await platform.extract_video_info(url)
            
            if not video_info:
                await self.show_error("解析失败，请检查视频链接")
                return
            
            # 添加到下载列表
            download_item = {
                'id': len(self.downloads) + 1,
                'url': url,
                'platform': platform.name,
                'video_info': video_info,
                'status': 'pending',
                'progress': 0,
                'created_at': _datetime.datetime.now()
            }
            
            self.downloads.append(download_item)
            
            # 跳转到下载页面
            await self.show_downloads()
            
            # 自动开始下载
            await self.start_download(download_item)
            
        except Exception as e:
            import logging, traceback, pathlib
            traceback_text = traceback.format_exc()
            logging.error(f"URL解析错误: {e}")
            # 将完整的 traceback 写入文件，便于打包后查看
            pathlib.Path('last-exception.log').write_text(f"{_datetime.datetime.now().isoformat()}\n" + traceback_text)
            await self.show_error(f"解析失败: {str(e)}")
        finally:
            self.hide_loading()
            self.page.update()
    
    async def start_download(self, download_item: Dict[str, Any]):
        """开始下载"""
        try:
            download_item['status'] = 'downloading'
            self.page.update()
            
            # 这里会调用实际的下载逻辑
            # 暂时模拟下载进度
            for progress in range(0, 101, 10):
                download_item['progress'] = progress
                await asyncio.sleep(0.1)  # 模拟下载时间
                self.page.update()
            
            download_item['status'] = 'completed'
            await self.show_success("下载完成！")
            
        except Exception as e:
            download_item['status'] = 'failed'
            download_item['error'] = str(e)
            await self.show_error(f"下载失败: {str(e)}")
        
        self.page.update()
    
    def show_loading(self, message: str = "加载中..."):
        """显示加载对话框"""
        self.loading_dialog = ft.AlertDialog(
            modal=True,
            title=Text("请稍候"),
            content=Text(message),
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        if self.page:
            self.page.dialog = self.loading_dialog
            self.loading_dialog.open = True
    
    def hide_loading(self):
        """隐藏加载对话框"""
        if self.loading_dialog and self.page:
            self.loading_dialog.open = False
            self.page.dialog = None
    
    async def show_error(self, message: str):
        """显示错误提示"""
        snack_bar = ft.SnackBar(
            Text(message)
        )
        if self.page:
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
    
    async def show_success(self, message: str):
        """显示成功提示"""
        snack_bar = ft.SnackBar(
            Text(message)
        )
        if self.page:
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
    
    async def show_info(self, message: str):
        """显示信息提示"""
        snack_bar = ft.SnackBar(
            Text(message)
        )
        if self.page:
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()


# 全局应用实例
app = VideoDownloaderApp()

# 不同平台的启动函数
def main():
    """默认启动函数（桌面端）"""
    ft.app(target=app.main)

def run_web(host: str = '127.0.0.1', port: int = 8000):
    """运行Web版本"""
    print(f"Starting Web server on http://{host}:{port}")
    ft.app(target=app.main, view=ft.AppView.WEB_BROWSER, port=port, host=host)

def run_desktop():
    """运行桌面版本"""
    ft.app(target=app.main)

def run_mobile():
    """运行移动端版本"""
    ft.app(target=app.main, view=ft.AppView.FLET_APP)


if __name__ == "__main__":
    main()