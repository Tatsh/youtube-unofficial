from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from .util import path_default, try_get

__all__ = ('CommentHistoryEntry', 'DEFAULT_DELETE_ACTION_PATH',
           'make_comment_history_entry')

DEFAULT_DELETE_ACTION_PATH = (
    'actionMenu.menuRenderer.items.1.menuNavigationItemRenderer.'
    'navigationEndpoint.confirmDialogEndpoint.content.'
    'confirmDialogRenderer.confirmButton.buttonRenderer.'
    'serviceEndpoint.performCommentActionEndpoint.action')


@dataclass
class CommentHistoryEntry:
    delete_action: str
    summary: Sequence[Mapping[str, Any]]
    timestamp: str
    content: Optional[str] = None


def make_comment_history_entry(
    api_entry: Mapping[str, Any],
    delete_action_path: str = DEFAULT_DELETE_ACTION_PATH
) -> CommentHistoryEntry:
    return CommentHistoryEntry(content=try_get(api_entry,
                                               lambda x: x['content']['runs']),
                               delete_action=path_default(
                                   delete_action_path, api_entry),
                               summary=api_entry['summary']['runs'],
                               timestamp=api_entry['timestamp']['simpleText'])
