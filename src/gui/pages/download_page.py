"""下载页面 - 下载管理界面"""

import flet as ft
from typing import Callable, Dict, Any, List
import datetime

from ..components.download_item import DownloadItem
from ..services.gui_service import GUIService


class DownloadPage:
    """下载页面"""
    
    def __init__(self, 
                 gui_service: GUIService,
                 downloads: List[Dict[str, Any]]):
        self.gui_service = gui_service
        self.downloads = downloads
        self.selected_items = set()
        
    def build(self) -> ft.Column:
        """构建下载页面UI"""
        return ft.Column(
            controls=[
                # 页面标题
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            "download",
                            size=32,
                            color=ft.Colors.BLUE
                        ),
                        ft.Text(
                            "下载管理",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        ft.Container(height=10),
                        # 操作按钮
                        ft.Row([
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon("play_arrow"),
                                    ft.Text("全部开始")
                                ]),
                                on_click=self.start_all_downloads,
                                bgcolor=ft.Colors.GREEN
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon("pause"),
                                    ft.Text("全部暂停")
                                ]),
                                on_click=self.pause_all_downloads,
                                bgcolor=ft.Colors.ORANGE
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon("delete_rounded"),
                                    ft.Text("清理完成")
                                ]),
                                on_click=self.clear_completed,
                                bgcolor=ft.Colors.RED
                            )
                        ])
                    ]),
                    padding=ft.padding.symmetric(vertical=10),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # 统计信息
                self.build_download_stats(),
                
                # 下载列表
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Checkbox(
                                    value=False,
                                    on_change=self.toggle_select_all
                                ),
                                ft.Text(
                                    "全选",
                                    size=14,
                                    weight=ft.FontWeight.NORMAL
                                ),
                                ft.Container(height=10),
                                ft.Text(
                                    f"共 {len(self.downloads)} 个下载",
                                    size=14,
                                    color=ft.Colors.WHITE
                                )
                            ]),
                            ft.Divider(height=1),
                        ] + self.build_download_list()
                    ),
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    padding=ft.padding.all(10),
                    expand=True
                ),
                
                # 底部操作栏
                self.build_bottom_actions()
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )
    
    def build_download_stats(self) -> ft.Container:
        """构建下载统计"""
        stats = self.calculate_stats()
        
        return ft.Container(
            content=ft.Row([
                self.build_stat_item(
                    "等待中", 
                    stats['pending'], 
                    ft.colors.ORANGE,
                    "hourglass_empty"
                ),
                self.build_stat_item(
                    "下载中", 
                    stats['downloading'], 
                    ft.colors.BLUE,
                    "downloading"
                ),
                self.build_stat_item(
                    "已完成", 
                    stats['completed'], 
                    ft.colors.GREEN,
                    "check_circle"
                ),
                self.build_stat_item(
                    "已失败", 
                    stats['failed'], 
                    ft.colors.ERROR,
                    "error"
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            padding=ft.padding.all(15),
            bgcolor=ft.Colors.GREY_700,
            border_radius=8,
            margin=ft.margin.only(bottom=20)
        )
    
    def build_stat_item(self, label: str, value: int, color: str, icon: str) -> ft.Container:
        """构建统计项"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=20, color=color),
                    ft.Text(
                        label,
                        size=14,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Text(
                    str(value),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=color
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),
            width=100,
            height=80,
            alignment=ft.alignment.center
        )
    
    def build_download_list(self) -> List[ft.Control]:
        """构建下载列表"""
        if not self.downloads:
            return [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            "download_off",
                            size=64,
                            color=ft.Colors.WHITE
                        ),
                        ft.Text(
                            "暂无下载任务",
                            size=18,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.NORMAL
                        ),
                        ft.Text(
                            "在主页输入视频链接开始下载",
                            size=14,
                            color=ft.Colors.WHITE
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    height=200,
                    alignment=ft.alignment.center
                )
            ]
        
        download_items = []
        for i, download in enumerate(self.downloads):
            download_item = DownloadItem(
                download=download,
                on_pause=lambda e, d=download: self.pause_download(d),
                on_resume=lambda e, d=download: self.resume_download(d),
                on_cancel=lambda e, d=download: self.cancel_download(d),
                on_retry=lambda e, d=download: self.retry_download(d),
                on_select=lambda e, d=download: self.toggle_select(d)
            )
            download_items.append(download_item.build())
        
        return download_items
    
    def build_bottom_actions(self) -> ft.Container:
        """构建底部操作栏"""
        selected_count = len(self.selected_items)
        
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    f"已选择 {selected_count} 项",
                    size=14,
                    color=ft.Colors.WHITE
                ),
                ft.Container(height=10),
                ft.Row([
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("delete_sweep"),
                            ft.Text("删除选中")
                        ]),
                        on_click=self.delete_selected,
                        disabled=selected_count == 0,
                        bgcolor=ft.Colors.RED
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon("play_arrow"),
                            ft.Text("开始选中")
                        ]),
                        on_click=self.start_selected,
                        disabled=selected_count == 0,
                        bgcolor=ft.Colors.GREEN
                    )
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(15),
            bgcolor=ft.Colors.GREY_700,
            border_radius=8,
            margin=ft.margin.only(top=20)
        )
    
    def calculate_stats(self) -> Dict[str, int]:
        """计算下载统计"""
        stats = {
            'pending': 0,
            'downloading': 0,
            'completed': 0,
            'failed': 0
        }
        
        for download in self.downloads:
            status = download.get('status', 'pending')
            stats[status] = stats.get(status, 0) + 1
        
        return stats
    
    async def toggle_select_all(self, e):
        """切换全选"""
        select_all = e.control.value
        self.selected_items.clear()
        
        if select_all:
            for download in self.downloads:
                if download.get('status') != 'completed':
                    self.selected_items.add(download['id'])
        
        # 更新UI
        self.page.update()
    
    def toggle_select(self, download: Dict[str, Any]):
        """切换单项选择"""
        download_id = download['id']
        if download_id in self.selected_items:
            self.selected_items.remove(download_id)
        else:
            self.selected_items.add(download_id)
    
    async def start_all_downloads(self, e):
        """开始所有下载"""
        for download in self.downloads:
            if download['status'] in ['pending', 'paused', 'failed']:
                download['status'] = 'downloading'
        self.page.update()
    
    async def pause_all_downloads(self, e):
        """暂停所有下载"""
        for download in self.downloads:
            if download['status'] == 'downloading':
                download['status'] = 'paused'
        self.page.update()
    
    async def clear_completed(self, e):
        """清理已完成的下载"""
        self.downloads = [
            d for d in self.downloads 
            if d.get('status') != 'completed'
        ]
        self.page.update()
    
    async def pause_download(self, download: Dict[str, Any]):
        """暂停单个下载"""
        download['status'] = 'paused'
        self.page.update()
    
    async def resume_download(self, download: Dict[str, Any]):
        """恢复单个下载"""
        download['status'] = 'downloading'
        self.page.update()
    
    async def cancel_download(self, download: Dict[str, Any]):
        """取消下载"""
        self.downloads.remove(download)
        self.page.update()
    
    async def retry_download(self, download: Dict[str, Any]):
        """重试下载"""
        download['status'] = 'pending'
        download['progress'] = 0
        download['error'] = None
        self.page.update()
    
    async def delete_selected(self, e):
        """删除选中项"""
        selected_ids = list(self.selected_items)
        for download_id in selected_ids:
            self.downloads = [
                d for d in self.downloads 
                if d['id'] != download_id
            ]
        self.selected_items.clear()
        self.page.update()
    
    async def start_selected(self, e):
        """开始选中项"""
        for download in self.downloads:
            if download['id'] in self.selected_items:
                download['status'] = 'downloading'
        self.page.update()
    
    @property
    def page(self):
        """获取页面引用"""
        # 这里需要从外部传入页面引用
        # 为了简化，暂时返回None，实际使用时需要调整
        return None