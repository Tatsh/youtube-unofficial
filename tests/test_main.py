from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.main import main

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_main_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert '-h, --help' in result.output


def test_main_commands(runner: CliRunner, mocker: MockerFixture) -> None:
    mock_clear_watch_history = mocker.patch('youtube_unofficial.main.clear_watch_history')
    mock_clear_watch_later = mocker.patch('youtube_unofficial.main.clear_watch_later')
    mock_print_history = mocker.patch('youtube_unofficial.main.print_history')
    mock_print_playlist = mocker.patch('youtube_unofficial.main.print_playlist')
    mock_print_watch_later = mocker.patch('youtube_unofficial.main.print_watch_later')
    mock_remove_history_entries = mocker.patch('youtube_unofficial.main.remove_history_entries')
    mock_remove_video_id = mocker.patch('youtube_unofficial.main.remove_video_id')
    mock_remove_watch_later_video_id = mocker.patch(
        'youtube_unofficial.main.remove_watch_later_video_id')
    mock_toggle_watch_history = mocker.patch('youtube_unofficial.main.toggle_watch_history')

    commands = [
        ('clear-watch-history', mock_clear_watch_history),
        ('clear-watch-later', mock_clear_watch_later),
        ('print-history', mock_print_history),
        ('print-playlist', mock_print_playlist),
        ('print-watch-later', mock_print_watch_later),
        ('remove-history-entries', mock_remove_history_entries),
        ('remove-video-id', mock_remove_video_id),
        ('remove-watch-later-video-id', mock_remove_watch_later_video_id),
        ('toggle-watch-history', mock_toggle_watch_history),
    ]

    for command, mock_func in commands:
        result = runner.invoke(main, [command])
        assert result.exit_code == 0
        mock_func.assert_called_once()
