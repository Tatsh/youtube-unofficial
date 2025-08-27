"""Typed dictionaries for YouTube history data."""
from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ('HistoryVideoIDsEntry',)


class Text(TypedDict):
    """Text information."""
    text: str
    """Text content."""


class DescriptionSnippet(TypedDict):
    """Description snippet information."""
    runs: Sequence[Text]
    """Text runs."""


class MetadataBadgeRender(TypedDict):
    """Child of :py:class:`MetadataBadgeRendererTopDict`."""
    style: str
    """Badge style."""


class MetadataBadgeRendererTop(TypedDict):
    """Information about the badge displayed for the user (e.g. checkmark meaning 'verified')."""
    metadataBadgeRenderer: MetadataBadgeRender
    """Inner data."""


class HistoryVideoIDsEntry(TypedDict, total=False):
    """History entry information."""
    description: str
    """Video description."""
    long_byline_text: str
    """Long byline text. Usually video description but may be different."""
    owner_text: str
    """Owner text. Usually the channel name."""
    short_byline_text: str
    """Short byline text. Often channel name but may be different."""
    short_view_count_text: str
    """Short view count text."""
    video_id: str
    """Video ID."""
    view_count_text: str
    """View count text."""
