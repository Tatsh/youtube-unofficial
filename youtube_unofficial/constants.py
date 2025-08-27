"""Constants."""
from __future__ import annotations

__all__ = ('EXTRACTED_THUMBNAIL_KEYS', 'HISTORY_ENTRY_KEYS_TO_SKIP', 'SIMPLE_TEXT_KEYS',
           'TEXT_RUNS_KEYS', 'THUMBNAILS_KEYS', 'USER_AGENT', 'WATCH_HISTORY_URL',
           'WATCH_LATER_URL')

USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/136.0.0.0 Safari/537.36')
"""
User agent.

:meta hide-value:
"""
WATCH_HISTORY_URL = 'https://www.youtube.com/feed/history'
"""
URL for the Watch History page.

:meta hide-value:
"""
WATCH_LATER_URL = 'https://www.youtube.com/playlist?list=WL'
"""
URL for the Watch Later playlist.

:meta hide-value:
"""
# print-history-ids constants
EXTRACTED_THUMBNAIL_KEYS = {'width', 'height', 'url'}
HISTORY_ENTRY_KEYS_TO_SKIP = {
    'isWatched', 'menu', 'navigationEndpoint', 'showActionMenu', 'thumbnailOverlays',
    'trackingParams'
}
"""
Keys to skip when extracting history entry data.

:meta hide-value:
"""
SIMPLE_TEXT_KEYS = {
    'shortViewCountText': 'short_view_count_text',
    'viewCountText': 'view_count_text'
}
"""
Keys for simple text fields.

:meta hide-value:
"""
TEXT_RUNS_KEYS = {
    'descriptionSnippet': 'description',
    'longBylineText': 'long_byline_text',
    'ownerText': 'owner_text',
    'title': 'title',
    'shortBylineText': 'short_byline_text',
}
"""
Keys for text runs fields.

:meta hide-value:
"""
THUMBNAILS_KEYS = {'channelThumbnailSupportedRenderers', 'richThumbnail'}
"""
Keys for thumbnail fields.

:meta hide-value:
"""
