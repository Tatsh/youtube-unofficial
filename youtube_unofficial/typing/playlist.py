from typing import Any, Iterable, Mapping, Sequence, Tuple

from typing_extensions import TypedDict

__all__ = ('PlaylistInfo', )


class WatchEndpointDict(TypedDict):
    videoId: str


class NavigationEndpointDict(TypedDict):
    watchEndpoint: WatchEndpointDict


class PlaylistVideoRendererDict(TypedDict):
    navigationEndpoint: NavigationEndpointDict
    setVideoId: str
    videoId: str


class PlaylistInfo(TypedDict):
    playlistVideoRenderer: PlaylistVideoRendererDict
