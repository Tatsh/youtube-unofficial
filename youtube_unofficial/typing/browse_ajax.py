from typing import Any, Iterable, Sequence, Tuple

from typing_extensions import TypedDict

__all__ = ('BrowseAJAXSequence', )


class NextContinuationDict(TypedDict):
    clickTrackingParams: str
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
    sectionListContinuation: ItemSectionContinuationDict


class AppendContinuationDict(TypedDict):
    appendContinuationItemsAction: Any


class ResponseDict(TypedDict, total=False):
    continuationContents: ContinuationContentsDict
    onResponseReceivedActions: Sequence[AppendContinuationDict]


class BrowseAJAXDict(TypedDict):
    response: ResponseDict
    xsrf_token: str


BrowseAJAXSequence = Tuple[Any, BrowseAJAXDict]
