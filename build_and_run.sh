#!/bin/bash

# Flet GUI 构建和运行脚本

set -e

echo "🚀 Video Downloader - Flet GUI 构建脚本"
echo "======================================"

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python 3.8+，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 安装依赖
echo "📦 安装GUI依赖..."
pip install -r requirements_gui.txt

# 构建选项
case "$1" in
    "desktop")
        echo "🖥️ 启动桌面版本..."
        python main_gui.py desktop
        ;;
    "web")
        echo "🌐 启动Web版本..."
        if [ -z "$2" ]; then
            PORT=8000
        else
            PORT=$2
        fi
        echo "📍 Web版本将在 http://localhost:$PORT 启动"
        python main_gui.py web --port $PORT --host 0.0.0.0
        ;;
    "mobile")
        echo "📱 启动移动端版本..."
        python main_gui.py mobile
        ;;
    "build")
        echo "🔨 构建桌面应用..."
        if command -v flet &> /dev/null; then
            flet pack main_gui.py --name "Video Downloader" --icon assets/icon.png
        else
            echo "❌ 错误: 未找到flet命令，请安装: pip install flet-pack"
            exit 1
        fi
        ;;
    "docker")
        echo "🐳 构建Docker镜像..."
        docker build -t video-downloader-web .
        echo "🚀 运行Docker容器..."
        docker run -p 8000:8000 video-downloader-web
        ;;
    "test")
        echo "🧪 运行测试..."
        python -m pytest tests/ -v
        ;;
    *)
        echo "使用方法:"
        echo "  ./build_and_run.sh [命令]"
        echo ""
        echo "命令:"
        echo "  desktop   - 启动桌面版本（默认）"
        echo "  web       - 启动Web版本"
        echo "  mobile    - 启动移动端版本"
        echo "  build     - 构建桌面应用"
        echo "  docker    - 构建并运行Docker镜像"
        echo "  test      - 运行测试"
        echo ""
        echo "示例:"
        echo "  ./build_and_run.sh desktop"
        echo "  ./build_and_run.sh web 8080"
        echo "  ./build_and_run.sh build"
        echo "  ./build_and_run.sh docker"
        exit 1
        ;;
esac