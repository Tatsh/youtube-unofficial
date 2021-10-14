from typing import Any, Dict, Mapping, Sequence, TypedDict

from .browse_ajax import NextContinuationDict

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


class IconDict(TypedDict):
    iconType: str


class PlaylistVideoRendererMenuRendererItemMenuServiceItemRendererDict(
        TypedDict):
    icon: IconDict
    serviceEndpoint: Mapping[str, Any]


class PlaylistVideoRendererMenuRendererItemDict(TypedDict):
    menuServiceItemRenderer: PlaylistVideoRendererMenuRendererItemMenuServiceItemRendererDict


class PlaylistVideoRendererMenuRendererDict(TypedDict):
    items: Sequence[PlaylistVideoRendererMenuRendererItemDict]


class PlaylistVideoRendererMenuDict(TypedDict):
    menuRenderer: PlaylistVideoRendererMenuRendererDict


class PlaylistVideoRendererDict(TypedDict, total=False):
    navigationEndpoint: NavigationEndpointDict
    shortBylineText: RunsOrTextDict
    title: RunsOrSimpleTextDict
    videoId: str

    menu: PlaylistVideoRendererMenuDict


class PlaylistInfo(TypedDict, total=False):
    continuationItemRenderer: Dict[str, Any]
    playlistVideoRenderer: PlaylistVideoRendererDict


class PlaylistVideoListRendererContinuationsDict(TypedDict):
    nextContinuationData: NextContinuationDict


class PlaylistVideoListRenderer(TypedDict):
    contents: Sequence[PlaylistInfo]
    continuations: Sequence[PlaylistVideoListRendererContinuationsDict]
