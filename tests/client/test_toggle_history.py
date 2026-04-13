from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
import json

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


@pytest.mark.anyio
async def test_toggle_history(mocker: MockerFixture, client: YouTubeClient,
                              data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'toggle-history-00.json').read_text()))

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        if kwargs.get('return_json'):
            return cast('dict[str, Any]', {'feedbackResponses': [{'isProcessed': True}]})
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    result = await client.toggle_watch_history()
    assert result is True
