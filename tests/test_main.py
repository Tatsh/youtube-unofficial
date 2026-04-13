from __future__ import annotations

from typing import TYPE_CHECKING, cast

from youtube_unofficial.client import YouTubeClient
from youtube_unofficial.main import main
import niquests
import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from click.testing import CliRunner
    from pytest_mock import MockerFixture


@pytest.fixture
def mock_build_session(mocker: MockerFixture) -> None:
    mock_session = mocker.AsyncMock(spec=niquests.AsyncSession)
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    async def _build(browser: str, profile: str) -> niquests.AsyncSession:
        return cast('niquests.AsyncSession', mock_session)

    mocker.patch('youtube_unofficial.commands.build_youtube_session', side_effect=_build)


def test_main_help(runner: CliRunner, mock_build_session: None) -> None:
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert '-h, --help' in result.output


async def _yield_one_str(self: YouTubeClient, *args: object,
                         **kwargs: object) -> AsyncGenerator[str, None]:
    yield '1234'


async def _yield_one_dict(self: YouTubeClient, *args: object,
                          **kwargs: object) -> AsyncGenerator[dict[str, object], None]:
    yield {'z': 1, 'fake': 'object'}


def test_print_watch_later(mocker: MockerFixture, runner: CliRunner,
                           mock_build_session: None) -> None:
    mocker.patch.object(YouTubeClient, 'get_playlist_video_ids', _yield_one_str)
    result = runner.invoke(main, ['print-watch-later'])
    assert result.exit_code == 0
    assert '1234\n' in result.output


def test_print_watch_later_json(mocker: MockerFixture, runner: CliRunner,
                                mock_build_session: None) -> None:
    mocker.patch.object(YouTubeClient, 'get_playlist_video_ids', _yield_one_dict)
    result = runner.invoke(main, ['print-watch-later', '--json'])
    assert result.exit_code == 0
    assert '{"fake": "object", "z": 1}' in result.output


def test_print_playlist(mocker: MockerFixture, runner: CliRunner, mock_build_session: None) -> None:
    mocker.patch.object(YouTubeClient, 'get_playlist_video_ids', _yield_one_str)
    result = runner.invoke(main, ['print-playlist', '1'])
    assert result.exit_code == 0
    assert '1234\n' in result.output


def test_print_playlist_json(mocker: MockerFixture, runner: CliRunner,
                             mock_build_session: None) -> None:
    mocker.patch.object(YouTubeClient, 'get_playlist_video_ids', _yield_one_dict)
    result = runner.invoke(main, ['print-playlist', '1', '--json'])
    assert result.exit_code == 0
    assert '{"fake": "object", "z": 1}' in result.output


def test_print_history(mocker: MockerFixture, runner: CliRunner, mock_build_session: None) -> None:
    mocker.patch.object(YouTubeClient, 'get_history_video_ids', _yield_one_str)
    result = runner.invoke(main, ['print-history'])
    assert result.exit_code == 0
    assert '1234\n' in result.output


def test_print_history_json(mocker: MockerFixture, runner: CliRunner,
                            mock_build_session: None) -> None:
    mocker.patch.object(YouTubeClient, 'get_history_video_ids', _yield_one_dict)
    result = runner.invoke(main, ['print-history', '--json'])
    assert result.exit_code == 0
    assert '{"fake": "object", "z": 1}' in result.output


def test_remove_history_entries(mocker: MockerFixture, runner: CliRunner,
                                mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.remove_video_ids_from_history',
                          mocker.AsyncMock(return_value=True))
    result = runner.invoke(main, ['remove-history-entries', '1', '2'])
    assert result.exit_code == 0
    assert method.call_count == 1
    method.assert_called_once_with(['1', '2'])


def test_remove_watch_later_id(mocker: MockerFixture, runner: CliRunner,
                               mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.remove_video_id_from_playlist',
                          mocker.AsyncMock(return_value=True))
    result = runner.invoke(main, ['remove-watch-later-video-id', '1', '2'])
    assert result.exit_code == 0
    assert method.call_count == 2


def test_remove_video_id(mocker: MockerFixture, runner: CliRunner,
                         mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.remove_video_id_from_playlist',
                          mocker.AsyncMock(return_value=True))
    result = runner.invoke(main, ['remove-video-id', 'id', '1', '2'])
    assert result.exit_code == 0
    assert method.call_count == 2


def test_toggle_watch_history(mocker: MockerFixture, runner: CliRunner,
                              mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.toggle_watch_history',
                          mocker.AsyncMock(return_value=True))
    result = runner.invoke(main, ['toggle-watch-history'])
    assert result.exit_code == 0
    assert method.call_count == 1
    assert 'Watch history toggled.' in result.output


def test_toggle_watch_history_error(mocker: MockerFixture, runner: CliRunner,
                                    mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.toggle_watch_history',
                          mocker.AsyncMock(return_value=False))
    result = runner.invoke(main, ['toggle-watch-history'])
    assert result.exit_code == 1
    assert method.call_count == 1
    assert 'Failed to toggle watch history.' in result.output
    assert 'Watch history toggled.' not in result.output


def test_clear_watch_history(mocker: MockerFixture, runner: CliRunner,
                             mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.clear_watch_history',
                          mocker.AsyncMock(return_value=True))
    result = runner.invoke(main, ['clear-watch-history'])
    assert result.exit_code == 0
    assert method.call_count == 1
    assert 'Watch history cleared.' in result.output


def test_clear_watch_later(mocker: MockerFixture, runner: CliRunner,
                           mock_build_session: None) -> None:
    method = mocker.patch('youtube_unofficial.client.YouTubeClient.clear_watch_later',
                          mocker.AsyncMock(return_value=None))
    result = runner.invoke(main, ['clear-watch-later'])
    assert result.exit_code == 0
    assert method.call_count == 1
    assert 'Watch later queue cleared.' in result.output
