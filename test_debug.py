"""调试错误来源"""

import sys
import os
import asyncio
import logging

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(message)s')

async def test_video_info_extraction():
    """测试视频信息提取"""
    from src.gui.plugins.platforms.bilibili_platform import BilibiliPlatform
    
    platform = BilibiliPlatform()
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    
    try:
        print(f"开始提取视频信息: {test_url}")
        video_info = await platform.extract_video_info(test_url)
        
        if video_info:
            print(f"✅ 成功获取视频信息:")
            print(f"   标题: {video_info.get('title', 'N/A')}")
            print(f"   时长: {video_info.get('duration', 'N/A')}")
            return True
        else:
            print("❌ 视频信息为空")
            return False
            
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_video_info_extraction())
    print(f"\n测试结果: {'成功' if success else '失败'}")