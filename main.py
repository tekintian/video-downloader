#!/usr/bin/env python3
"""
Video Downloader - Main entry point
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.main import cli

if __name__ == '__main__':
    cli()