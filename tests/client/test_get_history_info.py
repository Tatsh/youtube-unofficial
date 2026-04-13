from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock
import json

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


@pytest.mark.anyio
async def test_get_history_info_no_continuation(mocker: MockerFixture, client: YouTubeClient,
                                                data_path: Path) -> None:
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
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    result = [item async for item in client.get_history_info()]
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


@pytest.mark.anyio
async def test_get_history_info_with_continuation(mocker: MockerFixture, client: YouTubeClient,
                                                  data_path: Path) -> None:
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
    browse_json = json.loads(
        (data_path / 'get-history-info/00-with-continuation-response.json').read_text())

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        if kwargs.get('return_json'):
            return cast('dict[str, Any]', browse_json)
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    result = [item async for item in client.get_history_info()]
    assert result == [{
        'videoRenderer': {
            'videoId': 'test_video'
        }
    }, {
        'videoRenderer': {
            'videoId': 'test_video_2'
        }
    }]


@pytest.mark.anyio
async def test_get_history_info_alt_continuation(mocker: MockerFixture, client: YouTubeClient,
                                                 data_path: Path) -> None:
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
    responses = json.loads(
        (data_path / 'get-history-info/00-alt-continuation-response.json').read_text())
    post_idx = 0

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        nonlocal post_idx
        if kwargs.get('return_json'):
            j = responses[post_idx]['json']
            post_idx += 1
            return cast('dict[str, Any]', j)
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    result = [item async for item in client.get_history_info()]
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


@pytest.mark.anyio
async def test_get_history_info_no_continuation_on_2nd_req(mocker: MockerFixture,
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
    resp_list = json.loads(
        (data_path / 'get-history-info/00-no-continuation-on-2nd-req-responses.json').read_text())
    post_idx = 0

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        nonlocal post_idx
        if kwargs.get('return_json'):
            j = resp_list[post_idx]['json']
            post_idx += 1
            return cast('dict[str, Any]', j)
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    with caplog.at_level('INFO'):
        result = [item async for item in client.get_history_info()]
        assert result == [{'videoRenderer': {'videoId': 'test_video'}}]
        assert 'end of watch history.' in caplog.records[0].message


@pytest.mark.anyio
async def test_get_history_info_bad_continuation(mocker: MockerFixture, client: YouTubeClient,
                                                 data_path: Path) -> None:
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

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        if kwargs.get('return_json'):
            return {'onResponseReceivedActions': [{'appendContinuationItemsAction': {}}]}
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    result = [item async for item in client.get_history_info()]
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


@pytest.mark.anyio
async def test_get_history_info_no_continuation_token(mocker: MockerFixture,
                                                      client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch(
        'youtube_unofficial.client.initial_data',
        return_value={
            'contents': {
                'twoColumnBrowseResultsRenderer': {
                    'tabs': [{
                        'tabRenderer': {
                            'content': {
                                'sectionListRenderer': {
                                    'contents': [],
                                    'continuations': [{
                                        'nextContinuationData': None,
                                    }],
                                },
                            },
                        },
                    }],
                },
            },
        },
    )
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    with pytest.raises(RuntimeError, match='Failed to find continuation token'):
        async for _ in client.get_history_info():
            pass


@pytest.mark.anyio
async def test_get_history_info_no_videos(mocker: MockerFixture, client: YouTubeClient,
                                          data_path: Path) -> None:
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
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    result = [item async for item in client.get_history_info()]
    assert result == []
