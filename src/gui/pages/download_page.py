"""下载页 - 显示和管理下载任务"""

import flet as ft
from typing import List, Dict, Any, Callable
from datetime import datetime

from ..components.download_item import DownloadItem
from ..services.gui_service import GUIService


class DownloadPage:
    """下载页面"""
    
    def __init__(self, 
                 on_download_complete: Callable,
                 on_download_delete: Callable,
                 gui_service: GUIService):
        self.on_download_complete = on_download_complete,
        self.on_download_delete = on_download_delete,
        self.gui_service = gui_service,
        self.downloads: List[Dict[str, Any]] = []
        self.selected_download: str = None
    
    def build(self) -> ft.Column:
        """构建下载页面UI"""
        return ft.Column([
            # 页面标题
            ft.Container(
                content=ft.Row([
                    ft.Icon("download"),
                    ft.Text("下载管理", size=24, weight=ft.FontWeight.BOLD)
                ]),
                padding=ft.padding.all(20)
            ),
            
            # 统计信息
            self.build_stats_section(),
            
            # 下载列表
            self.build_download_list(),
            
            # 操作按钮
            self.build_action_buttons()], spacing=10, scroll=ft.ScrollMode.AUTO),
    
    def build_stats_section(self) -> ft.Container:
        """构建统计信息区域"""
        stats = self.gui_service.get_download_stats()
        
        return ft.Container(
            content=ft.Column([
                ft.Text("下载统计", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.build_stat_item(
                        "等待中", 
                        stats['pending'], 
                        ft.Colors.ORANGE,
                        "hourglass_empty"
                    ),
                    self.build_stat_item(
                        "下载中", 
                        stats['downloading'], 
                        ft.Colors.BLUE,
                        "downloading"
                    ),
                    self.build_stat_item(
                        "已完成", 
                        stats['completed'], 
                        ft.Colors.GREEN,
                        "check_circle"
                    ),
                    self.build_stat_item(
                        "已失败", 
                        stats['failed'], 
                        ft.Colors.RED,
                        "error"
                    )])], spacing=20),
            padding=ft.padding.all(15)
        )
    
    def build_stat_item(self, label: str, value: int, color: str, icon: str):
        """构建统计项"""
        # 简化的统计项，避免Container color参数问题
        return ft.Row([
            ft.Icon(icon, size=20),
            ft.Column([
                ft.Text(label, size=14),
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD)
            ])
        ])
    
    def build_download_list(self) -> List[ft.Control]:
        """构建下载列表"""
        if not self.downloads:
            return [
                ft.Container(
                    content=ft.Column([
                        ft.Icon("download_off", size=48),
                        ft.Text("暂无下载任务", size=16)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    height=200,
                )
            ]
        
        return [
            ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon("play_arrow"),
                        title=ft.Text(download['title']),
                        subtitle=ft.Text(
                            f"状态: {download.get('status', 'unknown')} | "
                            f"进度: {download.get('progress', 0)}%"
                        ),
                        on_click=lambda e, d=download: self.select_download(d)
                    ),
                    ft.Divider(color=ft.Colors.GREY_600)]),
                margin=ft.margin.symmetric(vertical=5)
            ) for download in self.downloads
        ]
    
    def build_action_buttons(self) -> ft.Container:
        """构建操作按钮区域"""
        return ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "清理完成", 
                    icon="delete_sweep",
                    on_click=self.clear_completed
                ),
                ft.ElevatedButton(
                    "全部开始", 
                    icon="play_arrow",
                    on_click=self.start_all
                ),
                ft.ElevatedButton(
                    "全部暂停", 
                    icon="pause",
                    on_click=self.pause_all
                )]),
            padding=ft.padding.all(15)
        )
    
    def select_download(self, download: Dict[str, Any]):
        """选择下载项"""
        self.selected_download = download['id']
    
    def clear_completed(self, e):
        """清理已完成的下载"""
        completed_downloads = [d for d in self.downloads if d.get('status') == 'completed']
        if completed_downloads:
            for download in completed_downloads:
                self.downloads.remove(download)
                self.on_download_delete(download)
    
    def start_all(self, e):
        """开始所有下载"""
        pending_downloads = [d for d in self.downloads if d.get('status') == 'pending']
        for download in pending_downloads:
            download['status'] = 'downloading'
            # 这里应该调用实际的下载逻辑
            # 暂时模拟
            download['progress'] = 50
    
    def pause_all(self, e):
        """暂停所有下载"""
        downloading_downloads = [d for d in self.downloads if d.get('status') == 'downloading']
        for download in downloading_downloads:
            download['status'] = 'paused'
    
    def refresh_downloads(self):
        """刷新下载列表"""
        self.downloads = self.gui_service.get_downloads()
        # 这里应该更新UI
        if hasattr(self, 'page_ref') and self.page_ref:
            self.page_ref.update()