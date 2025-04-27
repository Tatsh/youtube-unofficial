from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

__all__ = ('PlaylistInfo', 'PlaylistVideoListRenderer')


class NextContinuationDict(TypedDict):
    clickTrackingParams: str
    continuation: str


class WatchEndpointDict(TypedDict):
    videoId: str


class NavigationEndpointDict(TypedDict):
    watchEndpoint: WatchEndpointDict


class HasKeyText(TypedDict):
    text: str


class RunsOrSimpleTextDict(TypedDict, total=False):
    runs: Sequence[HasKeyText]
    simpleText: str


class RunsOrTextDict(TypedDict, total=False):
    runs: Sequence[HasKeyText]
    text: str


class IconDict(TypedDict):
    iconType: str


class PlaylistVideoRendererMenuRendererItemMenuServiceItemRendererDict(TypedDict):
    icon: IconDict
    serviceEndpoint: Mapping[str, Any]


class PlaylistVideoRendererMenuRendererItemDict(TypedDict):
    menuServiceItemRenderer: PlaylistVideoRendererMenuRendererItemMenuServiceItemRendererDict


class PlaylistVideoRendererMenuRendererDict(TypedDict):
    items: Sequence[PlaylistVideoRendererMenuRendererItemDict]


class PlaylistVideoRendererMenuDict(TypedDict):
    menuRenderer: PlaylistVideoRendererMenuRendererDict


class PlaylistVideoRendererDict(TypedDict, total=False):
    menu: PlaylistVideoRendererMenuDict
    navigationEndpoint: NavigationEndpointDict
    shortBylineText: RunsOrTextDict
    title: RunsOrSimpleTextDict
    videoId: str


class PlaylistInfo(TypedDict, total=False):
    """Playlist information."""
    continuationItemRenderer: dict[str, Any]
    """Continuation data."""
    playlistVideoRenderer: PlaylistVideoRendererDict
    """Inner renderer data."""


class PlaylistVideoListRendererContinuationsDict(TypedDict):
    nextContinuationData: NextContinuationDict


class PlaylistVideoListRenderer(TypedDict):
    """Playlist video list renderer dictionary."""
    contents: Sequence[PlaylistInfo]
    """Inner contents."""
    continuations: Sequence[PlaylistVideoListRendererContinuationsDict]
    """Continuation data."""
