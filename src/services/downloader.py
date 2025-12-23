"""Multi-threaded downloader service."""

import os
import asyncio
import aiofiles
import aiohttp
from pathlib import Path
from typing import List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import download_config
from ..core.exceptions import DownloadError, FileOperationError
from ..core.logger import logger


class DownloadProgress:
    """Download progress tracking."""
    
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.downloaded_size = 0
        self.progress_callback: Optional[Callable[[float], None]] = None
    
    def set_progress_callback(self, callback: Callable[[float], None]) -> None:
        """Set progress callback function."""
        self.progress_callback = callback
    
    def update(self, chunk_size: int) -> None:
        """Update download progress."""
        self.downloaded_size += chunk_size
        if self.progress_callback:
            progress = (self.downloaded_size / self.total_size) * 100
            self.progress_callback(progress)


class MultiThreadDownloader:
    """Enhanced multi-threaded downloader."""
    
    def __init__(self, url: str, save_path: str, num_threads: Optional[int] = None):
        self.url = url
        self.save_path = Path(save_path)
        self.num_threads = num_threads or download_config.max_threads
        self.temp_files: List[Path] = []
        self.progress = DownloadProgress(0)
        
        # Ensure directories exist
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Session configuration
        self.headers = {
            "User-Agent": download_config.user_agent,
        }
    
    @retry(
        stop=stop_after_attempt(download_config.retry_times),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_file_size(self) -> int:
        """Get total file size with retry logic."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.head(
                    self.url, 
                    timeout=aiohttp.ClientTimeout(total=download_config.timeout)
                ) as response:
                    if response.status == 200 and 'Content-Length' in response.headers:
                        return int(response.headers['Content-Length'])
                    else:
                        raise DownloadError(f"HTTP {response.status}: Cannot get file size")
        except Exception as e:
            logger.error(f"Failed to get file size: {e}")
            raise DownloadError(f"Failed to retrieve file size: {e}")
    
    async def download_chunk(self, session: aiohttp.ClientSession, start: int, end: int, chunk_index: int) -> Path:
        """Download a specific chunk of the file."""
        headers = {**self.headers, 'Range': f'bytes={start}-{end}'}
        temp_file = self.save_path.with_suffix(f'.part{chunk_index}')
        self.temp_files.append(temp_file)
        
        try:
            async with session.get(
                self.url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=download_config.timeout * 2)
            ) as response:
                response.raise_for_status()
                
                async with aiofiles.open(temp_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(download_config.chunk_size):
                        await f.write(chunk)
                        self.progress.update(len(chunk))
                
                logger.debug(f"Downloaded chunk {chunk_index}: {start}-{end}")
                return temp_file
                
        except Exception as e:
            logger.error(f"Failed to download chunk {chunk_index}: {e}")
            raise DownloadError(f"Failed to download chunk {chunk_index}: {e}")
    
    async def merge_chunks(self) -> None:
        """Merge all downloaded chunks into final file."""
        try:
            async with aiofiles.open(self.save_path, 'wb') as final_file:
                for temp_file in self.temp_files:
                    async with aiofiles.open(temp_file, 'rb') as part_file:
                        while True:
                            chunk = await part_file.read(download_config.chunk_size)
                            if not chunk:
                                break
                            await final_file.write(chunk)
                    
                    # Clean up temp file
                    temp_file.unlink()
            
            logger.info(f"Successfully merged chunks to {self.save_path}")
            
        except Exception as e:
            logger.error(f"Failed to merge chunks: {e}")
            raise FileOperationError(f"Failed to merge downloaded chunks: {e}")
    
    async def download(self, progress_callback: Optional[Callable[[float], None]] = None) -> None:
        """Download file using multiple threads."""
        if progress_callback:
            self.progress.set_progress_callback(progress_callback)
        
        try:
            # Get file size
            total_size = await self.get_file_size()
            self.progress.total_size = total_size
            logger.info(f"File size: {total_size / (1024*1024):.2f} MB")
            
            # Calculate chunk boundaries
            chunk_size = total_size // self.num_threads
            tasks = []
            
            # Create download tasks
            async with aiohttp.ClientSession(headers=self.headers) as session:
                for i in range(self.num_threads):
                    start = i * chunk_size
                    end = start + chunk_size - 1 if i < self.num_threads - 1 else total_size - 1
                    
                    task = self.download_chunk(session, start, end, i)
                    tasks.append(task)
                
                # Execute all download tasks concurrently
                logger.info(f"Starting download with {self.num_threads} threads...")
                await asyncio.gather(*tasks)
            
            # Merge all chunks
            await self.merge_chunks()
            
            logger.info(f"Download complete: {self.save_path}")
            
        except Exception as e:
            # Clean up on failure
            await self.cleanup()
            raise
    
    async def cleanup(self) -> None:
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file}: {e}")


class AsyncDownloader:
    """High-level async downloader interface."""
    
    @staticmethod
    async def download_file(
        url: str, 
        save_path: str, 
        progress_callback: Optional[Callable[[float], None]] = None,
        num_threads: Optional[int] = None
    ) -> None:
        """Download file asynchronously."""
        downloader = MultiThreadDownloader(url, save_path, num_threads)
        await downloader.download(progress_callback)


# Convenience function for synchronous usage
def download_file(
    url: str, 
    save_path: str, 
    progress_callback: Optional[Callable[[float], None]] = None,
    num_threads: Optional[int] = None
) -> None:
    """Download file (synchronous wrapper)."""
    asyncio.run(AsyncDownloader.download_file(url, save_path, progress_callback, num_threads))