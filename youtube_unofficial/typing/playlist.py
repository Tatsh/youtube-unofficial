"""Typed dictionaries for YouTube playlist data."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = (
    'HasKeyText',
    'Icon',
    'NavigationEndpoint',
    'NextContinuation',
    'PlaylistInfo',
    'PlaylistVideoIDsEntry',
    'PlaylistVideoListRenderer',
    'PlaylistVideoListRendererContinuations',
    'PlaylistVideoRenderer',
    'PlaylistVideoRendererMenu',
    'PlaylistVideoRendererMenuRenderer',
    'PlaylistVideoRendererMenuRendererItem',
    'PlaylistVideoRendererMenuRendererItemMenuServiceItemRenderer',
    'RunsOrSimpleText',
    'RunsOrText',
    'WatchEndpoint',
)


class NextContinuation(TypedDict):
    """Continuation data."""
    clickTrackingParams: str
    """Click tracking parameters."""
    continuation: str
    """Continuation token."""


class WatchEndpoint(TypedDict):
    """Watch endpoint data."""
    videoId: str
    """Video ID."""


class NavigationEndpoint(TypedDict):
    """Navigation endpoint data."""
    watchEndpoint: WatchEndpoint
    """Watch endpoint data."""


class HasKeyText(TypedDict):
    """Inside :py:class:`RunsOrSimpleText` and :py:class:`RunsOrText`."""
    text: str
    """Text content."""


class RunsOrSimpleText(TypedDict, total=False):
    """Inside :py:class:`PlaylistVideoRenderer`."""
    runs: Sequence[HasKeyText]
    """Text runs."""
    simpleText: str
    """Text content."""


class RunsOrText(TypedDict, total=False):
    """Inside :py:class:`PlaylistVideoRenderer`."""
    runs: Sequence[HasKeyText]
    """Text runs."""
    text: str
    """Text content."""


class Icon(TypedDict):
    """Icon data."""
    iconType: str
    """Icon type."""


class PlaylistVideoRendererMenuRendererItemMenuServiceItemRenderer(TypedDict):
    """Menu renderer."""
    icon: Icon
    """Icon data."""
    serviceEndpoint: dict[str, Any]
    """Service endpoint data."""


class PlaylistVideoRendererMenuRendererItem(TypedDict):
    """Menu renderer item."""
    menuServiceItemRenderer: PlaylistVideoRendererMenuRendererItemMenuServiceItemRenderer
    """Menu service item renderer."""


class PlaylistVideoRendererMenuRenderer(TypedDict):
    """Menu renderer."""
    items: Sequence[PlaylistVideoRendererMenuRendererItem]
    """Menu items."""


class PlaylistVideoRendererMenu(TypedDict):
    """Menu data."""
    menuRenderer: PlaylistVideoRendererMenuRenderer
    """Menu renderer data."""


class PlaylistVideoRenderer(TypedDict, total=False):
    """Playlist video renderer dictionary."""
    menu: PlaylistVideoRendererMenu
    """Menu data."""
    navigationEndpoint: NavigationEndpoint
    """Navigation endpoint data."""
    shortBylineText: RunsOrText
    """Short byline text."""
    title: RunsOrSimpleText
    """Video title."""
    videoId: str
    """Video ID."""


class PlaylistInfo(TypedDict, total=False):
    """Playlist information."""
    continuationItemRenderer: dict[str, Any]
    """Continuation data."""
    playlistVideoRenderer: PlaylistVideoRenderer
    """Inner renderer data."""


class PlaylistVideoListRendererContinuations(TypedDict):
    """Continuation data."""
    nextContinuationData: NextContinuation
    """Continuation data."""


class PlaylistVideoListRenderer(TypedDict):
    """Playlist video list renderer dictionary."""
    contents: Sequence[PlaylistInfo]
    """Inner contents."""
    continuations: Sequence[PlaylistVideoListRendererContinuations]
    """Continuation data."""


class PlaylistVideoIDsEntry(TypedDict):
    """Playlist information."""
    owner: str | None
    """Playlist owner."""
    title: str | None
    """Playlist title."""
    video_id: str
    """Video ID."""
    watch_url: str
    """Watch URL."""
