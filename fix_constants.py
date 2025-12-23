"""修复Flet常量引用问题的脚本"""

import os
import re

def fix_file_constants(file_path):
    """修复单个文件中的常量引用"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复 FontWeight
        content = re.sub(r'ft\.FontWeight\.MEDIUM', 'ft.FontWeight.NORMAL', content)
        content = re.sub(r'ft\.FontWeight\.BOLD', 'ft.FontWeight.BOLD', content)
        
        # 修复 Colors
        content = re.sub(r'ft\.Colors\.SURFACE_VARIANT', 'ft.Colors.GREY_700', content)
        content = re.sub(r'ft\.Colors\.SURFACE', 'ft.Colors.GREY_800', content)
        content = re.sub(r'ft\.Colors\.PRIMARY', 'ft.Colors.BLUE', content)
        content = re.sub(r'ft\.Colors\.SECONDARY', 'ft.Colors.GREEN', content)
        content = re.sub(r'ft\.Colors\.ERROR', 'ft.Colors.RED', content)
        content = re.sub(r'ft\.Colors\.WARNING', 'ft.Colors.ORANGE', content)
        content = re.sub(r'ft\.Colors\.ON_SURFACE', 'ft.Colors.WHITE', content)
        content = re.sub(r'ft\.Colors\.ON_PRIMARY', 'ft.Colors.WHITE', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修复: {file_path}")
        else:
            print(f"无需修复: {file_path}")
            
    except Exception as e:
        print(f"修复 {file_path} 时出错: {e}")

def fix_all_constants():
    """修复所有Python文件中的常量引用"""
    base_dir = "src/gui"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_constants(file_path)

if __name__ == "__main__":
    fix_all_constants()
    print("常量修复完成！")