# Bilibili API Integration Guide

## 概述

本项目已集成B站官方API，实现了优先使用官方API、失败时自动回退到yt-dlp的双重解析机制。

## 新增功能

### 1. 双重解析机制

- **优先使用B站官方API**: 直接调用 `api.bilibili.com` 获取视频信息
- **自动回退yt-dlp**: 当API调用失败时，自动使用yt-dlp作为备用方案
- **智能选择**: 根据可用性和成功率自动选择最佳解析方式

### 2. 支持的URL格式

```python
# 标准视频链接
https://www.bilibili.com/video/BV1GJ411x7h7

# 短链接
https://b23.tv/BV1GJ411x7h7

# 移动端链接
https://m.bilibili.com/video/BV1GJ411x7h7

# 番剧链接
https://www.bilibili.com/bangumi/play/ss12345
```

### 3. API功能增强

#### 视频信息获取
- **基本信息**: 标题、描述、时长、UP主等
- **统计数据**: 播放量、点赞数等
- **格式信息**: 支持DASH格式，分离音视频流

#### 高级格式支持
- **DASH格式**: 支持视频流和音频流分离
- **高质量选项**: 4K、HDR、杜比视界等（根据视频源）
- **编解码器**: H.264 (AVC) 和 H.265 (HEVC)

#### 质量选择
```python
# 最佳质量
best_quality_url = bilibili_service.get_download_url(url, quality='best')

# 特定DASH质量
dash_4k_url = bilibili_service.get_download_url(url, quality='dash-120')

# 最低质量
worst_quality_url = bilibili_service.get_download_url(url, quality='worst')
```

## 使用方法

### 基本使用

```python
from src.services.bilibili import bilibili_service

# 获取视频信息（自动选择API或yt-dlp）
video_info = bilibili_service.get_video_info(url)
print(f"Using: {video_info.get('api_source')}")  # 'official' 或 'ytdlp'

# 获取下载链接
download_url = bilibili_service.get_download_url(url, quality='best')

# 获取可用格式
formats = bilibili_service.get_available_formats(url)
```

### 高级功能

```python
# 检查API可用性
api_status = bilibili_service.test_api_availability()
print(f"API Status: {api_status['status']}")

# 获取API源信息
source_info = bilibili_service.get_api_source_info(url)
print(f"Has DASH: {source_info['has_dash']}")
print(f"Source: {source_info['api_source']}")

# 强制使用yt-dlp
ytdlp_info = bilibili_service.force_use_ytdlp(url)
```

## API对比

| 特性 | B站官方API | yt-dlp |
|------|------------|--------|
| **响应速度** | 快 | 中等 |
| **准确性** | 高 | 中等 |
| **稳定性** | 依赖官方服务 | 依赖第三方库 |
| **功能完整性** | 针对B站优化 | 通用多平台 |
| **DASH支持** | 原生支持 | 依赖实现 |
| **更新频率** | 官方同步 | 社区维护 |

## 错误处理

### 常见错误及解决方案

1. **API返回403**
   - 可能是IP被限制，会自动回退到yt-dlp

2. **视频不存在**
   - 检查URL是否正确，支持短链接自动解析

3. **地区限制**
   - 官方API和yt-dlp可能都受限

4. **网络超时**
   - 系统会自动重试和回退

### 日志信息

```python
from src.core.logger import logger

# 日志会显示详细过程
logger.info("Trying official Bilibili API for BV123456789")
logger.warning("Official API failed, falling back to yt-dlp")
logger.info("Successfully retrieved video info via yt-dlp")
```

## 测试

运行测试脚本验证功能：

```bash
python test_bilibili_api.py
```

测试内容包括：
- API可用性检查
- 多种URL格式测试
- 格式获取和下载链接
- 强制yt-dlp回退

## 配置选项

### 自定义请求头

```python
# 在BilibiliService中修改headers
self.headers = {
    'User-Agent': 'Your Custom User Agent',
    'Referer': 'https://www.bilibili.com/',
    'Cookie': 'Your cookie if needed',
}
```

### API超时设置

```python
# 修改API调用超时时间
response = self.api_session.get(url, params=params, timeout=30)  # 30秒
```

## 性能优化

### 缓存机制
- 建议实现视频信息缓存，避免重复API调用
- 可以缓存视频基本信息和播放链接

### 并发控制
- 官方API可能有请求频率限制
- 建议控制并发请求数量

## 故障排除

### 1. API不可用
```python
# 检查API状态
status = bilibili_service.test_api_availability()
if status['status'] != 'available':
    print("API不可用，将使用yt-dlp")
```

### 2. 格式选择问题
```python
# 查看可用格式
formats = bilibili_service.get_available_formats(url)
for fmt in formats:
    print(f"{fmt['format_id']}: {fmt['quality_desc']} ({fmt['type']})")
```

### 3. 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 更新日志

### v1.0.0 (当前版本)
- ✅ 集成B站官方API
- ✅ 自动回退机制
- ✅ DASH格式支持
- ✅ 增强的格式选择
- ✅ 完整的错误处理
- ✅ 测试脚本和文档

## 未来计划

- [ ] 添加视频信息缓存
- [ ] 支持更多B站功能（弹幕、评论）
- [ ] 优化并发性能
- [ ] 添加更多质量选项
- [ ] 支持批量下载

## 技术细节

### API端点
- `GET https://api.bilibili.com/x/web-interface/view` - 视频信息
- `GET https://api.bilibili.com/x/player/playurl` - 播放链接

### 请求参数
```python
# 获取播放链接时的参数
params = {
    'bvid': 'BV123456789',
    'cid': 123456789,
    'fourk': 1,
    'otype': 'json',
    'fnver': 0,
    'fnval': 976  # 支持DASH
}
```

### 响应格式转换
API响应会被转换为与yt-dlp兼容的格式，确保代码一致性。

---

如有问题或建议，请查看 `test_bilibili_api.py` 了解详细用法。