"""播放器页面 - 视频播放界面"""

import flet as ft
from typing import List, Dict, Any, Optional
import os


class PlayerPage:
    """视频播放器页面"""
    
    def __init__(self):
        self.current_video: Optional[Dict[str, Any]] = None
        self.video_path: Optional[str] = None
        self.is_playing = False
        self.current_time = 0
        self.total_time = 0
        
    def build(self) -> ft.Column:
        """构建播放器页面UI"""
        return ft.Column(
            controls=[
                # 页面标题
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            "play_arrow",
                            size=32
                        ),
                        ft.Text(
                            "视频播放器",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Container(height=10),
                        # 打开文件按钮
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon("folder_open"),
                                ft.Text("打开文件")
                            ]),
                            on_click=self.open_file_dialog
                        )
                    ]),
                    padding=ft.padding.symmetric(vertical=10),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # 播放器主体
                ft.Container(
                    content=self.build_video_player(),
                    expand=True
                ),
                
                # 播放控制栏
                self.build_controls(),
                
                # 播放列表
                self.build_playlist()
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )
    
    def build_video_player(self) -> ft.Container:
        """构建视频播放器"""
        return ft.Container(
            content=ft.Stack([
                # 视频显示区域
                ft.Container(
                    content=self.get_video_display(),
                    width=800,
                    height=450,
                    border_radius=12
                ),
                
                # 中心播放按钮（当没有视频时显示）
                ft.Container(
                    content=ft.Icon(
                        "play_circle",
                        size=80
                    ),
                    visible=not self.current_video
                )
            ]),
            margin=ft.margin.only(bottom=20)
        )
    
    def get_video_display(self) -> ft.Control:
        """获取视频显示控件"""
        if self.current_video and self.video_path:
            # 如果有视频文件，这里应该使用视频播放器组件
            # Flet目前没有内置的视频播放器，需要使用WebView或自定义组件
            return ft.Image(
                src=self.current_video.get('thumbnail', ''),
                width=800,
                height=450,
                fit=ft.ImageFit.CONTAIN,
                border_radius=12
            )
        else:
            # 默认占位符
            return ft.Column([
                ft.Icon(
                    "video_library",
                    size=120
                ),
                ft.Text(
                    "请选择视频文件",
                    size=18
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def build_controls(self) -> ft.Container:
        """构建播放控制栏"""
        return ft.Container(
            content=ft.Column([
                # 进度条
                ft.Container(
                    content=ft.Slider(
                        value=0,
                        min=0,
                        max=100,
                        divisions=100,
                        label="{value}%",
                        on_change=self.on_seek
                    ),
                    padding=ft.padding.symmetric(horizontal=10)
                ),
                
                # 控制按钮
                ft.Row([
                    # 播放/暂停按钮
                    ft.IconButton(
                        icon="pause" if self.is_playing else "play_arrow",
                        icon_size=32,
                        on_click=self.toggle_playback
                    ),
                    
                    # 停止按钮
                    ft.IconButton(
                        icon="stop",
                        icon_size=28,
                        on_click=self.stop_playback
                    ),
                    
                    ft.Container(height=10),
                    
                    # 时间显示
                    ft.Text(
                        self.format_time(self.current_time) + " / " + self.format_time(self.total_time),
                        size=14
                    ),
                    
                    ft.Container(height=10),
                    
                    # 音量控制
                    ft.Row([
                        ft.Icon(
                            "volume_up",
                            size=24
                        ),
                        ft.Slider(
                            value=50,
                            min=0,
                            max=100,
                            width=100,
                            on_change=self.on_volume_change
                        )
                    ]),
                    
                    # 全屏按钮
                    ft.IconButton(
                        icon="fullscreen",
                        icon_size=24,
                        on_click=self.toggle_fullscreen
                    )
                ])
            ]),
            padding=ft.padding.all(15),
            border_radius=8,
            margin=ft.margin.only(bottom=20)
        )
    
    def build_playlist(self) -> ft.Container:
        """构建播放列表"""
        # 模拟播放列表数据
        playlist_items = [
            {
                'title': '【官方 MV】Never Gonna Give You Up',
                'duration': 213,
                'thumbnail': ''
            },
            {
                'title': '【4K】Nature Documentary',
                'duration': 1800,
                'thumbnail': ''
            },
            {
                'title': 'Tutorial: Python GUI',
                'duration': 3600,
                'thumbnail': ''
            }
        ]
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        "queue_play_next",
                        size=24
                    ),
                    ft.Text(
                        "播放列表",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        f"{len(playlist_items)} 个视频",
                        size=14
                    )
                ]),
                ft.Divider(height=1),
                ft.Column(
                    controls=[
                        self.build_playlist_item(item, i == 0)
                        for i, item in enumerate(playlist_items)
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    height=200
                )
            ]),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            padding=ft.padding.all(15)
        )
    
    def build_playlist_item(self, item: Dict[str, Any], is_current: bool = False) -> ft.Container:
        """构建播放列表项"""
        return ft.Container(
            content=ft.Row([
                # 缩略图
                ft.Container(
                    content=ft.Icon(
                        "video_file" if not is_current else "play_arrow",
                        size=32
                    ),
                    width=60,
                    height=40,
                    border_radius=4
                ),
                
                # 视频信息
                ft.Column([
                    ft.Text(
                        item['title'],
                        size=14,
                        weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL
                    ),
                    ft.Text(
                        self.format_time(item['duration']),
                        size=12
                    )
                ]),
                
                ft.Container(height=10),
                
                # 操作按钮
                ft.Row([
                    ft.IconButton(
                        icon="play_arrow",
                        icon_size=20,
                        on_click=lambda e, i=item: self.play_item(i)
                    ),
                    ft.IconButton(
                        icon="more_vert",
                        icon_size=20,
                        on_click=lambda e, i=item: self.show_item_menu(i)
                    )
                ])
            ]),
            padding=ft.padding.symmetric(vertical=8, horizontal=10),
            border_radius=6,
            margin=ft.margin.only(bottom=5)
        )
    
    async def open_file_dialog(self, e):
        """打开文件对话框"""
        # 在实际实现中，这里会调用文件选择器
        # Flet目前没有内置的文件选择器，需要使用平台特定的API
        print("打开文件对话框")
        
        # 模拟选择文件
        self.load_video_file("mock_video_path.mp4")
    
    def load_video_file(self, file_path: str):
        """加载视频文件"""
        if not os.path.exists(file_path):
            return
        
        self.video_path = file_path
        self.current_video = {
            'title': os.path.basename(file_path),
            'path': file_path,
            'thumbnail': '',  # 需要生成缩略图
            'duration': 0
        }
        
        # 这里需要重新构建播放器界面
        # 由于Flet的限制，实际实现可能需要使用WebView组件
    
    async def toggle_playback(self, e):
        """切换播放/暂停"""
        self.is_playing = not self.is_playing
        
        # 更新按钮图标
        e.control.icon = "pause" if self.is_playing else "play_arrow"
        await e.control.page.update()
    
    async def stop_playback(self, e):
        """停止播放"""
        self.is_playing = False
        self.current_time = 0
        
        # 更新UI
        await e.control.page.update()
    
    async def on_seek(self, e):
        """处理进度条拖拽"""
        if self.total_time > 0:
            self.current_time = (e.control.value / 100) * self.total_time
    
    async def on_volume_change(self, e):
        """处理音量变化"""
        volume = e.control.value
        print(f"音量设置为: {volume}")
    
    async def toggle_fullscreen(self, e):
        """切换全屏"""
        print("切换全屏模式")
    
    async def play_item(self, item: Dict[str, Any]):
        """播放指定项目"""
        self.current_video = item
        self.current_time = 0
        self.is_playing = True
        print(f"播放: {item['title']}")
    
    async def show_item_menu(self, item: Dict[str, Any]):
        """显示项目菜单"""
        print(f"显示菜单: {item['title']}")
    
    def format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        if not seconds or seconds <= 0:
            return "00:00"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"