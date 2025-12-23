"""URL输入组件 - 支持拖拽和输入"""

import flet as ft
from typing import Callable


class URLInput(ft.Container):
    """URL输入组件，支持拖拽和输入"""
    
    def __init__(self, on_submit: Callable[[str], None], placeholder: str = ""):
        self.on_submit = on_submit,
        self.placeholder = placeholder,
        self.page_ref = None
        
        # URL输入框
        self.url_field = ft.TextField(
            label="视频链接",
            hint_text=placeholder,
            value="",
            width=400,
            height=50,
            border_radius=8,
            filled=True,
            capitalization=None,
            keyboard_type=ft.KeyboardType.URL,
            on_submit=self.handle_submit
        )
        
        # 解析按钮
        self.submit_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon("search"),
                ft.Text("解析", weight=ft.FontWeight.BOLD)
            ]),
            on_click=self.handle_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=2
            ),
            height=50,
        )
        
        # 拖拽区域
        self.drag_target = ft.DragTarget(
            group="url",
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(
                        "cloud_upload",
                        size=48,
                    ),
                    ft.Text(
                        "拖拽视频链接到这里",
                        size=16,
                        weight=ft.FontWeight.NORMAL
                    ),
                    ft.Text(
                        "支持B站、YouTube、抖音等平台",
                        size=12,
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8),
                width=500,
                height=120,
                border=ft.border.all(2, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                alignment=ft.alignment.center
            ),
            on_accept=self.handle_drag_accept,
            on_will_accept=self.handle_drag_will_accept
        )
        
        # 快捷链接按钮
        self.quick_links = self.build_quick_links()
        
        super().__init__(
            content=ft.Column([
                # 主输入区域
                ft.Column([
                    ft.Row([
                        self.url_field,
                        self.submit_button
                    ]),
                    
                    # 分隔线
                    ft.Divider(height=20),
                    
                    # 拖拽区域
                    self.drag_target,
                    
                    # 快捷链接
                    ft.Container(
                        content=self.quick_links,
                        margin=ft.margin.only(top=15)
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(25),
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                offset=ft.Offset(0, 2)
            )
        )
    
    def build_quick_links(self) -> ft.Row:
        """构建快捷链接"""
        platforms = [
            {"name": "Bilibili", "icon": "sports_esports", "example": "BV123456789"},
            {"name": "YouTube", "icon": "play_circle", "example": "dQw4w9WgXcQ"},
            {"name": "抖音", "icon": "music_note", "example": "7351234567890"}]
        
        link_buttons = []
        for platform in platforms:
            link_buttons.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            platform["icon"],
                            size=24,
                        ),
                        ft.Text(
                            platform["name"],
                            size=12,
                            weight=ft.FontWeight.NORMAL
                        )
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4),
                    width=70,
                    height=60,
                    border_radius=8,
                    margin=ft.margin.only(right=10),
                    on_click=lambda e, p=platform["example"]: self._handle_example_click(p)
                )
            )
        
        return ft.Column([
            ft.Text(
                "快捷测试链接：",
                size=14,
                weight=ft.FontWeight.NORMAL
            ),
            ft.Row(link_buttons, wrap=True)
        ], spacing=8),
    
    def _handle_example_click(self, example: str):
        """处理示例链接点击（同步方法）"""
        if example == "BV123456789":
            self.url_field.value = "https://www.bilibili.com/video/BV1GJ411x7h7",
        elif example == "dQw4w9WgXcQ":
            self.url_field.value = "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        elif example == "7351234567890":
            self.url_field.value = "https://v.douyin.com/ieFwNfGQ/"
        
        if self.page_ref:
            self.page_ref.update()
    
    async def insert_example(self, example: str):
        """插入示例链接"""
        if example == "BV123456789":
            self.url_field.value = "https://www.bilibili.com/video/BV1GJ411x7h7",
        elif example == "dQw4w9WgXcQ":
            self.url_field.value = "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        elif example == "7351234567890":
            self.url_field.value = "https://v.douyin.com/ieFwNfGQ/"
        
        self.page_ref.update()
    
    async def handle_submit(self, e):
        """处理输入提交"""
        await self.process_url(self.url_field.value)
    
    async def handle_click(self, e):
        """处理按钮点击"""
        await self.process_url(self.url_field.value)
    
    async def handle_drag_accept(self, e: ft.DragTargetEvent):
        """处理拖拽接受"""
        url = e.data if isinstance(e.data, str) else str(e.data)
        self.url_field.value = url
        await self.process_url(url)
    
    async def handle_drag_will_accept(self, e: ft.DragTargetEvent):
        """处理拖拽进入"""
        # 改变拖拽区域样式
        e.control.content.border = ft.border.all(2, ft.Colors.BLUE)
        e.control.content.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.BLUE)
        await e.control.update()
    
    async def process_url(self, url: str):
        """处理URL"""
        if not url or not url.strip():
            self.url_field.error_text = "请输入视频链接"
            self.url_field.focus()
            self.page_ref.update()
            return
        
        # 基本URL验证
        if not url.startswith(('http://', 'https://')):
            self.url_field.error_text = "请输入有效的URL（必须以http://或https://开头）"
            self.url_field.focus()
            self.page_ref.update()
            return
        
        # 检查是否为支持的域名（简单检查）
        supported_domains = ['bilibili.com', 'b23.tv', 'youtube.com', 'youtu.be', 'douyin.com', 'v.douyin.com']
        if not any(domain in url.lower() for domain in supported_domains):
            self.url_field.error_text = "暂不支持该平台，请检查链接"
            self.url_field.focus()
            self.page_ref.update()
            return
        
        # 清除错误提示
        self.url_field.error_text = None
        self.page_ref.update()
        
        # 显示加载状态
        self.show_loading_state()
        self.page_ref.update()
        
        # 调用回调函数
        try:
            await self.on_submit(url.strip())
        except Exception as e:
            await self.show_error(f"处理失败: {str(e)}")
        finally:
            self.hide_loading_state()
            self.page_ref.update()
    
    def show_loading_state(self):
        """显示加载状态"""
        self.submit_button.disabled = True,
        self.submit_button.content = ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text("解析中...", weight=ft.FontWeight.BOLD)
        ])
        
        self.drag_target.content.border = ft.border.all(2, ft.Colors.BLUE)
        self.drag_target.content.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.BLUE)
    
    def hide_loading_state(self):
        """隐藏加载状态"""
        self.submit_button.disabled = False,
        self.submit_button.content = ft.Row([
            ft.Icon("search"),
            ft.Text("解析", weight=ft.FontWeight.BOLD)
        ])
        
        self.drag_target.content.border = ft.border.all(2, ft.Colors.OUTLINE_VARIANT)
        self.drag_target.content.bgcolor = ft.Colors.GREY_700
    
    async def show_error(self, message: str):
        """显示错误消息"""
        if self.page_ref:
            snack_bar = ft.SnackBar(
                content=ft.Text(message)
            )
            self.page_ref.snack_bar = snack_bar,
            snack_bar.open = True
            self.page_ref.update()
    
    async def show_success(self, message: str):
        """显示成功消息"""
        if self.page_ref:
            snack_bar = ft.SnackBar(
                content=ft.Text(message)
            )
            self.page_ref.snack_bar = snack_bar,
            snack_bar.open = True
            self.page_ref.update()
    
    def did_mount(self):
        """组件挂载时调用"""
        self.page_ref = self.page
    
    def will_unmount(self):
        """组件卸载时调用"""
        self.page_ref = None