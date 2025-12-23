"""Main CLI interface."""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.bilibili import bilibili_service
from src.services.downloader import AsyncDownloader
from src.core.config import download_config, config_manager
from src.core.exceptions import VideoDownloaderError
from src.core.logger import logger
from src.utils.file_utils import safe_filename, format_filesize, ensure_directory
from src.utils.url_utils import is_valid_url, is_bilibili_url


console = Console()


class ProgressCallback:
    """Progress callback for rich progress bar."""
    
    def __init__(self, progress: Progress, task_id: int):
        self.progress = progress
        self.task_id = task_id
    
    def __call__(self, progress_percent: float):
        self.progress.update(self.task_id, completed=progress_percent)


@click.group()
@click.version_option(version="1.0.0", prog_name="Video Downloader")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose: bool):
    """Video Downloader - A modern video downloading tool."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")


@cli.command()
@click.argument('url')
@click.option('--output', '-o', help='Output file path')
@click.option('--quality', '-q', default='best', help='Video quality (best/worst/specific format)')
@click.option('--threads', '-t', default=4, help='Number of download threads')
@click.option('--info-only', is_flag=True, help='Show video info only, no download')
def download(url: str, output: Optional[str], quality: str, threads: int, info_only: bool):
    """Download video from URL."""
    try:
        # Validate URL
        if not is_valid_url(url):
            console.print(f"[red]Invalid URL: {url}[/red]")
            return
        
        # Check if supported platform
        if not is_bilibili_url(url):
            console.print(f"[yellow]Warning: URL may not be from supported platform[/yellow]")
        
        # Show video info
        with console.status("[bold green]Getting video information..."):
            video_info = bilibili_service.get_video_info(url)
        
        # Display video info
        display_video_info(video_info)
        
        if info_only:
            return
        
        # Determine output path
        if not output:
            safe_title = safe_filename(video_info['title'])
            output_dir = Path(config_manager.get('download_dir', download_config.default_download_dir))
            ensure_directory(output_dir)
            output = str(output_dir / f"{safe_title}.mp4")
        
        # Get download URL
        with console.status("[bold green]Preparing download..."):
            download_url = bilibili_service.get_download_url(url, quality)
        
        # Start download with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task_id = progress.add_task(
                f"[cyan]Downloading {video_info['title'][:50]}...", 
                total=100
            )
            
            progress_callback = ProgressCallback(progress, task_id)
            
            console.print(f"\n[green]Starting download to: {output}[/green]")
            
            # Run download
            import asyncio
            asyncio.run(
                AsyncDownloader.download_file(
                    download_url, 
                    output, 
                    progress_callback,
                    threads
                )
            )
        
        console.print(f"\n[bold green]✓ Download completed successfully![/bold green]")
        console.print(f"[blue]Saved to: {output}[/blue]")
        
    except VideoDownloaderError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('url')
def info(url: str):
    """Show video information."""
    try:
        if not is_valid_url(url):
            console.print(f"[red]Invalid URL: {url}[/red]")
            return
        
        with console.status("[bold green]Getting video information..."):
            video_info = bilibili_service.get_video_info(url)
        
        display_video_info(video_info)
        
        # Show available formats
        try:
            formats = bilibili_service.get_available_formats(url)
            display_formats(formats)
        except Exception as e:
            logger.warning(f"Failed to get formats: {e}")
        
    except VideoDownloaderError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration."""
    config_table = Table(title="Current Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_items = [
        ("Download Directory", config_manager.get('download_dir', './downloads')),
        ("Max Threads", str(download_config.max_threads)),
        ("Chunk Size", format_filesize(download_config.chunk_size)),
        ("Timeout", f"{download_config.timeout}s"),
        ("Retry Times", str(download_config.retry_times)),
        ("Video Quality", download_config.video_quality),
        ("Audio Only", str(download_config.audio_only)),
        ("Subtitle", str(download_config.subtitle)),
    ]
    
    for key, value in config_items:
        config_table.add_row(key, value)
    
    console.print(config_table)


@cli.command()
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str):
    """Set configuration value."""
    try:
        # Convert value to appropriate type
        if key in ['max_threads', 'timeout', 'retry_times']:
            value = int(value)
        elif key in ['audio_only', 'subtitle']:
            value = value.lower() in ('true', '1', 'yes', 'on')
        
        config_manager.set(key, value)
        console.print(f"[green]✓ Set {key} = {value}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error setting config: {e}[/red]")


def display_video_info(video_info: dict):
    """Display video information in a formatted table."""
    info_table = Table(title="Video Information", show_header=True, header_style="bold magenta")
    info_table.add_column("Property", style="cyan", width=15)
    info_table.add_column("Value", style="white")
    
    # Format duration
    duration = video_info.get('duration', 0)
    if duration:
        duration = int(duration)  # Convert to int
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        duration_str = "Unknown"
    
    # Format view count
    view_count = video_info.get('view_count', 0)
    if view_count:
        view_str = f"{view_count:,}"
    else:
        view_str = "Unknown"
    
    info_items = [
        ("Title", video_info.get('title', 'Unknown')),
        ("Duration", duration_str),
        ("Uploader", video_info.get('uploader', 'Unknown')),
        ("Views", view_str),
        ("Upload Date", video_info.get('upload_date', 'Unknown')),
        ("Video ID", video_info.get('id', 'Unknown')),
    ]
    
    for key, value in info_items:
        # Truncate long values
        if len(str(value)) > 50:
            value = str(value)[:47] + "..."
        info_table.add_row(key, str(value))
    
    console.print(info_table)


def display_formats(formats: list):
    """Display available video formats."""
    if not formats:
        return
    
    format_table = Table(title="Available Formats", show_header=True, header_style="bold blue")
    format_table.add_column("Format ID", style="cyan")
    format_table.add_column("Extension", style="white")
    format_table.add_column("Resolution", style="white")
    format_table.add_column("FPS", style="white")
    format_table.add_column("File Size", style="green")
    
    for fmt in formats[:10]:  # Show top 10 formats
        size = fmt.get('filesize', 0)
        size_str = format_filesize(size) if size else "Unknown"
        
        format_table.add_row(
            fmt.get('format_id', 'N/A'),
            fmt.get('ext', 'N/A'),
            fmt.get('resolution', 'N/A'),
            str(fmt.get('fps', 'N/A')),
            size_str
        )
    
    console.print(format_table)


if __name__ == '__main__':
    cli()