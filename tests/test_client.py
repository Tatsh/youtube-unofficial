from __future__ import annotations

from typing import TYPE_CHECKING, cast

from youtube_unofficial.client import NoFeedbackToken, YouTubeClient
from youtube_unofficial.constants import WATCH_HISTORY_URL, WATCH_LATER_URL
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
    mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser', return_value={})


def test_remove_video_id_from_playlist(mocker: MockerFixture, requests_mock: Mocker,
                                       mock_cookie_jar: MagicMock,
                                       mock_extract_cookies_from_browser: None) -> None:
    client = YouTubeClient(browser='firefox', profile='default')
    client.session.cookies = mock_cookie_jar

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
                                               mock_cookie_jar: MagicMock,
                                               mock_extract_cookies_from_browser: None) -> None:
    client = YouTubeClient(browser='firefox', profile='default')
    client.session.cookies = mock_cookie_jar

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


def test_get_playlist_info(mocker: MockerFixture, requests_mock: Mocker, mock_cookie_jar: MagicMock,
                           mock_extract_cookies_from_browser: None) -> None:
    client = YouTubeClient(browser='firefox', profile='default')
    client.session.cookies = mock_cookie_jar

    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    mocker.patch('youtube_unofficial.client.initial_data', return_value={})

    requests_mock.get(
        'https://www.youtube.com/playlist?list=test_playlist',
        text='<html></html>',
    )

    result = list(client.get_playlist_info(playlist_id='test_playlist'))
    assert result == []


def test_clear_playlist(mocker: MockerFixture) -> None:
    mock_session = mocker.Mock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    client = YouTubeClient(browser='firefox', profile='default')

    mocker.patch.object(client, 'get_playlist_info', return_value=iter([]))

    client.clear_playlist(playlist_id='test_playlist')


def test_clear_watch_later(mocker: MockerFixture) -> None:
    mock_session = mocker.Mock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    client = YouTubeClient(browser='firefox', profile='default')

    mocker.patch.object(client, 'clear_playlist')

    client.clear_watch_later()
    client.clear_playlist.assert_called_once_with('WL')


def test_remove_video_ids_from_history(mocker: MockerFixture) -> None:
    mock_session = mocker.Mock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    client = YouTubeClient(browser='firefox', profile='default')

    mocker.patch.object(client, 'get_history_info', return_value=iter([]))
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})

    result = client.remove_video_ids_from_history(video_ids=['test_video'])
    assert result is False
