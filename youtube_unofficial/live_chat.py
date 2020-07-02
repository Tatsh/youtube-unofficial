from dataclasses import dataclass
from typing import Any, Optional, Mapping, Sequence
from .util import path as at_path, try_get

__all__ = ('LiveChatHistoryEntry', 'make_live_chat_history_entry')


@dataclass
class LiveChatHistoryEntry:
    delete_params: str
    message: Sequence[str]
    timestamp: str
    video_title: Optional[str]
    video_url: Optional[str]


def make_live_chat_history_entry(
        api_entry: Mapping[str, Any]) -> LiveChatHistoryEntry:
    video_title_info = try_get(
        api_entry,
        lambda x: x['videoTitle']['runs'][0],
    ) or dict(text=None)
    video_url = try_get(
        video_title_info, lambda x: (x['navigationEndpoint']['commandMetadata']
                                     ['webCommandMetadata']['url']))
    if video_url:
        video_url = f'https://www.youtube.com{video_url}'
    return LiveChatHistoryEntry(delete_params=at_path(
        'deleteButton.buttonRenderer.command.'
        'signalServiceEndpoint.actions.0.openPopupAction.popup.'
        'confirmDialogRenderer.confirmButton.buttonRenderer.serviceEndpoint.'
        'deleteLiveChatMessageCommand.params', api_entry),
                                message=[
                                    x['text']
                                    for x in api_entry['message']['runs']
                                ],
                                timestamp=api_entry['timestamp']['simpleText'],
                                video_title=video_title_info['text'],
                                video_url=video_url)
