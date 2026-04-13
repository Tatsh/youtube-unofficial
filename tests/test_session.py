from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.constants import USER_AGENT
from youtube_unofficial.session import build_youtube_session
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.anyio
async def test_build_youtube_session(mocker: MockerFixture) -> None:
    mock_sync_session = mocker.MagicMock()
    mock_sync_session.cookies = {'sid': 'val'}
    mocker.patch('youtube_unofficial.session.yt_dlp_utils.setup_session',
                 return_value=mock_sync_session)
    mock_cached = mocker.MagicMock()
    mock_cached.cookies = mocker.MagicMock()
    mock_cached.headers = {}
    mocker.patch('youtube_unofficial.session.cached_session', return_value=mock_cached)
    session = await build_youtube_session('chrome', 'Default')
    assert session is mock_cached
    assert session.headers['User-Agent'] == USER_AGENT
    mock_sync_session.close.assert_called_once()
