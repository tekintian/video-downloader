"""Custom exceptions for video downloader."""


class VideoDownloaderError(Exception):
    """Base exception for video downloader."""
    pass


class NetworkError(VideoDownloaderError):
    """Network related errors."""
    pass


class URLParseError(VideoDownloaderError):
    """URL parsing errors."""
    pass


class DownloadError(VideoDownloaderError):
    """Download related errors."""
    pass


class FileOperationError(VideoDownloaderError):
    """File operation errors."""
    pass


class ConfigError(VideoDownloaderError):
    """Configuration related errors."""
    pass


class AuthenticationError(VideoDownloaderError):
    """Authentication related errors."""
    pass