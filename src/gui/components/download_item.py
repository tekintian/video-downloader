"""下载项组件 - 显示单个下载任务的详细信息"""

import flet as ft
from typing import Dict, Any, Callable, Optional, List
import datetime


class DownloadItem(ft.Container):
    """下载项组件"""
    
    def __init__(self, 
                 download: Dict[str, Any],
                 on_pause: Optional[Callable] = None,
                 on_resume: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None,
                 on_retry: Optional[Callable] = None,
                 on_select: Optional[Callable] = None):
        
        self.download = download
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_cancel = on_cancel
        self.on_retry = on_retry
        self.on_select = on_select
        
        # 下载状态
        self.status = download.get('status', 'pending')
        self.progress = download.get('progress', 0)
        self.error = download.get('error', None)
        
        # 视频信息
        self.video_info = download.get('video_info', {})
        self.title = self.video_info.get('title', '未知标题')
        self.uploader = self.video_info.get('uploader', '未知UP主')
        self.duration = self.video_info.get('duration', 0)
        self.size = download.get('file_size', 0)
        
        super().__init__(
            content=self.build_item(),
            padding=ft.padding.all(12),
            border_radius=8,
            bgcolor=self.get_background_color(),
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            margin=ft.margin.only(bottom=8)
        )
    
    def build_item(self) -> ft.Column:
        """构建下载项内容"""
        return ft.Column([
            # 顶部信息行
            ft.Row([
                # 选择框
                ft.Checkbox(
                    value=False,
                    on_change=self.handle_select
                ),
                
                # 视频信息
                ft.Column([
                    ft.Text(
                        self.title,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Row([
                        ft.Icon(
                            "person",
                            size=14,
                            color=ft.Colors.WHITE
                        ),
                        ft.Text(
                            self.uploader,
                            size=12,
                            color=ft.Colors.WHITE,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Container(
                            content=ft.Text(f"• {self.format_duration(self.duration)}"),
                            margin=ft.margin.only(left=5, right=5),
                            color=ft.Colors.WHITE
                        ),
                        ft.Text(
                            self.format_file_size(self.size),
                            size=12,
                            color=ft.Colors.WHITE
                        )
                    ])
                ], expand=True),
                
                # 状态标签
                ft.Container(
                    content=ft.Text(
                        self.get_status_text(),
                        size=12,
                        weight=ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=self.get_status_color(),
                    border_radius=4
                )
            ]),
            
            # 进度条（下载中时显示）
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            f"{self.progress:.1f}%",
                            size=12,
                            color=ft.Colors.WHITE
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            self.format_speed(),
                            size=12,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    ft.ProgressBar(
                        value=self.progress / 100,
                        bgcolor=ft.Colors.GREY_700,
                        color=ft.Colors.BLUE
                    )
                ]),
                visible=self.status == 'downloading',
                margin=ft.margin.only(top=8, bottom=4)
            ),
            
            # 错误信息（失败时显示）
            ft.Container(
                content=ft.Row([
                    ft.Icon(
                        "error_outline",
                        size=16,
                        color=ft.Colors.RED
                    ),
                    ft.Text(
                        self.error or "下载失败",
                        size=12,
                        color=ft.Colors.RED,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ]),
                visible=self.status == 'failed',
                margin=ft.margin.only(top=8),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED),
                padding=ft.padding.all(8),
                border_radius=4
            ),
            
            # 操作按钮
            ft.Row([
                self.build_action_buttons(),
                ft.Container(height=10),
                
                # 更多选项
                ft.IconButton(
                    icon="more_vert",
                    icon_size=20,
                    on_click=self.show_more_options
                )
            ], alignment=ft.MainAxisAlignment.START)
        ], spacing=8)
    
    def build_action_buttons(self) -> ft.Row:
        """构建操作按钮"""
        buttons = []
        
        if self.status == 'pending':
            buttons.append(
                ft.IconButton(
                    icon="play_arrow",
                    icon_size=20,
                    tooltip="开始下载",
                    on_click=self.handle_start,
                    bgcolor=ft.Colors.GREEN,
                    icon_color=ft.Colors.WHITE
                )
            )
            buttons.append(
                ft.IconButton(
                    icon="delete_rounded",
                    icon_size=20,
                    tooltip="删除",
                    on_click=self.handle_cancel,
                    bgcolor=ft.Colors.RED,
                    icon_color=ft.Colors.WHITE
                )
            )
        
        elif self.status == 'downloading':
            buttons.append(
                ft.IconButton(
                    icon="pause",
                    icon_size=20,
                    tooltip="暂停",
                    on_click=self.handle_pause,
                    bgcolor=ft.Colors.ORANGE,
                    icon_color=ft.Colors.WHITE
                )
            )
            buttons.append(
                ft.IconButton(
                    icon="stop",
                    icon_size=20,
                    tooltip="停止",
                    on_click=self.handle_cancel,
                    bgcolor=ft.Colors.RED,
                    icon_color=ft.Colors.WHITE
                )
            )
        
        elif self.status == 'paused':
            buttons.append(
                ft.IconButton(
                    icon="play_arrow",
                    icon_size=20,
                    tooltip="继续",
                    on_click=self.handle_resume,
                    bgcolor=ft.Colors.GREEN,
                    icon_color=ft.Colors.WHITE
                )
            )
            buttons.append(
                ft.IconButton(
                    icon="delete_rounded",
                    icon_size=20,
                    tooltip="删除",
                    on_click=self.handle_cancel,
                    bgcolor=ft.Colors.RED,
                    icon_color=ft.Colors.WHITE
                )
            )
        
        elif self.status == 'completed':
            buttons.append(
                ft.IconButton(
                    icon="folder_open",
                    icon_size=20,
                    tooltip="打开文件夹",
                    on_click=self.handle_open_folder
                )
            )
            buttons.append(
                ft.IconButton(
                    icon="play_arrow",
                    icon_size=20,
                    tooltip="播放",
                    on_click=self.handle_play
                )
            )
        
        elif self.status == 'failed':
            buttons.append(
                ft.IconButton(
                    icon="refresh_rounded",
                    icon_size=20,
                    tooltip="重试",
                    on_click=self.handle_retry,
                    bgcolor=ft.Colors.ORANGE,
                    icon_color=ft.Colors.WHITE
                )
            )
            buttons.append(
                ft.IconButton(
                    icon="delete_rounded",
                    icon_size=20,
                    tooltip="删除",
                    on_click=self.handle_cancel,
                    bgcolor=ft.Colors.RED,
                    icon_color=ft.Colors.WHITE
                )
            )
        
        return ft.Row(buttons, spacing=8)
    
    async def handle_select(self, e):
        """处理选择框变化"""
        if self.on_select:
            await self.on_select(self.download)
    
    async def handle_start(self, e):
        """处理开始下载"""
        self.status = 'downloading'
        self.update_ui()
        if self.on_resume:  # 复用resume逻辑
            await self.on_resume(self.download)
    
    async def handle_pause(self, e):
        """处理暂停下载"""
        self.status = 'paused'
        self.update_ui()
        if self.on_pause:
            await self.on_pause(self.download)
    
    async def handle_resume(self, e):
        """处理继续下载"""
        self.status = 'downloading'
        self.update_ui()
        if self.on_resume:
            await self.on_resume(self.download)
    
    async def handle_cancel(self, e):
        """处理取消下载"""
        if self.on_cancel:
            await self.on_cancel(self.download)
    
    async def handle_retry(self, e):
        """处理重试下载"""
        self.status = 'pending'
        self.progress = 0
        self.error = None
        self.update_ui()
        if self.on_retry:
            await self.on_retry(self.download)
    
    async def handle_open_folder(self, e):
        """处理打开文件夹"""
        print("打开文件夹")
    
    async def handle_play(self, e):
        """处理播放视频"""
        print("播放视频")
    
    async def show_more_options(self, e):
        """显示更多选项"""
        print("显示更多选项")
    
    def update_ui(self):
        """更新UI"""
        self.bgcolor = self.get_background_color()
        self.content = self.build_item()
        if self.page:
            self.update()
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        status_map = {
            'pending': '等待中',
            'downloading': '下载中',
            'paused': '已暂停',
            'completed': '已完成',
            'failed': '已失败',
            'cancelled': '已取消'
        }
        return status_map.get(self.status, '未知')
    
    def get_status_color(self):
        """获取状态颜色"""
        color_map = {
            'pending': ft.Colors.ORANGE,
            'downloading': ft.Colors.BLUE,
            'paused': ft.Colors.ORANGE,
            'completed': ft.Colors.GREEN,
            'failed': ft.Colors.RED,
            'cancelled': ft.Colors.GREY
        }
        return color_map.get(self.status, ft.Colors.GREY)
    
    def get_background_color(self) -> str:
        """获取背景颜色"""
        if self.status == 'failed':
            return ft.Colors.with_opacity(0.05, ft.Colors.RED)
        elif self.status == 'completed':
            return ft.Colors.with_opacity(0.05, ft.Colors.GREEN)
        else:
            return ft.Colors.TRANSPARENT
    
    def format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if not seconds or seconds <= 0:
            return "未知"
        
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
    
    def format_speed(self) -> str:
        """格式化下载速度"""
        # 这里需要实际的下载速度数据
        # 暂时返回模拟值
        if self.status == 'downloading':
            return f"{(self.progress * 100):.0f} KB/s"
        return ""
    
    def update_progress(self, progress: float):
        """更新进度"""
        self.progress = progress
        self.update_ui()
    
    def set_status(self, status: str, error: str = None):
        """设置状态"""
        self.status = status
        self.error = error
        self.update_ui()


