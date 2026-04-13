"""Tests that have no initial data."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


async def _download_html_or_json(*args: object, **kwargs: object) -> str | dict[str, str]:
    if kwargs.get('return_json'):
        return {'status': 'STATUS_SUCCEEDED'}
    return '<html></html>'


@pytest.mark.anyio
async def test_remove_video_id_from_playlist(mocker: MockerFixture, client: YouTubeClient) -> None:
    ytcfg_mock = {
        'INNERTUBE_API_KEY': 'test_api_key',
        'VISITOR_DATA': 'test_visitor_data',
        'USER_SESSION_ID': 'test_session_id',
        'SESSION_INDEX': 0,
    }
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=ytcfg_mock)
    mocker.patch('youtube_unofficial.client.context_client_body', return_value={})
    mocker.patch('youtube_unofficial.client.Soup')

    mocker.patch('youtube_unofficial.client.download_page', side_effect=_download_html_or_json)

    result = await client.remove_video_id_from_playlist(playlist_id='test_playlist',
                                                        video_id='test_video')
    assert result is True


@pytest.mark.anyio
async def test_remove_video_id_from_playlist_missing_innertube_keys(mocker: MockerFixture,
                                                                    client: YouTubeClient) -> None:
    mocker.patch(
        'youtube_unofficial.client.find_ytcfg',
        return_value={
            'VISITOR_DATA': 'test_visitor_data',
            'USER_SESSION_ID': 'test_session_id',
            'SESSION_INDEX': 0,
        },
    )
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    with pytest.raises(KeyError, match='INNERTUBE_API_KEY'):
        await client.remove_video_id_from_playlist(playlist_id='test_playlist',
                                                   video_id='test_video')


@pytest.mark.anyio
async def test_remove_video_id_from_playlist_missing_sapisid(mocker: MockerFixture,
                                                             client: YouTubeClient) -> None:
    mocker.patch(
        'youtube_unofficial.client.find_ytcfg',
        return_value={
            'INNERTUBE_API_KEY': 'test_api_key',
            'VISITOR_DATA': 'test_visitor_data',
            'USER_SESSION_ID': 'test_session_id',
            'SESSION_INDEX': 0,
        },
    )
    mocker.patch('youtube_unofficial.client.context_client_body', return_value={})
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch.object(client.session.cookies, 'get', return_value=None)
    mocker.patch('youtube_unofficial.client.download_page', side_effect=_download_html_or_json)
    with pytest.raises(RuntimeError, match='SAPISID'):
        await client.remove_video_id_from_playlist(playlist_id='test_playlist',
                                                   video_id='test_video')


async def _empty_playlist_info(*args: object, **kwargs: object) -> AsyncGenerator[Any, None]:
    return
    yield  # Required to make this an async generator.


@pytest.mark.anyio
async def test_clear_playlist(mocker: MockerFixture, client: YouTubeClient) -> None:
    mocker.patch.object(client, 'get_playlist_info', _empty_playlist_info)
    await client.clear_playlist(playlist_id='test_playlist')


@pytest.mark.anyio
async def test_clear_watch_later(mocker: MockerFixture, client: YouTubeClient) -> None:
    mocker.patch.object(client, 'clear_playlist', new_callable=AsyncMock)
    await client.clear_watch_later()
    client.clear_playlist.assert_called_once_with(  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
        'WL')


async def _empty_history_info(*args: object, **kwargs: object) -> AsyncGenerator[Any, None]:
    return
    yield  # Required to make this an async generator.


@pytest.mark.anyio
async def test_remove_video_ids_from_history_no_entries(mocker: MockerFixture,
                                                        client: YouTubeClient) -> None:
    mocker.patch.object(client, 'get_history_info', _empty_history_info)
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    result = await client.remove_video_ids_from_history(video_ids=['test_video'])
    assert result is False


@pytest.mark.anyio
async def test_remove_video_ids_from_history_empty(mocker: MockerFixture,
                                                   client: YouTubeClient) -> None:
    result = await client.remove_video_ids_from_history([])
    assert result is False


@pytest.mark.anyio
async def test_remove_video_from_playlist_cached(mocker: MockerFixture,
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

    mock_dl = mocker.patch('youtube_unofficial.client.download_page',
                           side_effect=_download_html_or_json)

    result = await client.remove_video_id_from_playlist('test_playlist',
                                                        'test_video',
                                                        cache_values=True)
    assert result is True
    result = await client.remove_video_id_from_playlist('test_playlist',
                                                        'test_video',
                                                        cache_values=True)
    assert result is True
    assert mock_dl.call_count == 3


@pytest.mark.anyio
async def test_remove_set_video_id_from_playlist(mocker: MockerFixture,
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

    mocker.patch('youtube_unofficial.client.download_page', side_effect=_download_html_or_json)

    result = await client.remove_set_video_id_from_playlist('test_playlist', 'test_video')
    assert result is True


@pytest.mark.anyio
async def test_remove_set_video_id_from_playlist_cached(mocker: MockerFixture,
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

    mock_dl = mocker.patch('youtube_unofficial.client.download_page',
                           side_effect=_download_html_or_json)

    result = await client.remove_set_video_id_from_playlist('test_playlist',
                                                            'test_video',
                                                            cache_values=True)
    assert result is True
    result = await client.remove_set_video_id_from_playlist('test_playlist',
                                                            'test_video',
                                                            cache_values=True)
    assert result is True
    assert mock_dl.call_count == 3
