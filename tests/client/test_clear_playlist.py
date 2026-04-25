from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
import json

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.logging import LogCaptureFixture
    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


@pytest.mark.anyio
async def test_clear_playlist_empty(mocker: MockerFixture, client: YouTubeClient,
                                    caplog: LogCaptureFixture, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'clear-playlist/00-empty.json').read_text()))
    with caplog.at_level('INFO'):
        await client.clear_playlist(playlist_id='test_playlist')
        assert 'playlist is empty.' in caplog.records[0].message


@pytest.mark.anyio
async def test_clear_playlist_empty_iter(mocker: MockerFixture, client: YouTubeClient,
                                         data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'clear-playlist/00-empty-iter.json').read_text()))
    rem_video_id = mocker.spy(client, 'remove_video_id_from_playlist')
    await client.clear_playlist(playlist_id='test_playlist')
    assert rem_video_id.call_count == 0


@pytest.mark.anyio
async def test_clear_playlist(mocker: MockerFixture, client: YouTubeClient,
                              data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'USER_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'clear-playlist/00.json').read_text()))
    mocker.patch.object(client, 'remove_video_id_from_playlist', new_callable=AsyncMock)
    rem_video_id = mocker.spy(client, 'remove_video_id_from_playlist')
    await client.clear_playlist(playlist_id='test_playlist')
    assert rem_video_id.call_count == 2
