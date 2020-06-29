from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .util import path_default


@dataclass
class CommentHistoryEntry:
    content: str
    delete_action: str
    summary: Sequence[Mapping[str, Any]]
    timestamp: str


def make_comment_history_entry(
        api_entry: Mapping[str, Any]) -> CommentHistoryEntry:
    return CommentHistoryEntry(
        content=api_entry['content']['runs'],
        delete_action=path_default(
            'actionMenu.menuRenderer.items.1.menuNavigationItemRenderer.'
            'navigationEndpoint.confirmDialogEndpoint.content.'
            'confirmDialogRenderer.confirmButton.buttonRenderer.'
            'serviceEndpoint.performCommentActionEndpoint.action', api_entry),
        summary=api_entry['summary']['runs'],
        timestamp=api_entry['timestamp']['simpleText'])
