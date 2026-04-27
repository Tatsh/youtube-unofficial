"""Unofficial YouTube client."""
from __future__ import annotations

from .client import YouTubeClient
from .session import build_youtube_session

__all__ = ('YouTubeClient', 'build_youtube_session')
__version__ = 'v0.4.0'
