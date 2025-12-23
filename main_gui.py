"""Flet GUI启动入口"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.app import app, run_desktop, run_web, run_mobile

def main():
    """主入口函数"""
    # 根据参数选择不同的启动方式
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'web':
            print("启动Web版本...")
            run_web()
        elif mode == 'mobile':
            print("启动移动端版本...")
            run_mobile()
        elif mode == 'desktop':
            print("启动桌面版本...")
            run_desktop()
        else:
            print(f"未知模式: {mode}")
            print("可用模式: web, desktop, mobile")
    else:
        print("启动默认桌面版本...")
        run_desktop()

if __name__ == "__main__":
    main()