"""简化的Flet GUI测试"""

import flet as ft


def main(page: ft.Page):
    page.title = "视频下载器"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    def download_clicked(e):
        status_text.value = "开始下载..."
        page.update()
    
    # 简单的界面
    url_field = ft.TextField(
        label="视频URL",
        width=400,
        hint_text="请输入视频链接"
    )
    
    download_btn = ft.ElevatedButton(
        "下载",
        on_click=download_clicked,
        icon="download"
    )
    
    status_text = ft.Text("准备就绪", size=16)
    
    page.add(
        ft.Column(
            [
                ft.Text("视频下载器", size=32, weight=ft.FontWeight.BOLD),
                url_field,
                ft.Row([download_btn], alignment=ft.MainAxisAlignment.CENTER),
                status_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )


if __name__ == "__main__":
    ft.app(target=main)