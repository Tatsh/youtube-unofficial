"""Tests that have no initial data."""
from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.constants import WATCH_LATER_URL

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient


def test_remove_video_id_from_playlist(mocker: MockerFixture, requests_mock: Mocker,
                                       client: YouTubeClient) -> None:
    ytcfg_mock = {
        'INNERTUBE_API_KEY': 'test_api_key',
        'VISITOR_DATA': 'test_visitor_data',
        'USER_SESSION_ID': 'test_session_id',
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


def test_remove_video_ids_from_history_no_entries(mocker: MockerFixture,
                                                  client: YouTubeClient) -> None:
    mock_session = mocker.MagicMock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
    mocker.patch.object(client, 'get_history_info', return_value=iter([]))
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    result = client.remove_video_ids_from_history(video_ids=['test_video'])
    assert result is False


def test_remove_video_ids_from_history_empty(mocker: MockerFixture, requests_mock: Mocker,
                                             client: YouTubeClient) -> None:
    result = client.remove_video_ids_from_history([])
    assert result is False


def test_remove_video_from_playlist_cached(mocker: MockerFixture, requests_mock: Mocker,
                                           client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.context_client_body', return_value={})
    mocker.patch('youtube_unofficial.client.Soup')

    requests_mock.get(WATCH_LATER_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse/edit_playlist',
        json={'status': 'STATUS_SUCCEEDED'},
    )

    result = client.remove_video_id_from_playlist('test_playlist', 'test_video', cache_values=True)
    assert result is True
    result = client.remove_video_id_from_playlist('test_playlist', 'test_video', cache_values=True)
    assert result is True
    assert len(requests_mock.request_history) == 3


def test_remove_set_video_id_from_playlist(mocker: MockerFixture, requests_mock: Mocker,
                                           client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.context_client_body', return_value={})
    mocker.patch('youtube_unofficial.client.Soup')

    requests_mock.get(WATCH_LATER_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse/edit_playlist',
        json={'status': 'STATUS_SUCCEEDED'},
    )

    result = client.remove_set_video_id_from_playlist('test_playlist', 'test_video')
    assert result is True


def test_remove_set_video_id_from_playlist_cached(mocker: MockerFixture, requests_mock: Mocker,
                                                  client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.context_client_body', return_value={})
    mocker.patch('youtube_unofficial.client.Soup')

    requests_mock.get(WATCH_LATER_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse/edit_playlist',
        json={'status': 'STATUS_SUCCEEDED'},
    )

    result = client.remove_set_video_id_from_playlist('test_playlist',
                                                      'test_video',
                                                      cache_values=True)
    assert result is True
    result = client.remove_set_video_id_from_playlist('test_playlist',
                                                      'test_video',
                                                      cache_values=True)
    assert result is True
    assert len(requests_mock.request_history) == 3
