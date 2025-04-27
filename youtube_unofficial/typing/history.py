from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ('DescriptionSnippetDict', 'MetadataBadgeRenderDict', 'MetadataBadgeRendererTopDict',
           'TextDict')


class TextDict(TypedDict):
    """Text information."""
    text: str
    """Text content."""


class DescriptionSnippetDict(TypedDict):
    """Description snippet information."""
    runs: Sequence[TextDict]
    """Text runs."""


class MetadataBadgeRenderDict(TypedDict):
    """Child of :py:class:`MetadataBadgeRendererTopDict`."""
    style: str
    """Badge style."""


class MetadataBadgeRendererTopDict(TypedDict):
    """Information about the badge displayed for the user (e.g. checkmark meaning 'verified')."""
    metadataBadgeRenderer: MetadataBadgeRenderDict
    """Inner data."""
