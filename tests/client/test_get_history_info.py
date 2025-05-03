from __future__ import annotations

from typing import TYPE_CHECKING
import json

from youtube_unofficial.constants import WATCH_HISTORY_URL

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient


def test_get_history_info_no_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                          client: YouTubeClient, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-info/00-no-continuation.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    result = list(client.get_history_info())
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


def test_get_history_info_with_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                            client: YouTubeClient, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-info/00-with-continuation.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse',
        json=json.loads(
            (data_path / 'get-history-info/00-with-continuation-response.json').read_text()))
    result = list(client.get_history_info())
    assert result == [{
        'videoRenderer': {
            'videoId': 'test_video'
        }
    }, {
        'videoRenderer': {
            'videoId': 'test_video_2'
        }
    }]


def test_get_history_info_alt_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                           client: YouTubeClient, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-info/00-alt-continuation.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse',
        response_list=json.loads(
            (data_path / 'get-history-info/00-alt-continuation-response.json').read_text()))
    result = list(client.get_history_info())
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


def test_get_history_info_no_continuation_on_2nd_req(mocker: MockerFixture, requests_mock: Mocker,
                                                     client: YouTubeClient,
                                                     caplog: LogCaptureFixture,
                                                     data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch(
        'youtube_unofficial.client.initial_data',
        return_value=json.loads(
            (data_path / 'get-history-info/00-no-continuation-on-2nd-req.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/browse',
        response_list=json.loads(
            (data_path /
             'get-history-info/00-no-continuation-on-2nd-req-responses.json').read_text()))
    with caplog.at_level('INFO'):
        result = list(client.get_history_info())
        assert result == [{'videoRenderer': {'videoId': 'test_video'}}]
        assert 'end of watch history.' in caplog.records[0].message


def test_get_history_info_bad_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                           client: YouTubeClient, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-info/00-bad-continuation.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/browse',
                       json={'onResponseReceivedActions': [{
                           'appendContinuationItemsAction': {}
                       }]})
    result = list(client.get_history_info())
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


def test_get_history_info_no_videos(mocker: MockerFixture, requests_mock: Mocker,
                                    client: YouTubeClient, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-info/00-no-videos.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    result = list(client.get_history_info())
    assert result == []
