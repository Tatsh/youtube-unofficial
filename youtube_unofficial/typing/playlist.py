from typing import Iterable, Sequence

from typing_extensions import TypedDict

from youtube_unofficial.typing.browse_ajax import NextContinuationDict

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


class PlaylistVideoListRendererContinuationsDict(TypedDict):
    nextContinuationData: NextContinuationDict


class PlaylistVideoListRenderer(TypedDict):
    contents: Iterable[PlaylistInfo]
    continuations: Sequence[PlaylistVideoListRendererContinuationsDict]
