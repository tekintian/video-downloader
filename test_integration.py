#!/usr/bin/env python3
"""
Integration test for video downloader functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.bilibili import bilibili_service
from src.services.downloader import AsyncDownloader
from src.core.config import download_config
from src.utils.url_utils import is_valid_url, is_bilibili_url
from src.core.logger import logger


async def test_video_info():
    """Test video information retrieval."""
    test_url = "https://www.bilibili.com/video/BV1xx411c7mu"
    
    print(f"Testing video info for: {test_url}")
    
    # Test URL validation
    assert is_valid_url(test_url), "URL should be valid"
    assert is_bilibili_url(test_url), "URL should be Bilibili URL"
    
    # Get video info
    video_info = bilibili_service.get_video_info(test_url)
    
    print(f"✓ Video title: {video_info['title']}")
    print(f"✓ Video duration: {video_info['duration']}s")
    print(f"✓ Video uploader: {video_info['uploader']}")
    
    return video_info


async def test_download_url():
    """Test download URL retrieval."""
    test_url = "https://www.bilibili.com/video/BV1xx411c7mu"
    
    print(f"\nTesting download URL retrieval for: {test_url}")
    
    # First get available formats
    formats = bilibili_service.get_available_formats(test_url)
    if formats:
        # Use the first available format
        format_id = formats[0]['format_id']
        print(f"Using format: {format_id}")
        
        # Get download URL with specific format
        download_url = bilibili_service.get_download_url(test_url, format_id)
        
        print(f"✓ Download URL: {download_url[:100] if download_url else 'None'}...")
        
        return download_url
    else:
        print("✗ No formats available")
        return None


async def test_downloader_capabilities():
    """Test downloader capabilities without actual download."""
    print(f"\nTesting downloader capabilities...")
    
    # Test configuration
    print(f"✓ Max threads: {download_config.max_threads}")
    print(f"✓ Chunk size: {download_config.chunk_size}")
    print(f"✓ Timeout: {download_config.timeout}s")
    print(f"✓ Retry times: {download_config.retry_times}")
    
    return True


async def test_formats():
    """Test format retrieval."""
    test_url = "https://www.bilibili.com/video/BV1xx411c7mu"
    
    print(f"\nTesting format retrieval for: {test_url}")
    
    # Get available formats
    formats = bilibili_service.get_available_formats(test_url)
    
    print(f"✓ Found {len(formats)} formats")
    
    for i, fmt in enumerate(formats[:3]):  # Show first 3 formats
        print(f"  - Format {i+1}: {fmt['format_id']} ({fmt['ext']})")
    
    return formats


async def main():
    """Run all integration tests."""
    print("🚀 Starting Video Downloader Integration Tests\n")
    
    try:
        # Test video info
        video_info = await test_video_info()
        
        # Test formats
        formats = await test_formats()
        
        # Test download URL
        download_url = await test_download_url()
        
        # Test downloader capabilities
        await test_downloader_capabilities()
        
        print(f"\n✅ All tests passed!")
        print(f"📊 Summary:")
        print(f"   - Video: {video_info['title']}")
        print(f"   - Duration: {video_info['duration']}s")
        print(f"   - Formats: {len(formats)} available")
        print(f"   - Download URL: {'✓' if download_url else '✗'}")
        
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)