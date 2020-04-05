from typing import Any, Iterable, Mapping, Sequence, Tuple

from typing_extensions import TypedDict

__all__ = ('BrowseAJAXSequence', )


class NextContinuationDict(TypedDict):
    clickTrackingParams: Mapping[str, str]
    continuation: str


class ContinuationDict(TypedDict):
    nextContinuationData: NextContinuationDict


class PlaylistVideoListContinuationDict(TypedDict, total=False):
    contents: Iterable[Any]
    continuations: Sequence[ContinuationDict]


class ItemSectionContinuationDict(TypedDict, total=False):
    contents: Iterable[Any]
    continuations: Sequence[ContinuationDict]


class ContinuationContentsDict(TypedDict):
    playlistVideoListContinuation: PlaylistVideoListContinuationDict
    itemSectionContinuation: ItemSectionContinuationDict


class ResponseDict(TypedDict):
    continuationContents: ContinuationContentsDict


class BrowseAJAXDict(TypedDict):
    response: ResponseDict
    xsrf_token: str


BrowseAJAXSequence = Tuple[Any, BrowseAJAXDict]
