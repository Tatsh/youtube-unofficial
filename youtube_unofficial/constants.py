from typing import Mapping, Set, Tuple
from typing_extensions import Final

__all__ = (
    'BROWSE_AJAX_URL',
    'CHALLENGE_URL',
    'COMMENT_HISTORY_URL',
    'EXTRACTED_THUMBNAIL_KEYS',
    'HISTORY_ENTRY_KEYS_TO_SKIP',
    'HISTORY_URL',
    'HOMEPAGE_URL',
    'LIVE_CHAT_HISTORY_URL',
    'LOGIN_URL',
    'LOOKUP_URL',
    'NETRC_MACHINE',
    'SERVICE_AJAX_URL',
    'SIMPLE_TEXT_KEYS',
    'TEXT_RUNS_KEYS',
    'TFA_URL',
    'THUMBNAILS_KEYS',
    'USER_AGENT',
    'WATCH_HISTORY_URL',
    'WATCH_LATER_URL',
)

NETRC_MACHINE: Final[str] = 'youtube'
USER_AGENT: Final[str] = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36')

BROWSE_AJAX_URL: Final[str] = 'https://www.youtube.com/browse_ajax'
CHALLENGE_URL: Final[str] = 'https://accounts.google.com/_/signin/sl/challenge'
COMMENT_HISTORY_URL: Final[str] = ('https://www.youtube.com/feed/history/'
                                   'comment_history')
COMMUNITY_HISTORY_URL: Final[str] = ('https://www.youtube.com/feed/history/'
                                     'community_history')
HISTORY_URL: Final[str] = 'https://www.youtube.com/feed/history'
LIVE_CHAT_HISTORY_URL: Final[str] = ('https://www.youtube.com/feed/history/'
                                     'live_chat_history')
LOGIN_URL: Final[str] = 'https://accounts.google.com/ServiceLogin'
LOOKUP_URL: Final[str] = 'https://accounts.google.com/_/signin/sl/lookup'
SEARCH_HISTORY_URL: Final[str] = ('https://www.youtube.com/feed/history/'
                                  'search_history')
SERVICE_AJAX_URL: Final[str] = 'https://www.youtube.com/service_ajax'
TFA_URL: Final[
    str] = 'https://accounts.google.com/_/signin/challenge?hl=en&TL={0}'
WATCH_HISTORY_URL: Final[str] = 'https://www.youtube.com/feed/history'
WATCH_LATER_URL: Final[str] = 'https://www.youtube.com/playlist?list=WL'
# print-history-ids constants
EXTRACTED_THUMBNAIL_KEYS: Final[Tuple[str, str,
                                      str]] = ('width', 'height', 'url')
HISTORY_ENTRY_KEYS_TO_SKIP: Final[Set[str]] = {
    'menu', 'navigationEndpoint', 'thumbnailOverlays', 'trackingParams'
}
SIMPLE_TEXT_KEYS: Final[Mapping[str, str]] = {
    'shortViewCountText': 'short_view_count_text',
    'viewCountText': 'view_count_text'
}
TEXT_RUNS_KEYS: Final[Mapping[str, str]] = {
    'descriptionSnippet': 'description',
    'longBylineText': 'long_byline_text',
    'ownerText': 'owner_text',
    'title': 'title',
    'shortBylineText': 'short_byline_text',
}
THUMBNAILS_KEYS: Final[Mapping[str, Tuple[str, str]]] = {
    'channelThumbnailSupportedRenderers':
    ('channelThumbnailWithLinkRenderer.thumbnail.thumbnails',
     'channel_thumbnails'),
    'richThumbnail':
    ('movingThumbnailRenderer.movingThumbnailDetails.thumbnails',
     'moving_thumbnails'),
}
