from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
import json

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


@pytest.mark.anyio
async def test_response_indicates_logged_out(mocker: MockerFixture, client: YouTubeClient,
                                             data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'response-logged-out-00.json').read_text()))

    async def fake_dl(*args: Any, **kwargs: Any) -> str | dict[str, Any]:
        if kwargs.get('return_json'):
            return cast('dict[str, Any]',
                        {'responseContext': {
                            'mainAppWebResponseContext': {
                                'loggedOut': True
                            }
                        }})
        return '<html></html>'

    mocker.patch('youtube_unofficial.client.download_page', side_effect=fake_dl)
    with pytest.raises(RuntimeError, match=r'logged out'):
        await client.remove_video_ids_from_history(['test_video'])
