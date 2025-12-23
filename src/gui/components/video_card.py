"""视频卡片组件 - 显示视频信息"""

import flet as ft
from typing import Dict, Any, Optional


class VideoCard(ft.Container):
    """视频信息卡片组件"""
    
    def __init__(self, video_info: Dict[str, Any], on_download=None):
        self.video_info = video_info,
        self.on_download = on_download
        
        # 提取视频信息
        self.title = video_info.get('title', '未知标题')
        self.duration = video_info.get('duration', 0)
        self.uploader = video_info.get('uploader', '未知UP主')
        self.view_count = video_info.get('view_count', 0)
        self.thumbnail = video_info.get('thumbnail', '')
        self.description = video_info.get('description', '')
        
        super().__init__(
            content=self.build_card(),
            width=300,
            border_radius=12,
            padding=ft.padding.all(15),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                offset=ft.Offset(0, 2)
            )
        )
    
    def build_card(self) -> ft.Column:
        """构建卡片内容"""
        return ft.Column([
            # 缩略图区域
            self.build_thumbnail_section(),
            
            # 视频信息区域
            self.build_info_section(),
            
            # 操作按钮区域
            self.build_action_section()
        ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=10),
    
    def build_thumbnail_section(self) -> ft.Container:
        """构建缩略图区域"""
        if self.thumbnail:
            thumbnail_widget = ft.Image(
                src=self.thumbnail,
                width=270,
                height=150,
                fit=ft.ImageFit.COVER,
                border_radius=8,
                repeat=ft.ImageRepeat.NO_REPEAT
            )
        else:
            # 默认占位符
            thumbnail_widget = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        "video_library",
                        size=48,
                    ),
                    ft.Text(
                        "无缩略图",
                        size=12,
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=270,
                height=150,
                border_radius=8,
            )
        
        return ft.Container(
            content=ft.Stack([
                thumbnail_widget,
                # 时长标签（如果有）
                ft.Container(
                    content=ft.Text(
                        self.format_duration(self.duration),
                        size=12,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=4,
                    margin=ft.margin.only(right=10, bottom=10),
                    visible=self.duration > 0
                )
            ]),
            margin=ft.margin.only(bottom=10)
        )
    
    def build_info_section(self) -> ft.Column:
        """构建视频信息区域"""
        return ft.Column([
            # 标题
            ft.Text(
                self.title,
                size=16,
                weight=ft.FontWeight.BOLD,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            
            # UP主信息
            ft.Row([
                ft.Icon(
                    "person",
                    size=16,
                ),
                ft.Text(
                    self.uploader,
                    size=14,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Container(height=10),
                # 播放量
                ft.Row([
                    ft.Icon(
                        "visibility",
                        size=16,
                    ),
                    ft.Text(
                        self.format_view_count(self.view_count),
                        size=12,
                    )
                ])
            ]),
            
            # 描述（截断）
            ft.Text(
                self.description,
                size=12,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS
            ) if self.description else ft.Container()
        ], spacing=5),
    
    def build_action_section(self) -> ft.Row:
        """构建操作按钮区域"""
        return ft.Row([
            # 下载按钮
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon("download", size=16),
                    ft.Text("下载", weight=ft.FontWeight.BOLD)
                ]),
                on_click=self.handle_download,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=6)
                )
            ),
            
            # 详情按钮
            ft.OutlinedButton(
                content=ft.Row([
                    ft.Icon("info", size=16),
                    ft.Text("详情")
                ]),
                on_click=self.handle_details,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=6)
                )
            ),
            
            ft.Container(height=10),
            
            # 更多选项
            ft.IconButton(
                icon="more_vert",
                on_click=self.handle_more_options,
                icon_size=20,
            )
        ])
    
    async def handle_download(self, e):
        """处理下载按钮点击"""
        if self.on_download:
            await self.on_download(self.video_info)
    
    async def handle_details(self, e):
        """处理详情按钮点击"""
        # 这里可以显示详细信息对话框
        print("显示视频详情")
    
    async def handle_more_options(self, e):
        """处理更多选项按钮点击"""
        # 这里可以显示更多选项菜单
        print("显示更多选项")
    
    def format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if not seconds or seconds <= 0:
            return ""
        
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def format_view_count(self, count: int) -> str:
        """格式化播放量"""
        if not count or count <= 0:
            return "未知"
        
        if count >= 100000000:  # 1亿
            return f"{count/100000000:.1f}亿"
        elif count >= 10000:  # 1万
            return f"{count/10000:.1f}万"
        else:
            return f"{count:,}"
    
    def update_video_info(self, new_video_info: Dict[str, Any]):
        """更新视频信息"""
        self.video_info = new_video_info,
        self.title = new_video_info.get('title', '未知标题')
        self.duration = new_video_info.get('duration', 0)
        self.uploader = new_video_info.get('uploader', '未知UP主')
        self.view_count = new_video_info.get('view_count', 0)
        self.thumbnail = new_video_info.get('thumbnail', '')
        self.description = new_video_info.get('description', '')
        
        # 重新构建卡片内容
        self.content = self.build_card()
        
        if self.page:
            self.update()


class CompactVideoCard(VideoCard):
    """紧凑版视频卡片"""
    
    def __init__(self, video_info: Dict[str, Any], on_download=None):
        super().__init__(video_info, on_download)
        
        # 调整尺寸
        self.width = 200,
        self.padding = ft.padding.all(10)
    
    def build_card(self) -> ft.Column:
        """构建紧凑版卡片内容"""
        return ft.Column([
            # 缩略图（较小）
            self.build_compact_thumbnail(),
            
            # 基本信息
            self.build_compact_info(),
            
            # 简化操作按钮
            self.build_compact_actions()
        ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=8),
    
    def build_compact_thumbnail(self) -> ft.Container:
        """构建紧凑版缩略图"""
        if self.thumbnail:
            thumbnail_widget = ft.Image(
                src=self.thumbnail,
                width=180,
                height=100,
                fit=ft.ImageFit.COVER,
                border_radius=6,
            )
        else:
            thumbnail_widget = ft.Container(
                content=ft.Icon(
                    "video_library",
                    size=32,
                ),
                width=180,
                height=100,
                border_radius=6,
            )
        
        return ft.Container(
            content=ft.Stack([
                thumbnail_widget,
                ft.Container(
                    content=ft.Text(
                        self.format_duration(self.duration),
                        size=10,
                        weight=ft.FontWeight.BOLD
                    ),
                    padding=ft.padding.symmetric(horizontal=4, vertical=1),
                    border_radius=2,
                    margin=ft.margin.only(right=5, bottom=5),
                    visible=self.duration > 0
                )
            ])
        )
    
    def build_compact_info(self) -> ft.Column:
        """构建紧凑版信息"""
        return ft.Column([
            ft.Text(
                self.title,
                size=12,
                weight=ft.FontWeight.BOLD,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            ft.Text(
                self.uploader,
                size=10,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS
            )
        ], spacing=2),
    
    def build_compact_actions(self) -> ft.Row:
        """构建紧凑版操作按钮"""
        return ft.Row([
            ft.IconButton(
                icon="download",
                icon_size=20,
                on_click=self.handle_download,
                icon_color=ft.Colors.WHITE
            ),
            ft.Container(height=10)
        ])