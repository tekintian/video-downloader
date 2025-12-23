# GUI实现方案：PyQt6

## 项目架构设计

### 目录结构
```
src/
├── gui/
│   ├── __init__.py
│   ├── main.py              # GUI主入口
│   ├── main_window.py       # 主窗口
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── download_widget.py    # 下载管理组件
│   │   ├── video_info_widget.py # 视频信息显示
│   │   ├── progress_widget.py   # 进度条组件
│   │   └── settings_widget.py   # 设置组件
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── about_dialog.py      # 关于对话框
│   │   └── format_dialog.py     # 格式选择对话框
│   └── resources/
│       ├── icons/           # 图标资源
│       └── styles.qss       # 样式文件
```

### 核心功能设计

#### 1. 主窗口 (MainWindow)
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        # 菜单栏
        # 工具栏
        # 状态栏
        # 中心组件（下载管理器）
```

#### 2. 下载管理组件 (DownloadWidget)
```python
class DownloadWidget(QWidget):
    def __init__(self):
        self.download_queue = []
        self.active_downloads = []
        
    def add_download(self, url: str):
        # 添加到下载队列
        # 自动开始下载
        
    def pause_download(self, download_id: str):
        # 暂停下载
        
    def resume_download(self, download_id: str):
        # 恢复下载
```

#### 3. 视频信息组件 (VideoInfoWidget)
```python
class VideoInfoWidget(QWidget):
    def display_video_info(self, video_info: dict):
        # 显示缩略图
        # 显示基本信息
        # 显示可用格式
        
    def on_format_selected(self, format_id: str):
        # 格式选择处理
```

## 实施步骤

### Phase 1: 基础框架 (1-2周)
1. ✅ 设置PyQt6依赖
2. ✅ 创建基础窗口结构
3. ✅ 集成现有的核心服务
4. ✅ 基本的事件处理

### Phase 2: 核心功能 (2-3周)
1. ✅ URL输入和验证
2. ✅ 视频信息获取和显示
3. ✅ 下载进度展示
4. ✅ 下载队列管理

### Phase 3: 高级功能 (1-2周)
1. ✅ 设置界面
2. ✅ 下载历史记录
3. ✅ 批量下载
4. ✅ 拖拽支持

### Phase 4: 优化和打包 (1周)
1. ✅ 性能优化
2. ✅ 错误处理完善
3. ✅ 多平台打包
4. ✅ 安装程序制作

## 技术实现要点

### 1. 异步操作集成
```python
# 将现有的异步下载逻辑整合到Qt信号槽
class DownloadWorker(QObject):
    progress_updated = pyqtSignal(int)
    download_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def start_download(self, url: str, path: str):
        # 在线程中运行现有的异步下载逻辑
        asyncio.run(self._download_async(url, path))
```

### 2. 配置管理集成
```python
# 复用现有的配置管理
class SettingsWidget(QWidget):
    def load_settings(self):
        # 从config_manager加载配置到GUI
        pass
        
    def save_settings(self):
        # 保存GUI设置到配置文件
        pass
```

### 3. 样式设计
```css
/* modern.qss - 现代化样式 */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #4a4a4a;
}
```

## 依赖添加

### pyproject.toml 更新
```toml
dependencies = [
    # ... 现有依赖
    "PyQt6>=6.5.0",
    "PyQt6-tools>=6.5.0",  # 开发工具
]

[project.optional-dependencies]
gui = [
    "PyQt6>=6.5.0",
    "PyQt6-tools>=6.5.0",
    "pillow>=10.0.0",  # 图像处理
]
```

## 打包方案

### Windows: PyInstaller
```bash
# 安装PyInstaller
pip install pyinstaller

# 打包命令
pyinstaller --windowed --onefile --icon=assets/icon.ico src/gui/main.py
```

### macOS: PyInstaller + create-dmg
```bash
# 打包为.app
pyinstaller --windowed --onefile --icon=assets/icon.icns src/gui/main.py

# 创建DMG安装包
create-dmg "dist/Video Downloader.app"
```

## 预期效果

### 界面特点
- 现代化深色主题
- 响应式布局设计
- 流畅的动画过渡
- 直观的拖拽操作

### 功能特点
- 支持批量下载管理
- 实时下载进度显示
- 智能格式选择
- 完善的错误处理
- 多语言支持预留

## 开发时间估算
- **总开发周期**: 5-8周
- **MVP版本**: 3-4周
- **完整版本**: 6-8周

## 成本效益分析
- ✅ **开发成本**: 中等（Python技能复用）
- ✅ **维护成本**: 低（PyQt生态成熟）
- ✅ **用户体验**: 高（原生外观）
- ✅ **跨平台成本**: 低（一次开发，多平台运行）

## 风险评估
- **技术风险**: 低（PyQt6成熟稳定）
- **性能风险**: 低（性能优异）
- **维护风险**: 低（社区支持好）
- **用户体验风险**: 低（原生外观符合用户预期）