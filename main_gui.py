"""Flet GUI启动入口"""

import sys
import os
import datetime as _datetime

# 在打包成可执行文件时，PyInstaller 会把文件解压到临时目录 sys._MEIPASS
# 在运行时优先尝试从解包目录查找 `src`，否则使用源码目录下的 `src`。
if getattr(sys, 'frozen', False):
    _base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
else:
    _base_dir = os.path.dirname(__file__)

_src_path = os.path.join(_base_dir, 'src')
if os.path.isdir(_src_path) and _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from gui.app import app, run_desktop, run_web, run_mobile

def main():
    """主入口函数"""
    # 根据参数选择不同的启动方式
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'web':
            print("启动Web版本...")
            # 记录模式并尝试运行
            from pathlib import Path
            Path('flet-run.log').write_text(f"main: launching web at {_datetime.datetime.now().isoformat()}\n")
            run_web()
        elif mode == 'mobile':
            print("启动移动端版本...")
            from pathlib import Path
            Path('flet-run.log').write_text(f"main: launching mobile at {_datetime.datetime.now().isoformat()}\n")
            run_mobile()
        elif mode == 'desktop':
            print("启动桌面版本...")
            from pathlib import Path
            Path('flet-run.log').write_text(f"main: launching desktop at {_datetime.datetime.now().isoformat()}\n")
            run_desktop()
        else:
            print(f"未知模式: {mode}")
            print("可用模式: web, desktop, mobile")
    else:
        print("启动默认桌面版本...")
        from pathlib import Path
        Path('flet-run.log').write_text(f"main: launching default desktop at {_datetime.datetime.now().isoformat()}\n")
        run_desktop()

if __name__ == "__main__":
    main()