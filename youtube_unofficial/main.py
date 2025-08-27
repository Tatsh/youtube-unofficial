"""Entry point for the CLI."""
from __future__ import annotations

import click

from .commands import (
    clear_watch_history,
    clear_watch_later,
    print_history,
    print_playlist,
    print_watch_later,
    remove_history_entries,
    remove_video_id,
    remove_watch_later_video_id,
    toggle_watch_history,
)


@click.group(context_settings={'help_option_names': ('-h', '--help')})
def main() -> None:
    """Unofficial YouTube CLI."""


main.add_command(clear_watch_history)
main.add_command(clear_watch_later)
main.add_command(print_history)
main.add_command(print_playlist)
main.add_command(print_watch_later)
main.add_command(remove_history_entries)
main.add_command(remove_video_id)
main.add_command(remove_watch_later_video_id)
main.add_command(toggle_watch_history)
