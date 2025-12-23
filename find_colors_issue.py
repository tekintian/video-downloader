"""查找具体的colors问题"""

import os
import re

def find_colors_issue():
    """查找具体的colors使用问题"""
    base_dir = "src/gui"
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        # 查找 'colors.' (小写)
                        if re.search(r'\.colors\.', line):
                            print(f"{file_path}:{i}: {line.strip()}")
                            
                        # 查找 "colors." (字符串中的小写)
                        if '"colors.' in line:
                            print(f"{file_path}:{i}: {line.strip()}")
                            
                        # 查找 'colors[' (小写)
                        if "colors['" in line:
                            print(f"{file_path}:{i}: {line.strip()}")
                            
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    find_colors_issue()