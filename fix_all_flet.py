"""全面修复Flet问题的脚本"""

import os
import re

def fix_file_flet(file_path):
    """修复单个文件中的Flet问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复图标 - 将所有 ft.icons.XXX 转换为字符串
        content = re.sub(r'ft\.icons\.([A-Z_]+)', lambda m: f'"{m.group(1).lower()}"', content)
        
        # 修复字体粗细
        content = re.sub(r'ft\.FontWeight\.MEDIUM', 'ft.FontWeight.NORMAL', content)
        content = re.sub(r'ft\.FontWeight\.BOLD', 'ft.FontWeight.BOLD', content)
        
        # 修复 TextCapitalization
        content = re.sub(r'ft\.TextCapitalization\.NONE', 'None', content)
        
        # 修复颜色 - 使用基本的颜色
        color_replacements = {
            'ft.Colors.WHITE_VARIANT': 'ft.Colors.WHITE',
            'ft.Colors.BLACK_VARIANT': 'ft.Colors.BLACK',
            'ft.Colors.SURFACE_VARIANT': 'ft.Colors.GREY_700',
            'ft.Colors.SURFACE': 'ft.Colors.GREY_800',
            'ft.Colors.PRIMARY': 'ft.Colors.BLUE',
            'ft.Colors.SECONDARY': 'ft.Colors.GREEN',
            'ft.Colors.ERROR': 'ft.Colors.RED',
            'ft.Colors.WARNING': 'ft.Colors.ORANGE',
            'ft.Colors.ON_SURFACE': 'ft.Colors.WHITE',
            'ft.Colors.ON_PRIMARY': 'ft.Colors.WHITE',
            'ft.Colors.INFORMATION': 'ft.Colors.BLUE',
            'ft.Colors.BACKGROUND': 'ft.Colors.WHITE',
        }
        
        for old, new in color_replacements.items():
            content = content.replace(old, new)
        
        # 修复一些常见的图标名称
        icon_replacements = {
            '"video_library_rounded"': '"video_library"',
            '"download_rounded"': '"download"',
            '"play_arrow_rounded"': '"play_arrow"',
            '"settings_rounded"': '"settings"',
            '"home_rounded"': '"home"',
            '"folder_open_rounded"': '"folder_open"',
            '"restore_rounded"': '"restore"',
            '"save_rounded"': '"save"',
            '"check_circle_rounded"': '"check_circle"',
            '"error_rounded"': '"error"',
            '"flash_on_rounded"': '"flash_on"',
            '"hd_rounded"': '"hd"',
            '"pause_rounded"': '"pause"',
            '"stop_rounded"': '"stop"',
            '"volume_up_rounded"': '"volume_up"',
            '"fullscreen_rounded"': '"fullscreen"',
            '"queue_play_next_rounded"': '"queue_play_next"',
            '"video_file_rounded"': '"video_file"',
            '"more_vert_rounded"': '"more_vert"',
            '"stars_rounded"': '"stars"',
            '"storage_rounded"': '"storage"',
            '"analytics_rounded"': '"analytics"',
            '"sports_esports_rounded"': '"sports_esports"',
            '"play_circle_rounded"': '"play_circle"',
            '"music_note_rounded"': '"music_note"',
            '"chat_rounded"': '"chat"',
            '"language_rounded"': '"language"',
            '"person_rounded"': '"person"',
            '"visibility_rounded"': '"visibility"',
            '"info_rounded"': '"info"',
            '"search_rounded"': '"search"',
            '"cloud_upload_rounded"': '"cloud_upload"',
            '"hourglass_empty_rounded"': '"hourglass_empty"',
            '"downloading_rounded"': '"downloading"',
            '"download_off_rounded"': '"download_off"',
            '"delete_sweep_rounded"': '"delete_sweep"',
        }
        
        for old, new in icon_replacements.items():
            content = content.replace(old, new)
        
        # 修复异步方法调用
        content = content.replace('await page.update()', 'page.update()')
        content = content.replace('await self.page.update()', 'self.page.update()')
        content = content.replace('await page.update_async()', 'page.update()')
        content = content.replace('await self.page.update_async()', 'self.page.update()')
        content = content.replace('await self.page_ref.update()', 'self.page_ref.update()')
        content = content.replace('await page_ref.update()', 'page_ref.update()')
        content = content.replace('.update_async()', '.update()')
        
        # 修复 flet.datetime 引用
        content = content.replace('ft.datetime.datetime', 'datetime.datetime')
        content = content.replace('flet.datetime', 'datetime')
        
        # 修复 Spacer 组件
        content = content.replace('ft.Spacer()', 'ft.Container(height=10)')
        
        # 修复 Colors.SUCCESS
        content = content.replace('ft.Colors.SUCCESS', 'ft.Colors.GREEN')
        content = content.replace('ft.colors.SUCCESS', 'ft.Colors.GREEN')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修复: {file_path}")
        else:
            print(f"无需修复: {file_path}")
            
    except Exception as e:
        print(f"修复 {file_path} 时出错: {e}")

def fix_all_flet():
    """修复所有Python文件中的Flet问题"""
    base_dir = "src/gui"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_flet(file_path)

if __name__ == "__main__":
    fix_all_flet()
    print("全面修复完成！")