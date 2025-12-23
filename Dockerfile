# Flet Web版本 Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libopus-dev \
    libvpx-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements_gui.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements_gui.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLET_WEB_BROWSER_PORT=8000

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main_gui.py", "web", "--host", "0.0.0.0", "--port", "8000"]