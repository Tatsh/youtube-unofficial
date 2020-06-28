from typing import Sequence

from typing_extensions import TypedDict

__all__ = ('DescriptionSnippetDict', 'IconTypeDict', 'MetadataBadgeRenderDict',
           'MetadataBadgeRendererTopDict', 'TextDict')


class TextDict(TypedDict):
    text: str


class DescriptionSnippetDict(TypedDict):
    runs: Sequence[TextDict]


class IconTypeDict(TypedDict):
    iconType: str


class MetadataBadgeRenderDict(TypedDict):
    icon: IconTypeDict
    style: str


class MetadataBadgeRendererTopDict(TypedDict):
    metadataBadgeRenderer: MetadataBadgeRenderDict
