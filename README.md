# Video Downloader

A modern, feature-rich video downloading tool with multi-threading support, built with inspiration from the double-mouse-downloader project.

## Features

- 🚀 **Multi-threaded Downloads**: Fast downloading with configurable thread count
- 🎬 **Multiple Platform Support**: Bilibili (with plans for more platforms)
- 📊 **Rich CLI Interface**: Beautiful terminal UI with progress bars
- ⚙️ **Flexible Configuration**: Customizable download settings
- 🔍 **Video Information**: Detailed video metadata and format information
- 🛡️ **Error Handling**: Robust error handling with retry logic
- 📝 **Logging**: Comprehensive logging system
- 🎯 **Smart File Naming**: Automatic safe filename generation

## Installation

### From Source

```bash
git clone https://github.com/tekintian/video-downloader.git
cd video-downloader
pip install -r requirements.txt
pip install -e .
```

### Using pip (when published)

```bash
pip install video-downloader
```

## Quick Start

### Basic Usage

```bash
# Download a video
python main.py download "https://www.bilibili.com/video/BV1xx411c7mD"

# Download with custom output path
python main.py download "https://www.bilibili.com/video/BV1xx411c7mD" -o "/path/to/output.mp4"

# Download with specific quality and threads
python main.py download "https://www.bilibili.com/video/BV1xx411c7mD" -q "best" -t 8
```

### Get Video Information

```bash
# Show video details
python main.py info "https://www.bilibili.com/video/BV1xx411c7mD"
```

### Configuration

```bash
# Show current configuration
python main.py config

# Set configuration values
python main.py set-config max_threads 8
python main.py set-config download_dir "/path/to/downloads"
```

## CLI Commands

### `download`
Download video from URL

```bash
python main.py download [OPTIONS] URL

Options:
  -o, --output PATH     Output file path
  -q, --quality TEXT    Video quality (best/worst/specific format) [default: best]
  -t, --threads INTEGER Number of download threads [default: 4]
  --info-only          Show video info only, no download
  -v, --verbose        Enable verbose logging
```

### `info`
Show video information without downloading

```bash
python main.py info URL
```

### `config`
Show current configuration

```bash
python main.py config
```

### `set-config`
Set configuration value

```bash
python main.py set-config KEY VALUE
```

## Configuration

The application supports both environment variables and configuration files:

### Environment Variables
Prefix with `VIDEO_DOWNLOADER_`:
- `VIDEO_DOWNLOADER_MAX_THREADS=4`
- `VIDEO_DOWNLOADER_DOWNLOAD_DIR=./downloads`
- `VIDEO_DOWNLOADER_TIMEOUT=30`
- `VIDEO_DOWNLOADER_RETRY_TIMES=3`

### Configuration File
Configuration is stored in `~/.video_downloader/config.json`:

```json
{
  "download_dir": "./downloads",
  "max_threads": 4,
  "video_quality": "best",
  "subtitle": true,
  "theme": "dark"
}
```

## Architecture

The project follows a modular architecture inspired by double-mouse-downloader:

```
video_down/
├── src/
│   ├── core/                 # Core functionality
│   │   ├── config.py        # Configuration management
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── logger.py        # Logging setup
│   ├── services/             # Business logic
│   │   ├── bilibili.py      # Bilibili service
│   │   └── downloader.py    # Download engine
│   ├── utils/                # Utility functions
│   │   ├── file_utils.py    # File operations
│   │   └── url_utils.py     # URL handling
│   └── cli/                  # Command line interface
│       └── main.py          # CLI implementation
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── setup.py                 # Package setup
└── README.md                # Documentation
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/tekintian/video-downloader.git
cd video-downloader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_bilibili.py
```

### Code Formatting

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/
```

## Requirements

- Python 3.8+
- See `requirements.txt` for detailed dependencies

### Main Dependencies

- `yt-dlp`: Video extraction and download
- `aiohttp`: Async HTTP client
- `aiofiles`: Async file operations
- `click`: CLI framework
- `rich`: Rich terminal output
- `pydantic`: Data validation
- `loguru`: Logging
- `tenacity`: Retry logic
- `pathvalidate`: Safe filename handling

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the [double-mouse-downloader](https://github.com/double-mouse/downloader) project
- Built with modern Python async patterns
- UI powered by the excellent [Rich](https://github.com/Textualize/rich) library

## Roadmap

- [ ] Support for YouTube
- [ ] Support for more platforms (TikTok, Instagram, etc.)
- [ ] GUI interface (Electron/React)
- [ ] Playlist/Batch downloads
- [ ] Auto subtitle download
- [ ] Video conversion capabilities
- [ ] Download scheduling
- [ ] Browser extension

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/tekintian/video-downloader/issues) page
2. Create a new issue with detailed information
3. Join our [Discussions](https://github.com/tekintian/video-downloader/discussions) for general questions

---

**Happy Downloading! 🚀**