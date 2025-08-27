"""Commands."""
from __future__ import annotations

from typing import TYPE_CHECKING
import json
import logging

from bascom import setup_logging
import click

from . import YouTubeClient

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = ('clear_watch_history', 'clear_watch_later', 'print_history', 'print_playlist',
           'print_watch_later', 'remove_history_entries', 'remove_video_id',
           'remove_watch_later_video_id', 'toggle_watch_history')


def print_playlist_ids_callback(browser: str,
                                profile: str,
                                playlist_id: str,
                                *,
                                output_json: bool = False) -> None:
    yt = YouTubeClient(browser, profile)
    for entry in yt.get_playlist_video_ids(playlist_id,
                                           return_dict=output_json):  # type: ignore[call-overload]
        if output_json:
            click.echo(json.dumps(entry, sort_keys=True))
        else:
            click.echo(entry)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.option('-j', '--json', 'output_json', is_flag=True, help='Output in JSON format.')
def print_watch_later(browser: str,
                      profile: str,
                      *,
                      debug: bool = False,
                      output_json: bool = False) -> None:
    """
    Print your Watch Later playlist.

    By default, this will print the video IDs of your Watch Later playlist.

    If -j/--json is specified, this will print a JSON object for each video in your Watch Later
    playlist. The JSON object will have the following interface:

    \b

    .. code-block:: typescript

       {
           owner: string
           title: string
           video_id: string
           watch_url: string
       }
    """  # noqa: D301
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    print_playlist_ids_callback(browser, profile, 'WL', output_json=output_json)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.option('-j', '--json', 'output_json', is_flag=True, help='Output in JSON format.')
@click.argument('playlist_id')
def print_playlist(browser: str,
                   profile: str,
                   playlist_id: str,
                   *,
                   debug: bool = False,
                   output_json: bool = False) -> None:
    """
    Print a playlist.

    By default, this will print the video IDs of the given playlist ID.

    If -j/--json is specified, this will print a JSON object for each video in your Watch Later
    playlist. The JSON object will have the following interface:

    \b

    .. code-block:: typescript

       {
           owner: string
           title: string
           video_id: string
           watch_url: string
       }
    """  # noqa: D301
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    print_playlist_ids_callback(browser, profile, playlist_id, output_json=output_json)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.option('-j', '--json', 'output_json', is_flag=True, help='Output in JSON format.')
def print_history(browser: str,
                  profile: str,
                  *,
                  debug: bool = False,
                  output_json: bool = False) -> None:
    """Print your watch history.

    By default, this will print the video IDs of your watch history.

    If -j/--json is specified, this will print a JSON object for each video in your watch
    history. The JSON object will have the following interface:

    \b

    .. code-block:: typescript

       {
           channel_thumbnails: {
               height: int
               width: int
               url: string
           }[]
           description: string
           length: string
           length_accessible: string
           long_byline_text: string
           moving_thumbnails: {
               height: int
               width: int
               url: string
           }[]
           owner_text: string
           short_byline_text: string
           short_view_count_text: string
           title: string
           video_id: string
           video_thumbnails: {
               height: int
               width: int
               url: string
           }[]
        }
    """  # noqa: D301
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    yt = YouTubeClient(browser, profile)
    for entry in yt.get_history_video_ids(return_dict=output_json):  # type: ignore[call-overload]
        if output_json:
            click.echo(json.dumps(entry, sort_keys=True))
        else:
            click.echo(entry)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.argument('video_ids', nargs=-1)
def remove_history_entries(browser: str,
                           profile: str,
                           video_ids: tuple[str, ...],
                           *,
                           debug: bool = False) -> None:
    """Remove videos from Watch History."""
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    yt = YouTubeClient(browser, profile)
    for video_id in video_ids:
        yt.remove_video_ids_from_history(video_id)


def remove_svi_callback(browser: str, profile: str, playlist_id: str,
                        video_ids: Iterable[str]) -> None:
    yt = YouTubeClient(browser, profile)
    for svi in video_ids:
        yt.remove_video_id_from_playlist(playlist_id, svi)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.argument('video_ids', nargs=-1)
def remove_watch_later_video_id(browser: str,
                                profile: str,
                                video_ids: tuple[str, ...],
                                *,
                                debug: bool = False) -> None:
    """Remove videos from your Watch Later queue."""
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    remove_svi_callback(browser, profile, 'WL', video_ids)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.argument('playlist_id', nargs=1)
@click.argument('video_ids', nargs=-1)
def remove_video_id(browser: str,
                    profile: str,
                    playlist_id: str,
                    video_ids: tuple[str, ...],
                    *,
                    debug: bool = False) -> None:
    """Remove videos from a playlist."""
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    remove_svi_callback(browser, profile, playlist_id, video_ids)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
def toggle_watch_history(browser: str, profile: str, *, debug: bool = False) -> None:
    """Disable or enable watch history."""  # noqa: DOC501
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    if not YouTubeClient(browser=browser, profile=profile).toggle_watch_history():
        click.echo('Failed to toggle watch history.', err=True)
        raise click.Abort
    click.echo('Watch history toggled.')


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
def clear_watch_history(browser: str, profile: str, *, debug: bool = False) -> None:
    """Clear watch history."""
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    yt = YouTubeClient(browser, profile)
    yt.clear_watch_history()
    click.echo('Watch history cleared.')


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
def clear_watch_later(browser: str, profile: str, *, debug: bool = False) -> None:
    """Clear watch later queue."""
    setup_logging(debug=debug,
                  loggers={
                      'youtube_unofficial': {
                          'handlers': ('console',),
                          'level': logging.DEBUG if debug else logging.INFO,
                          'propagate': False,
                      }
                  })
    yt = YouTubeClient(browser, profile)
    yt.clear_watch_later()
    click.echo('Watch later queue cleared.')
