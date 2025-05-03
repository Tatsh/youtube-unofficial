"""Configuration for Pytest."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NoReturn, cast
import os

from click.testing import CliRunner
from youtube_unofficial.client import YouTubeClient
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
def client(mock_cookie_jar: MagicMock, mock_extract_cookies_from_browser: None) -> YouTubeClient:
    client = YouTubeClient(browser='firefox', profile='default')
    client.session.cookies = mock_cookie_jar
    return client


@pytest.fixture
def data_path() -> Path:
    return Path(__file__).parent / 'client/data'
