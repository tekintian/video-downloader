"""修复Flet图标引用问题的脚本"""

import os
import re

def fix_file_icons(file_path):
    """修复单个文件中的图标引用"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换 ft.icons.ICON_NAME 为 "icon_name"
        pattern = r'ft\.icons\.([A-Z_]+)'
        content = re.sub(pattern, lambda m: f'"{m.group(1).lower()}"', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修复: {file_path}")
        else:
            print(f"无需修复: {file_path}")
            
    except Exception as e:
        print(f"修复 {file_path} 时出错: {e}")

def fix_all_icons():
    """修复所有Python文件中的图标引用"""
    base_dir = "src/gui"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_icons(file_path)

if __name__ == "__main__":
    fix_all_icons()
    print("图标修复完成！")