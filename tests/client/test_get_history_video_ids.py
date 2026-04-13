from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
import json

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


@pytest.mark.anyio
async def test_get_history_video_ids(mocker: MockerFixture, client: YouTubeClient,
                                     data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'get-history-video-ids/00.json').read_text()))
    result = [x async for x in client.get_history_video_ids(return_dict=True)]
    assert result == [{
        'video_id': 'test_video_id',
        'title': 'Test Title',
        'owner_text': 'Test Owner',
        'short_byline_text': 'Test Channel',
        'length': '5:00',
        'length_accessible': '5 minutes',
        'verified': True,
        'short_view_count_text': '10 views',
        'moving_thumbnails': [{
            'height': 100,
            'url': 'https://example.com/thumbnail.jpg',
            'width': 100
        }],
        'video_thumbnails': [{
            'height': 100,
            'url': 'https://example.com/thumbnail.jpg',
            'width': 100
        }, {
            'height': 320,
            'width': 180,
            'url': 'test_thumbnail_url',
        }],
        'random': 1,
        'watch_url': 'https://www.youtube.com/watch?v=test_video_id',
    }, {
        'video_id': 'test_video_id',
        'title': 'Test Title',
        'owner_text': 'Test Owner',
        'short_byline_text': 'Test Channel',
        'length': '5:00',
        'length_accessible': '5 minutes',
        'verified': False,
        'short_view_count_text': '10 views',
        'moving_thumbnails': [{
            'height': 100,
            'url': 'https://example.com/thumbnail.jpg',
            'width': 100
        }],
        'video_thumbnails': [{
            'height': 100,
            'url': 'https://example.com/thumbnail.jpg',
            'width': 100
        }, {
            'height': 320,
            'width': 180,
            'url': 'test_thumbnail_url',
        }],
        'random': 1,
        'watch_url': 'https://www.youtube.com/watch?v=test_video_id',
    }]


@pytest.mark.anyio
async def test_get_history_video_ids_strings(mocker: MockerFixture, client: YouTubeClient,
                                             data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-video-ids/00-strings.json').read_text()))
    result = [x async for x in client.get_history_video_ids()]
    assert result == ['test_video_id', 'test_video_id']


@pytest.mark.anyio
async def test_get_history_video_ids_empty(mocker: MockerFixture, client: YouTubeClient,
                                           data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-video-ids/00-empty.json').read_text()))
    result = [x async for x in client.get_history_video_ids(return_dict=False)]
    assert result == []


@pytest.mark.anyio
async def test_get_history_video_ids_missing_video_id(mocker: MockerFixture, client: YouTubeClient,
                                                      data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-video-ids/00-missing-video-id.json').read_text()))
    result = [x async for x in client.get_history_video_ids(return_dict=False)]
    assert result == []


@pytest.mark.anyio
async def test_get_history_video_ids_bad_video_id_type(mocker: MockerFixture, client: YouTubeClient,
                                                       data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'get-history-video-ids/00-bad-video-id-type.json').read_text()))
    with pytest.raises(TypeError, match='Expected string video ID'):
        async for _ in client.get_history_video_ids(return_dict=True):
            pass