class CompactDownloadItem(DownloadItem):
    """紧凑版下载项"""
    
    def build_item(self) -> ft.Column:
        """构建紧凑版下载项"""
        return ft.Row([
            # 选择框
            ft.Checkbox(
                value=False,
                on_change=self.handle_select
            ),
            
            # 标题和状态
            ft.Column([
                ft.Text(
                    self.title,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Row([
                    ft.Text(
                        self.get_status_text(),
                        size=10,
                        color=self.get_status_color(),
                        weight=ft.FontWeight.NORMAL
                    ),
                    ft.Text(
                        f"• {self.progress:.0f}%",
                        size=10,
                        color=ft.Colors.WHITE,
                        visible=self.status == 'downloading'
                    )
                ], spacing=5)
            ], expand=True),
            
            # 进度条（简化）
            ft.ProgressBar(
                value=self.progress / 100,
                width=100,
                bgcolor=ft.Colors.GREY_700,
                color=ft.Colors.BLUE,
                visible=self.status == 'downloading'
            ),
            
            # 操作按钮（简化）
            ft.Row([
                self.build_compact_action_buttons()
            ], spacing=4)
        ], alignment=ft.MainAxisAlignment.CENTER)
    
    def build_compact_action_buttons(self) -> List[ft.IconButton]:
        """构建紧凑版操作按钮"""
        buttons = []
        
        if self.status == 'pending':
            buttons.append(
                ft.IconButton(
                    icon="play_arrow",
                    icon_size=16,
                    tooltip="开始",
                    on_click=self.handle_start
                )
            )
        elif self.status == 'downloading':
            buttons.append(
                ft.IconButton(
                    icon="pause",
                    icon_size=16,
                    tooltip="暂停",
                    on_click=self.handle_pause
                )
            )
        elif self.status == 'paused':
            buttons.append(
                ft.IconButton(
                    icon="play_arrow",
                    icon_size=16,
                    tooltip="继续",
                    on_click=self.handle_resume
                )
            )
        elif self.status == 'completed':
            buttons.append(
                ft.IconButton(
                    icon="play_arrow",
                    icon_size=16,
                    tooltip="播放",
                    on_click=self.handle_play
                )
            )
        elif self.status == 'failed':
            buttons.append(
                ft.IconButton(
                    icon="refresh_rounded",
                    icon_size=16,
                    tooltip="重试",
                    on_click=self.handle_retry
                )
            )
        
        return buttons