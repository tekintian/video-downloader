"""主页 - 视频下载器主页界面"""

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
        self.on_url_submit = on_url_submit,
        self.platform_manager = platform_manager,
        self.current_video_info = None
    
    def build(self) -> ft.Column:
        """构建主页UI"""
        return ft.Column(
            controls=[
                # 标题区域
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(
                                "video_library",
                                size=48,
                            ),
                            ft.Text(
                                "视频下载器",
                                size=48,
                                weight=ft.FontWeight.BOLD
                            )
                        ]),
                        
                        ft.Text(
                            "支持B站、YouTube、抖音等主流平台，一键下载高清视频",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.NORMAL
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                    margin=ft.margin.symmetric(vertical=20)
                ),
                
                # URL输入区域
                ft.Container(
                    content=URLInput(
                        on_submit=self.on_url_submit,
                        placeholder="粘贴B站、YouTube或抖音视频链接..."
                    ),
                    margin=ft.margin.only(bottom=30)
                ),
                
                # 支持的平台
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon("language"),
                            ft.Text(
                                "支持的平台",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            )
                        ]),
                        ft.Divider(height=1),
                        self.build_supported_platforms()
                    ], spacing=10),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # 功能特点
                self.build_features(),
                
                # 统计信息
                self.build_statistics(),
                
                # 底部间距
                ft.Container(height=20)],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
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
                        ),
                        ft.Text(
                            platform.name.capitalize(),
                            size=14,
                            weight=ft.FontWeight.NORMAL
                        ),
                        ft.Text(
                            f"{len(platform.supported_domains)} 域名",
                            size=12,
                            text_align=ft.TextAlign.CENTER
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5),
                    width=120,
                    height=110,
                    border_radius=12,
                    padding=ft.padding.all(10),
                    margin=ft.margin.only(right=10),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=4
                    )
                )
            )
        
        return ft.Row(
            controls=platform_cards,
            scroll=ft.ScrollMode.AUTO,
            wrap=True
        )
    
    def build_features(self) -> ft.Container:
        """构建功能特点展示"""
        features = [
            {
                "icon": "flash_on",
                "title": "快速解析",
                "description": "官方API优先，解析速度快",
                "color": ft.Colors.ORANGE
            },
            {
                "icon": "hd",
                "title": "高清下载",
                "description": "支持4K、HDR等高清格式",
                "color": ft.Colors.BLUE
            },
            {
                "icon": "pause",
                "title": "断点续传",
                "description": "下载失败可继续续传",
                "color": ft.Colors.GREEN
            },
            {
                "icon": "play_arrow",
                "title": "内置播放",
                "description": "下载后可直接播放",
                "color": ft.Colors.PURPLE
            }
        ]
        
        feature_cards = []
        for feature in features:
            feature_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            feature["icon"],
                            size=32,
                        ),
                        ft.Text(
                            feature["title"],
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            feature["description"],
                            size=12,
                            text_align=ft.TextAlign.CENTER
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8),
                    width=140,
                    height=140,
                    border_radius=12,
                    padding=ft.padding.all(15),
                    margin=ft.margin.only(right=10)
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon("stars"),
                    ft.Text(
                        "核心功能",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    )
                ]),
                ft.Divider(height=1),
                ft.Row(
                    controls=feature_cards,
                    wrap=True
                )
            ], spacing=10),
            margin=ft.margin.only(bottom=20)
        )
    
    def build_statistics(self) -> ft.Container:
        """构建统计信息"""
        stats = [
            {"label": "总下载", "value": "0", "icon": "download"},
            {"label": "成功", "value": "0", "icon": "check_circle"},
            {"label": "失败", "value": "0", "icon": "error"},
            {"label": "总大小", "value": "0 MB", "icon": "storage"}
        ]
        
        stat_containers = []
        for stat in stats:
            stat_containers.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(
                                stat["icon"],
                                size=20,
                            ),
                            ft.Text(
                                stat["label"],
                                size=14,
                            )
                        ]),
                        ft.Text(
                            stat["value"],
                            size=24,
                            weight=ft.FontWeight.BOLD
                        )
                    ], spacing=5),
                    width=120,
                    border_radius=8,
                    padding=ft.padding.all(12),
                    margin=ft.margin.only(right=10)
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon("analytics"),
                    ft.Text(
                        "使用统计",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    )
                ]),
                ft.Divider(height=1),
                ft.Row(
                    controls=stat_containers
                )
            ], spacing=10),
            margin=ft.margin.only(bottom=20)
        )
    
    def get_platform_icon(self, platform_name: str) -> str:
        """获取平台图标"""
        icons = {
            'bilibili': "sports_esports",
            'youtube': "play_circle",
            'douyin': "music_note",
            'weibo': "chat",
            'default': "language"
        }
        return icons.get(platform_name.lower(), icons['default'])