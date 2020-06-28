from typing import Sequence

from typing_extensions import TypedDict

__all__ = ('PlaylistInfo', )


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


class PlaylistVideoRendererDict(TypedDict, total=False):
    navigationEndpoint: NavigationEndpointDict
    shortBylineText: RunsOrTextDict
    setVideoId: str
    title: RunsOrSimpleTextDict
    videoId: str


class PlaylistInfo(TypedDict):
    playlistVideoRenderer: PlaylistVideoRendererDict
