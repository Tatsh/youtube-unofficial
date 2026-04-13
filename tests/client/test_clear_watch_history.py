from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock
import json

from youtube_unofficial.client import NoFeedbackToken, YouTubeClient
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


async def _fake_dl_with_json(json_data: dict[str, Any]) -> Any:
    async def _inner(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        if kwargs.get('return_json'):
            return json_data
        return '<html></html>'

    return _inner


@pytest.mark.anyio
async def test_clear_watch_history_no_feedback_token(mocker: MockerFixture,
                                                     client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {}
                             }
                         }
                     }
                 })
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    with pytest.raises(NoFeedbackToken):
        await client.clear_watch_history()


@pytest.mark.anyio
async def test_clear_watch_history_clear_button_disabled(mocker: MockerFixture,
                                                         client: YouTubeClient,
                                                         data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads(
                     (data_path / 'clear-watch-history/00-button-disabled.json').read_text()))
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    assert await client.clear_watch_history() is False


@pytest.mark.anyio
async def test_clear_watch_history(mocker: MockerFixture, client: YouTubeClient,
                                   data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'clear-watch-history/00.json').read_text()))

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        if kwargs.get('return_json'):
            return cast('dict[str, Any]', {'feedbackResponses': [{'isProcessed': True}]})
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    assert await client.clear_watch_history() is True


@pytest.mark.anyio
async def test_clear_watch_history_missing_session_ytcfg(mocker: MockerFixture,
                                                         client: YouTubeClient,
                                                         data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch(
        'youtube_unofficial.client.find_ytcfg',
        return_value={
            'INNERTUBE_API_KEY': 'test_api_key',
            'VISITOR_DATA': 'test_visitor_data',
        },
    )
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'clear-watch-history/00.json').read_text()))
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    with pytest.raises(KeyError, match='DELEGATED_SESSION_ID'):
        await client.clear_watch_history()
