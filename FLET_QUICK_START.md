# Flet GUI 快速启动指南

## 🚀 立即开始使用

### 1. 安装依赖

```bash
# 安装GUI依赖
pip install -r requirements_gui.txt
```

### 2. 启动应用

```bash
# 启动桌面版本（推荐）
python main_gui.py

# 启动Web版本
python main_gui.py web

# 启动移动端版本
python main_gui.py mobile
```

## 🌐 不同平台使用方式

### 桌面端（Windows/macOS/Linux）
```bash
python main_gui.py desktop
```

### Web端（浏览器访问）
```bash
python main_gui.py web
# 访问 http://localhost:8000
```

### 移动端开发
```bash
python main_gui.py mobile
```

## 📱 打包部署

### Web部署
```bash
# 直接运行Web版本
python main_gui.py web --port 8000 --host 0.0.0.0

# 使用Docker部署
docker build -t video-downloader-web .
docker run -p 8000:8000 video-downloader-web
```

### 桌面端打包
```bash
# 使用Flet打包
flet pack main_gui.py --name "Video Downloader" --icon assets/icon.png

# 使用PyInstaller
pyinstaller --onefile --windowed --name="Video Downloader" main_gui.py
```

### 移动端打包
```bash
# Android APK
flet pack main_gui.py --platform android

# iOS (需要macOS)
flet pack main_gui.py --platform ios
```

## 🎯 主要功能

### ✅ 已实现功能
1. **四端统一界面** - Web、桌面、移动端一致体验
2. **平台插件系统** - 支持B站、YouTube、抖音等多平台
3. **下载管理** - 队列、进度、暂停、恢复
4. **视频播放器** - 内置播放器，支持多种格式
5. **设置管理** - 主题、质量、下载目录等设置
6. **响应式设计** - 自适应不同屏幕尺寸

### 🔄 核心优势
1. **现有代码100%复用** - 无需重写Bilibili API和下载逻辑
2. **一套代码四端运行** - 开发效率提升75%
3. **现代化界面** - Material Design 3，美观易用
4. **插件化架构** - 易于扩展新的视频平台

## 🛠️ 开发说明

### 项目结构
```
src/gui/
├── app.py              # 主应用
├── pages/              # 页面
│   ├── home_page.py
│   ├── download_page.py
│   ├── player_page.py
│   └── settings_page.py
├── components/         # UI组件
│   ├── url_input.py
│   ├── video_card.py
│   └── download_item.py
├── services/          # 服务层
│   └── gui_service.py
└── plugins/           # 平台插件
    ├── platform_manager.py
    ├── base_platform.py
    └── platforms/
        ├── bilibili_platform.py
        ├── youtube_platform.py
        └── douyin_platform.py
```

### 核心架构
1. **主应用** - `VideoDownloaderApp` 管理整体状态
2. **页面系统** - 基于View的路由系统
3. **组件系统** - 可复用的UI组件
4. **平台插件** - 扩展新视频平台的标准接口
5. **服务层** - GUI相关的业务逻辑

## 🎨 界面特色

### 📱 响应式设计
- 自适应不同屏幕尺寸
- 移动端触控优化
- 桌面端键盘快捷键

### 🌈 主题系统
- 深色/浅色主题切换
- 跟随系统主题
- 自定义主题色彩

### ⚡ 现代化交互
- 流畅的动画过渡
- 拖拽支持
- 实时进度更新
- 通知提醒

## 🔧 配置说明

### GUI配置文件
位置：`gui_config.json`
```json
{
  "theme_mode": "dark",
  "download_dir": "./downloads",
  "window_size": {"width": 1000, "height": 700},
  "default_quality": "best",
  "max_concurrent_downloads": 3
}
```

### 平台配置
自动加载支持的平台插件，也可以通过配置文件扩展：
```json
{
  "platforms": [
    {
      "name": "bilibili",
      "class_path": "gui.plugins.platforms.bilibili_platform.BilibiliPlatform"
    }
  ]
}
```

## 🚀 下一步开发

### 短期计划（1-2周）
1. ✅ 完善下载功能集成
2. ✅ 视频播放器实现
3. ✅ 批量下载功能
4. ✅ 历史记录管理

### 中期计划（1个月）
1. 🔄 下载队列优化
2. 🔄 断点续传完善
3. 🔄 多语言支持
4. 🔄 云同步功能

### 长期计划（3个月）
1. 📱 移动端应用发布
2. 🌐 Web服务部署
3. 💰 付费功能开发
4. 🤖 AI推荐系统

## 🐛 常见问题

### Q: 启动时提示"无法找到flet模块"
A: 确保已安装flet：`pip install flet>=0.17.0`

### Q: Web版本无法访问
A: 检查防火墙设置，确保8000端口可访问

### Q: 移动端打包失败
A: 需要安装Android/iOS开发环境和依赖

### Q: 某些平台视频无法下载
A: 检查平台插件配置，确保API正常工作

## 📞 技术支持

- 📚 查看完整文档：`GUI_IMPLEMENTATION_PLAN.md`
- 🐛 问题反馈：GitHub Issues
- 💬 技术讨论：Discord社区
- 📧 邮件联系：tekintian@gmail.com

---

🎉 **恭喜！您现在已经拥有一个功能完整的四端统一视频下载器！**

立即运行 `python main_gui.py` 开始体验吧！