"""Configuration for Pytest."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn, cast
import os

from click.testing import CliRunner
from youtube_unofficial.client import YouTubeClient
import niquests
import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

if os.getenv('_PYTEST_RAISE', '0') != '0':  # pragma no cover

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[None]) -> NoReturn:
        assert call.excinfo is not None
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[BaseException]) -> NoReturn:
        raise excinfo.value


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_cookie_jar(mocker: MockerFixture) -> MagicMock:
    mock_jar = mocker.MagicMock()
    mock_jar.get.return_value = 'test_cookie'
    return cast('MagicMock', mock_jar)


@pytest.fixture
def mock_extract_cookies_from_browser(mocker: MockerFixture) -> None:
    mock_jar = mocker.MagicMock()
    mocker.patch('yt_dlp_utils.lib.extract_cookies_from_browser', return_value=mock_jar)


@pytest.fixture
def client(mock_cookie_jar: MagicMock, mock_extract_cookies_from_browser: None,
           mocker: MockerFixture) -> YouTubeClient:
    mock_session = mocker.AsyncMock(spec=niquests.AsyncSession)
    mock_session.cookies = mock_cookie_jar
    return YouTubeClient(mock_session)


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / 'client/data'


def make_niquests_response(mocker: MockerFixture,
                           *,
                           text: str = '',
                           json_data: dict[str, Any] | None = None,
                           status_code: int = 200) -> MagicMock:
    r = mocker.MagicMock()
    r.text = text.strip() if text else ''
    r.json = mocker.MagicMock(return_value=json_data if json_data is not None else {})
    r.raise_for_status = mocker.MagicMock()
    r.status_code = status_code
    return cast('MagicMock', r)
