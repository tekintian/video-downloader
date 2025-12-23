"""测试GUI基本功能的脚本"""

import asyncio
import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.bilibili import bilibili_service
from src.gui.plugins.platforms.bilibili_platform import BilibiliPlatform

async def test_bilibili_platform():
    """测试B站平台功能"""
    print("🧪 测试B站平台功能...")
    
    platform = BilibiliPlatform()
    test_url = "https://www.bilibili.com/video/BV1H7qrBkEPN/"
    
    print(f"📝 测试URL: {test_url}")
    print(f"🏷️  平台名称: {platform.name}")
    print(f"🌐 支持域名: {platform.supported_domains}")
    
    # 测试URL识别
    is_supported = platform.is_supported_url(test_url)
    print(f"✅ URL支持检查: {is_supported}")
    
    if is_supported:
        try:
            # 测试视频信息提取
            print("📊 正在提取视频信息...")
            video_info = await platform.extract_video_info(test_url)
            
            if video_info:
                print("🎉 视频信息提取成功!")
                print(f"   标题: {video_info.get('title', 'N/A')}")
                print(f"   时长: {video_info.get('duration', 'N/A')}")
                print(f"   作者: {video_info.get('uploader', 'N/A')}")
                print(f"   描述: {video_info.get('description', 'N/A')[:50]}...")
                return True
            else:
                print("❌ 视频信息提取失败")
                return False
                
        except Exception as e:
            print(f"❌ 提取过程中出错: {e}")
            return False
    else:
        print("❌ URL不支持")
        return False

async def test_service_direct():
    """直接测试服务层"""
    print("\n🔧 测试服务层...")
    
    test_url = "https://www.bilibili.com/video/BV1H7qrBkEPN/"
    
    try:
        video_info = bilibili_service.get_video_info(test_url)
        if video_info:
            print("🎉 服务层测试成功!")
            print(f"   标题: {video_info.get('title', 'N/A')}")
            print(f"   时长: {video_info.get('duration', 'N/A')}")
            return True
        else:
            print("❌ 服务层测试失败")
            return False
    except Exception as e:
        print(f"❌ 服务层测试出错: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始功能测试...\n")
    
    # 测试服务层
    service_ok = await test_service_direct()
    
    # 测试平台层
    platform_ok = await test_bilibili_platform()
    
    print(f"\n📋 测试结果:")
    print(f"   服务层: {'✅ 通过' if service_ok else '❌ 失败'}")
    print(f"   平台层: {'✅ 通过' if platform_ok else '❌ 失败'}")
    
    if service_ok and platform_ok:
        print("\n🎊 所有测试通过! GUI功能正常!")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查相关代码")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)