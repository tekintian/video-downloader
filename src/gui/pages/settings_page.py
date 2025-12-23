"""设置页面 - 应用设置界面"""

import flet as ft
from typing import Dict, Any

from ..services.gui_service import GUIService


class SettingsPage:
    """设置页面"""
    
    def __init__(self, gui_service: GUIService):
        self.gui_service = gui_service
        
        # 设置项默认值
        self.settings = {
            'download_dir': './downloads',
            'max_threads': 4,
            'chunk_size': 1024 * 1024,  # 1MB
            'timeout': 30,
            'retry_times': 3,
            'video_quality': 'best',
            'audio_only': False,
            'subtitle': True,
            'api_priority': 'official',  # 'official' or 'ytdlp'
            'theme_mode': 'dark',
            'auto_check_update': True,
            'enable_notifications': True
        }
    
    def build(self) -> ft.Column:
        """构建设置页面UI"""
        return ft.Column(
            controls=[
                # 页面标题
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            "settings",
                            size=32,
                            color=ft.Colors.BLUE
                        ),
                        ft.Text(
                            "应用设置",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ]),
                    padding=ft.padding.symmetric(vertical=10),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # 设置分组
                ft.Column([
                    self.build_download_settings(),
                    self.build_quality_settings(),
                    self.build_api_settings(),
                    self.build_appearance_settings(),
                    self.build_advanced_settings(),
                    
                    # 操作按钮
                    ft.Container(
                        content=ft.Row([
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon("restore"),
                                    ft.Text("重置默认")
                                ]),
                                on_click=self.reset_settings,
                                bgcolor=ft.Colors.OUTLINE_VARIANT
                            ),
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon("save"),
                                    ft.Text("保存设置")
                                ]),
                                on_click=self.save_settings,
                                bgcolor=ft.Colors.BLUE
                            )
                        ]),
                        margin=ft.margin.only(top=20)
                    )
                ])
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20
        )
    
    def build_download_settings(self) -> ft.Container:
        """构建下载设置"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon("download", color=ft.Colors.BLUE),
                    ft.Text(
                        "下载设置",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Divider(height=1),
                
                # 下载目录
                ft.Row([
                    ft.Text("下载目录：", width=120),
                    ft.TextField(
                        value=self.settings['download_dir'],
                        width=300,
                        border_radius=8
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("folder_open", size=16),
                            ft.Text("浏览")
                        ]),
                        on_click=self.browse_download_dir
                    )
                ]),
                
                # 最大线程数
                ft.Row([
                    ft.Text("最大线程数：", width=120),
                    ft.Slider(
                        value=self.settings['max_threads'],
                        min=1,
                        max=16,
                        divisions=15,
                        width=300,
                        label=f"{self.settings['max_threads']} 线程"
                    )
                ]),
                
                # 超时设置
                ft.Row([
                    ft.Text("下载超时：", width=120),
                    ft.TextField(
                        value=str(self.settings['timeout']),
                        width=100,
                        text_align=ft.TextAlign.RIGHT
                    ),
                    ft.Text("秒", color=ft.Colors.WHITE)
                ]),
                
                # 重试次数
                ft.Row([
                    ft.Text("重试次数：", width=120),
                    ft.Slider(
                        value=self.settings['retry_times'],
                        min=0,
                        max=10,
                        divisions=10,
                        width=300,
                        label=f"{self.settings['retry_times']} 次"
                    )
                ])
            ], spacing=15),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_700,
            border_radius=12
        )
    
    def build_quality_settings(self) -> ft.Container:
        """构建质量设置"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft-icons.HD_ROUNDED, color=ft.Colors.BLUE),
                    ft.Text(
                        "视频质量",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Divider(height=1),
                
                # 视频质量选择
                ft.Row([
                    ft.Text("默认质量：", width=120),
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("best", "最佳质量"),
                            ft.dropdown.Option("1080p", "1080P"),
                            ft.dropdown.Option("720p", "720P"),
                            ft.dropdown.Option("480p", "480P"),
                            ft.dropdown.Option("360p", "360P")
                        ],
                        value=self.settings['video_quality'],
                        width=200,
                        border_radius=8
                    )
                ]),
                
                # 音频设置
                ft.Row([
                    ft.Text("仅下载音频：", width=120),
                    ft.Checkbox(
                        value=self.settings['audio_only'],
                        label="启用",
                        on_change=self.toggle_audio_only
                    )
                ]),
                
                # 字幕设置
                ft.Row([
                    ft.Text("下载字幕：", width=120),
                    ft.Checkbox(
                        value=self.settings['subtitle'],
                        label="启用",
                        on_change=self.toggle_subtitle
                    )
                ])
            ], spacing=15),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_700,
            border_radius=12
        )
    
    def build_api_settings(self) -> ft.Container:
        """构建API设置"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft-icons.API_ROUNDED, color=ft.Colors.BLUE),
                    ft.Text(
                        "API设置",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Divider(height=1),
                
                # API优先级
                ft.Row([
                    ft.Text("API优先级：", width=120),
                    ft.RadioGroup(
                        value=self.settings['api_priority'],
                        content=ft.Column([
                            ft.Radio(
                                value="official",
                                label="官方API (推荐)",
                                label_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                            ),
                            ft.Radio(
                                value="ytdlp",
                                label="yt-dlp (备用)"
                            )
                        ]),
                        on_change=self.change_api_priority
                    )
                ]),
                
                ft.Text(
                    "官方API解析速度快但可能受限，yt-dlp兼容性好但速度较慢",
                    size=12,
                    color=ft.Colors.WHITE,
                    italic=True
                )
            ], spacing=15),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_700,
            border_radius=12
        )
    
    def build_appearance_settings(self) -> ft.Container:
        """构建外观设置"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft-icons.PALETTE_ROUNDED, color=ft.Colors.BLUE),
                    ft.Text(
                        "外观设置",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Divider(height=1),
                
                # 主题模式
                ft.Row([
                    ft.Text("主题模式：", width=120),
                    ft.RadioGroup(
                        value=self.settings['theme_mode'],
                        content=ft.Column([
                            ft.Radio(
                                value="light",
                                label="浅色主题",
                                label_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
                            ),
                            ft.Radio(
                                value="dark",
                                label="深色主题"
                            ),
                            ft.Radio(
                                value="system",
                                label="跟随系统"
                            )
                        ]),
                        on_change=self.change_theme_mode
                    )
                ])
            ], spacing=15),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_700,
            border_radius=12
        )
    
    def build_advanced_settings(self) -> ft.Container:
        """构建高级设置"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft-icons.TUNING_ROUNDED, color=ft.Colors.BLUE),
                    ft.Text(
                        "高级设置",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Divider(height=1),
                
                # 自动检查更新
                ft.Row([
                    ft.Text("自动检查更新：", width=150),
                    ft.Checkbox(
                        value=self.settings['auto_check_update'],
                        label="启用",
                        on_change=self.toggle_auto_update
                    )
                ]),
                
                # 启用通知
                ft.Row([
                    ft.Text("桌面通知：", width=150),
                    ft.Checkbox(
                        value=self.settings['enable_notifications'],
                        label="启用",
                        on_change=self.toggle_notifications
                    )
                ])
            ], spacing=15),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_700,
            border_radius=12
        )
    
    async def browse_download_dir(self, e):
        """浏览下载目录"""
        # 实际实现需要调用文件选择器
        print("浏览下载目录")
    
    async def toggle_audio_only(self, e):
        """切换仅音频模式"""
        self.settings['audio_only'] = e.control.value
    
    async def toggle_subtitle(self, e):
        """切换字幕下载"""
        self.settings['subtitle'] = e.control.value
    
    async def change_api_priority(self, e):
        """更改API优先级"""
        self.settings['api_priority'] = e.control.value
    
    async def change_theme_mode(self, e):
        """更改主题模式"""
        self.settings['theme_mode'] = e.control.value
        
        # 实时应用主题
        if e.control.page:
            if e.control.value == "light":
                e.control.page.theme_mode = ft.ThemeMode.LIGHT
            elif e.control.value == "dark":
                e.control.page.theme_mode = ft.ThemeMode.DARK
            else:
                e.control.page.theme_mode = ft.ThemeMode.SYSTEM
            
            await e.control.page.update()
    
    async def toggle_auto_update(self, e):
        """切换自动更新"""
        self.settings['auto_check_update'] = e.control.value
    
    async def toggle_notifications(self, e):
        """切换通知"""
        self.settings['enable_notifications'] = e.control.value
    
    async def reset_settings(self, e):
        """重置设置"""
        # 恢复默认值
        self.settings = {
            'download_dir': './downloads',
            'max_threads': 4,
            'chunk_size': 1024 * 1024,
            'timeout': 30,
            'retry_times': 3,
            'video_quality': 'best',
            'audio_only': False,
            'subtitle': True,
            'api_priority': 'official',
            'theme_mode': 'dark',
            'auto_check_update': True,
            'enable_notifications': True
        }
        
        # 重新构建页面
        if e.control.page:
            await self.show_message("设置已重置为默认值", e.control.page)
    
    async def save_settings(self, e):
        """保存设置"""
        try:
            # 这里会调用实际的设置保存逻辑
            # 暂时模拟保存过程
            await self.show_message("设置已保存", e.control.page)
        except Exception as error:
            await self.show_message(f"保存失败: {str(error)}", e.control.page, error=True)
    
    async def show_message(self, message: str, page: ft.Page, error: bool = False):
        """显示消息"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED if error else ft.Colors.GREEN
        )
        page.snack_bar = snack_bar
        snack_bar.open = True
        page.update()