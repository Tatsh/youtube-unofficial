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
async def test_get_playlist_video_ids(mocker: MockerFixture, client: YouTubeClient,
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
                     (data_path / 'get-playlist-video-ids/20-video-ids.json').read_text()))
    result: list[str] = [vid async for vid in client.get_playlist_video_ids('test_playlist')]
    assert result == ['test_video_id']


@pytest.mark.anyio
async def test_get_playlist_video_ids_dict(mocker: MockerFixture, client: YouTubeClient,
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
                     (data_path / 'get-playlist-video-ids/20-video-ids-dict.json').read_text()))
    result = [
        entry async for entry in client.get_playlist_video_ids('test_playlist', return_dict=True)
    ]
    assert result == [{
        'owner': 'test_channel_name',
        'title': 'test_video_title',
        'video_id': 'test_video_id',
        'watch_url': 'https://www.youtube.com/watch?v=test_video_id'
    }, {
        'owner': 'test_channel_name',
        'title': 'test_video_title',
        'video_id': 'test_video_id',
        'watch_url': 'https://www.youtube.com/watch?v=test_video_id'
    }, {
        'owner': None,
        'title': None,
        'video_id': 'test_video_id',
        'watch_url': 'https://www.youtube.com/watch?v=test_video_id'
    }]
