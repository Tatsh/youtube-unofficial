from __future__ import annotations

from typing import TYPE_CHECKING, cast

from youtube_unofficial.client import NoFeedbackToken, YouTubeClient
from youtube_unofficial.constants import WATCH_HISTORY_URL, WATCH_LATER_URL
from yt_dlp.cookies import YoutubeDLCookieJar
import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture
    from requests_mock import Mocker


@pytest.fixture
def mock_cookie_jar(mocker: MockerFixture) -> MagicMock:
    mock_jar = mocker.MagicMock()
    mock_jar.get.return_value = 'test_cookie'
    return cast('MagicMock', mock_jar)


@pytest.fixture
def mock_extract_cookies_from_browser(mocker: MockerFixture) -> None:
    mock_jar = mocker.MagicMock(spec=YoutubeDLCookieJar)
    mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser', return_value=mock_jar)


@pytest.fixture
def client(mock_cookie_jar: MagicMock, mock_extract_cookies_from_browser: None) -> YouTubeClient:
    client = YouTubeClient(browser='firefox', profile='default')
    client.session.cookies = mock_cookie_jar
    return client


def test_remove_video_id_from_playlist(mocker: MockerFixture, requests_mock: Mocker,
                                       client: YouTubeClient) -> None:
    ytcfg_mock = {
        'INNERTUBE_API_KEY': 'test_api_key',
        'VISITOR_DATA': 'test_visitor_data',
        'DELEGATED_SESSION_ID': 'test_session_id',
        'SESSION_INDEX': 0,
    }
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=ytcfg_mock)
    mocker.patch('youtube_unofficial.client.context_client_body', return_value={})
    mocker.patch('youtube_unofficial.client.Soup')

    requests_mock.get(WATCH_LATER_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse/edit_playlist',
        json={'status': 'STATUS_SUCCEEDED'},
    )

    result = client.remove_video_id_from_playlist(playlist_id='test_playlist',
                                                  video_id='test_video')
    assert result is True


def test_clear_watch_history_no_feedback_token(mocker: MockerFixture, requests_mock: Mocker,
                                               client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    mocker.patch('youtube_unofficial.client.initial_data', return_value={})

    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/feedback',
        json={'status': 'STATUS_SUCCEEDED'},
    )

    with pytest.raises(NoFeedbackToken):
        client.clear_watch_history()


def test_clear_watch_history_clear_button_disabled(mocker: MockerFixture, requests_mock: Mocker,
                                                   client: YouTubeClient) -> None:
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {
                                     'contents': [{
                                         'buttonRenderer': {
                                             'isDisabled': True,
                                         }
                                     }]
                                 }
                             }
                         }
                     }
                 })
    assert client.clear_watch_history() is False


def test_clear_watch_history(mocker: MockerFixture, requests_mock: Mocker,
                             client: YouTubeClient) -> None:
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/feedback',
                       json={'feedbackResponses': [{
                           'isProcessed': True
                       }]})
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {
                                     'contents': [{}, {
                                         'buttonRenderer': {
                                             'navigationEndpoint': {
                                                 'confirmDialogEndpoint': {
                                                     'content': {
                                                         'confirmDialogRenderer': {
                                                             'confirmEndpoint': {
                                                                 'feedbackEndpoint': {
                                                                     'feedbackToken': '',
                                                                 },
                                                                 'commandMetadata': {
                                                                     'webCommandMetadata': {
                                                                         'apiUrl':
                                                                             '/youtubei/v1/feedback'
                                                                     }
                                                                 },
                                                             }
                                                         }
                                                     }
                                                 }
                                             }
                                         }
                                     }]
                                 }
                             }
                         }
                     }
                 })
    assert client.clear_watch_history() is True


def test_get_playlist_info(mocker: MockerFixture, requests_mock: Mocker,
                           client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'tabs': [{
                                 'tabRenderer': {
                                     'content': {
                                         'sectionListRenderer': {
                                             'contents': [{
                                                 'itemSectionRenderer': {
                                                     'contents': [{
                                                         'playlistVideoListRenderer': {
                                                             'contents': [{
                                                                 'playlistVideoRenderer': {}
                                                             }]
                                                         }
                                                     }]
                                                 }
                                             }]
                                         }
                                     }
                                 }
                             }]
                         }
                     }
                 })
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    result = list(client.get_playlist_info(playlist_id='test_playlist'))
    assert result == [{'playlistVideoRenderer': {}}]


def test_get_playlist_info_empty(mocker: MockerFixture, requests_mock: Mocker,
                                 client: YouTubeClient) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'tabs': [{
                                 'tabRenderer': {
                                     'content': {
                                         'sectionListRenderer': {
                                             'contents': [{
                                                 'itemSectionRenderer': {
                                                     'contents': [{}]
                                                 }
                                             }]
                                         }
                                     }
                                 }
                             }]
                         }
                     }
                 })
    with pytest.raises(KeyError, match=r'This playlist might be empty\.'):
        list(client.get_playlist_info(playlist_id='test_playlist'))


def test_get_playlist_info_empty_alt(mocker: MockerFixture, requests_mock: Mocker,
                                     client: YouTubeClient) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data', return_value={'contents': {}})
    with pytest.raises(KeyError, match=r'twoColumnBrowseResultsRenderer'):
        list(client.get_playlist_info(playlist_id='test_playlist'))


def test_clear_playlist(mocker: MockerFixture, client: YouTubeClient) -> None:
    mock_session = mocker.Mock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    mocker.patch.object(client, 'get_playlist_info', return_value=iter([]))
    client.clear_playlist(playlist_id='test_playlist')


def test_clear_watch_later(mocker: MockerFixture, client: YouTubeClient) -> None:
    mock_session = mocker.Mock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    mocker.patch.object(client, 'clear_playlist')
    client.clear_watch_later()
    client.clear_playlist.assert_called_once_with('WL')  # type: ignore[attr-defined]


def test_remove_video_ids_from_history(mocker: MockerFixture, client: YouTubeClient) -> None:
    mock_session = mocker.MagicMock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    mocker.patch.object(client, 'get_history_info', return_value=iter([]))
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    result = client.remove_video_ids_from_history(video_ids=['test_video'])
    assert result is False


def test_toggle_history(mocker: MockerFixture, client: YouTubeClient,
                        requests_mock: Mocker) -> None:
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/feedback',
                       json={'feedbackResponses': [{
                           'isProcessed': True
                       }]})
    mock_session = mocker.MagicMock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {
                                     'contents': [{}, {}, {
                                         'buttonRenderer': {
                                             'navigationEndpoint': {
                                                 'confirmDialogEndpoint': {
                                                     'content': {
                                                         'confirmDialogRenderer': {
                                                             'confirmEndpoint': {
                                                                 'feedbackEndpoint': {
                                                                     'feedbackToken': '',
                                                                 },
                                                                 'commandMetadata': {
                                                                     'webCommandMetadata': {
                                                                         'apiUrl':
                                                                             '/youtubei/v1/feedback'
                                                                     }
                                                                 },
                                                             }
                                                         }
                                                     }
                                                 }
                                             }
                                         }
                                     }]
                                 }
                             }
                         }
                     }
                 })
    result = client.toggle_watch_history()
    assert result is True
