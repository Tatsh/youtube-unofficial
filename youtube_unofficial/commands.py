from __future__ import annotations

from operator import itemgetter
from typing import TYPE_CHECKING, Any
import json
import logging

from benedict import benedict
import click

from . import YouTubeClient
from .constants import (
    EXTRACTED_THUMBNAIL_KEYS,
    HISTORY_ENTRY_KEYS_TO_SKIP,
    SIMPLE_TEXT_KEYS,
    TEXT_RUNS_KEYS,
    THUMBNAILS_KEYS,
)
from .utils import extract_keys, get_text_runs

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .typing.history import MetadataBadgeRendererTopDict

__all__ = ('clear_watch_history', 'clear_watch_later', 'print_history', 'print_playlist',
           'print_watch_later', 'remove_history_entries', 'remove_video_id',
           'remove_watch_later_video_id', 'toggle_watch_history')


def print_playlist_ids_callback(browser: str,
                                profile: str,
                                playlist_id: str,
                                *,
                                output_json: bool = False) -> None:
    yt = YouTubeClient(browser, profile)
    for item in yt.get_playlist_info(playlist_id):
        renderer = item['playlistVideoRenderer']
        if 'videoId' not in renderer:
            continue
        owner = title = None
        if 'shortBylineText' in renderer:
            if 'runs' in renderer['shortBylineText']:
                owner = ' - '.join(map(itemgetter('text'), renderer['shortBylineText']['runs']))
            elif 'text' in renderer['shortBylineText']:
                owner = renderer['shortBylineText']['text']
        if 'title' in renderer:
            if 'simpleText' in renderer['title']:
                title = renderer['title']['simpleText']
            elif 'runs' in renderer['title']:
                title = ' - '.join(map(itemgetter('text'), renderer['title']['runs']))
        if output_json:
            click.echo(
                json.dumps({
                    'owner': owner,
                    'title': title,
                    'video_id': renderer['videoId'],
                    'watch_url': f'https://www.youtube.com/watch?v={renderer["videoId"]}'
                }))
        else:
            click.echo(renderer['videoId'])


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.option('-j', '--json', 'output_json', is_flag=True, help='Output in JSON format')
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
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    print_playlist_ids_callback(browser, profile, 'WL', output_json=output_json)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.option('-j', '--json', 'output_json', is_flag=True, help='Output in JSON format')
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
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.option('-j', '--json', 'output_json', is_flag=True, help='Output in JSON format')
def print_history(browser: str,
                  profile: str,
                  *,
                  debug: bool = False,
                  output_json: bool = False) -> int:
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
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')

    def is_verified(owner_badges: Iterable[MetadataBadgeRendererTopDict]) -> bool:
        for badge in (x['metadataBadgeRenderer'] for x in owner_badges):
            if badge['style'] == 'BADGE_STYLE_TYPE_VERIFIED':
                return True
        return False

    yt = YouTubeClient(browser, profile)
    if output_json:
        for entry in yt.get_history_info():
            d: dict[str, Any] = {}
            if 'videoId' not in entry.get('videoRenderer', {}):
                continue
            for k, v in sorted(entry.get('videoRenderer', {}).items()):
                if k in HISTORY_ENTRY_KEYS_TO_SKIP:
                    continue
                if k == 'videoId':
                    d['video_id'] = v
                elif isinstance(v, int | str | float | bool):
                    d[k] = v
                elif k in TEXT_RUNS_KEYS:
                    d[TEXT_RUNS_KEYS[k]] = get_text_runs(v)
                elif k in THUMBNAILS_KEYS:
                    list_path = THUMBNAILS_KEYS[k][0]
                    target_key = THUMBNAILS_KEYS[k][1]
                    for thumb in benedict(v)[list_path]:
                        try:
                            d[target_key].append(extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb))
                        except KeyError:  # noqa: PERF203
                            d[target_key] = [extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb)]
                elif k in SIMPLE_TEXT_KEYS:
                    d[SIMPLE_TEXT_KEYS[k]] = v['simpleText']
                elif k == 'lengthText':
                    d['length_accessible'] = benedict(v)['accessibility.accessibilityData.label']
                    d['length'] = v['simpleText']
                elif k == 'ownerBadges':
                    d['verified'] = is_verified(v)
                elif k == 'thumbnail':
                    for thumb in v['thumbnails']:
                        try:
                            d['video_thumbnails'].append(
                                extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb))
                        except KeyError:  # noqa: PERF203
                            d['video_thumbnails'] = [extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb)]
            d['watch_url'] = f'https://www.youtube.com/watch?v={d["video_id"]}'
            click.echo(json.dumps(d, sort_keys=True))
    else:
        for entry in yt.get_history_info():
            click.echo(entry['videoRenderer']['videoId'])
    return 0


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.argument('video_ids', nargs=-1)
def remove_history_entries(browser: str,
                           profile: str,
                           video_ids: tuple[str, ...],
                           *,
                           debug: bool = False) -> None:
    """Remove videos from Watch History."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    yt = YouTubeClient(browser, profile)
    for video_id in video_ids:
        yt.remove_video_ids_from_history(video_id)


def remove_svi_callback(browser: str, profile: str, playlist_id: str,
                        video_ids: Iterable[str]) -> None:
    yt = YouTubeClient(browser, profile)
    for svi in video_ids:
        yt.remove_video_id_from_playlist(playlist_id, svi)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
@click.argument('video_ids', nargs=-1)
def remove_watch_later_video_id(browser: str,
                                profile: str,
                                video_ids: tuple[str, ...],
                                *,
                                debug: bool = False) -> None:
    """Remove videos from your Watch Later queue."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    remove_svi_callback(browser, profile, 'WL', video_ids)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
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
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    remove_svi_callback(browser, profile, playlist_id, video_ids)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
def toggle_watch_history(browser: str, profile: str, *, debug: bool = False) -> None:
    """Disable or enable watch history."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    if not YouTubeClient(browser=browser, profile=profile).toggle_watch_history():
        click.echo('Failed to toggle watch history.', err=True)
        raise click.Abort
    click.echo('Watch history toggled.')


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
def clear_watch_history(browser: str, profile: str, *, debug: bool = False) -> None:
    """Clear watch history."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    yt = YouTubeClient(browser, profile)
    yt.clear_watch_history()
    click.echo('Watch history cleared.')


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug output')
@click.option('-b', '--browser', default='chrome', help='Browser to read cookies from.')
@click.option('-p', '--profile', default='Default', help='Browser profile.')
def clear_watch_later(browser: str, profile: str, *, debug: bool = False) -> None:
    """Clear watch later queue."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    yt = YouTubeClient(browser, profile)
    yt.clear_watch_later()
    click.echo('Watch later queue cleared.')
