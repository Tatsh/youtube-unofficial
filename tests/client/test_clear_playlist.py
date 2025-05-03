from __future__ import annotations

from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient


def test_clear_playlist_empty(mocker: MockerFixture, requests_mock: Mocker, client: YouTubeClient,
                              caplog: LogCaptureFixture, data_path: Path) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'clear-playlist/00-empty.json').read_text()))
    with caplog.at_level('INFO'):
        client.clear_playlist(playlist_id='test_playlist')
        assert 'playlist is empty.' in caplog.records[0].message


def test_clear_playlist_empty_iter(mocker: MockerFixture, requests_mock: Mocker,
                                   client: YouTubeClient, data_path: Path) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'clear-playlist/00-empty-iter.json').read_text()))
    rem_video_id = mocker.spy(client, 'remove_video_id_from_playlist')
    client.clear_playlist(playlist_id='test_playlist')
    assert rem_video_id.call_count == 0


def test_clear_playlist(mocker: MockerFixture, requests_mock: Mocker, client: YouTubeClient,
                        data_path: Path) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'clear-playlist/00.json').read_text()))
    mocker.patch.object(client, 'remove_video_id_from_playlist')
    rem_video_id = mocker.spy(client, 'remove_video_id_from_playlist')
    client.clear_playlist(playlist_id='test_playlist')
    assert rem_video_id.call_count == 2
