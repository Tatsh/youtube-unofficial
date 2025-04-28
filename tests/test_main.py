from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.main import main

if TYPE_CHECKING:
    from click.testing import CliRunner


def test_main_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert '-h, --help' in result.output
