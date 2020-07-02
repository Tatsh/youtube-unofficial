# pylint: disable=broad-except
from operator import itemgetter
from os.path import expanduser
from typing import Any, Callable, Dict, Mapping, Optional, Sequence
import argparse
import json
import logging
import sys

from . import YouTube
from .constants import (EXTRACTED_THUMBNAIL_KEYS, HISTORY_ENTRY_KEYS_TO_SKIP,
                        SIMPLE_TEXT_KEYS, TEXT_RUNS_KEYS, THUMBNAILS_KEYS)
from .typing.history import MetadataBadgeRendererTopDict
from .util import extract_keys, get_text_runs, path

__all__ = (
    'clear_favorites',
    'clear_watch_history',
    'clear_watch_later',
    'print_history_ids',
    'print_playlist_ids',
    'print_watchlater_ids',
    'remove_history_entry',
    'remove_setvideoid',
    'remove_watchlater_setvideoid',
    'toggle_search_history',
)


def _common_arguments(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u',
                        '--username',
                        help='If not specified, a netrc file will be used')
    parser.add_argument('-p',
                        '--password',
                        help='If not specified, a netrc file will be used')
    parser.add_argument('--netrc',
                        default=expanduser('~/.netrc'),
                        help='A netrc file to use')
    parser.add_argument('--cookies',
                        default=expanduser('~/.ytch-cookies.txt'),
                        help='Netscape cookies file to use')
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help='Log and raise exceptions')
    return parser


def _parse_common_arguments(args: argparse.Namespace) -> Mapping[str, Any]:
    kwargs = {}
    if args.username:
        kwargs['username'] = args.username
        kwargs['password'] = args.password
    elif args.netrc:
        kwargs['netrc_file'] = args.netrc
    if args.cookies:
        kwargs['cookies_path'] = args.cookies
    if args.debug:
        channel = logging.StreamHandler()
        channel.setLevel(logging.DEBUG)
        channel.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s'))
        for logname in ('youtube-unofficial', 'requests', 'urllib3'):
            log = logging.getLogger(logname)
            log.setLevel(logging.DEBUG)
            log.addHandler(channel)
    return kwargs


def _simple_method_call(method_name: str,
                        description: str) -> Callable[..., int]:
    def f() -> int:
        parser = _common_arguments(description)
        args = parser.parse_args()
        kwargs = _parse_common_arguments(args)

        yt = YouTube(**kwargs)
        try:
            yt.login()
            getattr(yt, method_name)()
        except Exception as e:
            if args.debug:
                raise e
            print(str(e), file=sys.stderr)
            return 1
        return 0

    return f


def print_playlist_ids_callback(
    parser: Optional[argparse.ArgumentParser] = None,  # pylint: disable=unused-argument
    playlist_id: Optional[str] = None
) -> Callable[..., int]:
    def f() -> int:
        nonlocal parser
        if not parser:
            parser = _common_arguments('Print playlist video IDs/information')
        parser.add_argument('-j', '--json', action='store_true')
        args = parser.parse_args()
        kwargs = _parse_common_arguments(args)
        yt = YouTube(**kwargs)
        try:
            yt.login()
        except Exception as e:
            if args.debug:
                raise e
            print(str(e), file=sys.stderr)
            return 1
        for item in yt.get_playlist_info(playlist_id or args.playlist_id):
            renderer = item['playlistVideoRenderer']
            owner = title = None
            if 'shortBylineText' in renderer:
                if 'runs' in renderer['shortBylineText']:
                    owner = ' - '.join(
                        map(itemgetter('text'),
                            renderer['shortBylineText']['runs']))
                elif 'text' in renderer['shortBylineText']:
                    owner = renderer['shortBylineText']['text']
            if 'title' in renderer:
                if 'simpleText' in renderer['title']:
                    title = renderer['title']['simpleText']
                elif 'runs' in 'title':
                    title = ' - '.join(
                        map(itemgetter('text'), renderer['title']['runs']))
            if args.json:
                print(
                    json.dumps({
                        'owner':
                        owner,
                        'title':
                        title,
                        'setVideoId':
                        renderer['setVideoId']
                        if 'setVideoId' in renderer else None,
                        'videoId':
                        renderer['videoId']
                    }))
            else:
                print('{} {}'.format(renderer['videoId'],
                                     renderer['setVideoId']))
        return 0

    return f


def print_watchlater_ids() -> int:
    return print_playlist_ids_callback(playlist_id='WL')()


def print_playlist_ids() -> int:
    parser = _common_arguments('Print playlist video IDs/information')
    parser.add_argument('playlist_id')
    return print_playlist_ids_callback(parser=parser)()


def print_history_ids() -> int:
    def is_verified(
            owner_badges: Sequence[MetadataBadgeRendererTopDict]) -> bool:
        for badge in (x['metadataBadgeRenderer'] for x in owner_badges):
            if badge['style'] == 'BADGE_STYLE_TYPE_VERIFIED':
                return True
        return False

    parser = _common_arguments('Print Watch History video IDs/information')
    parser.add_argument('-j', '--json', action='store_true')
    args = parser.parse_args()
    kwargs = _parse_common_arguments(args)
    yt = YouTube(**kwargs)
    try:
        yt.login()
    except Exception as e:
        if args.debug:
            raise e
        print(str(e), file=sys.stderr)
        return 1
    if args.json:
        for entry in yt.get_history_info():
            d: Dict[str, Any] = {}
            for k, v in sorted(entry['videoRenderer'].items()):
                if k in HISTORY_ENTRY_KEYS_TO_SKIP:
                    continue
                if isinstance(v, (int, str, float, bool)):
                    d[k] = v
                elif k in TEXT_RUNS_KEYS:
                    d[TEXT_RUNS_KEYS[k]] = get_text_runs(v)
                elif k in THUMBNAILS_KEYS:
                    list_path = THUMBNAILS_KEYS[k][0]
                    target_key = THUMBNAILS_KEYS[k][1]
                    for thumb in path(list_path, v):
                        try:
                            d[target_key].append(
                                extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb))
                        except KeyError:
                            d[target_key] = [
                                extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb)
                            ]
                elif k in SIMPLE_TEXT_KEYS:
                    d[SIMPLE_TEXT_KEYS[k]] = v['simpleText']
                elif k == 'lengthText':
                    d['length_accessible'] = path(
                        "accessibility.accessibilityData.label", v)
                    d['length'] = v['simpleText']
                elif k == 'ownerBadges':
                    d['verified'] = is_verified(v)
                elif k == 'thumbnail':
                    for thumb in v['thumbnails']:
                        try:
                            d['video_thumbnails'].append(
                                extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb))
                        except KeyError:
                            d['video_thumbnails'] = [
                                extract_keys(EXTRACTED_THUMBNAIL_KEYS, thumb)
                            ]
            print(json.dumps(d))
    else:
        for item in yt.get_history_info():
            print(item['videoRenderer']['videoId'])
    return 0


def remove_history_entry() -> int:
    parser = _common_arguments('Remove videos from Watch History')
    parser.add_argument('video_id', nargs='+')
    args = parser.parse_args()
    kwargs = _parse_common_arguments(args)
    yt = YouTube(**kwargs)
    try:
        yt.login()
    except Exception as e:
        if args.debug:
            raise e
        print(str(e), file=sys.stderr)
        return 1
    for vid in args.video_id:
        yt.remove_video_id_from_history(vid)
    return 0


def remove_svi_callback(
    playlist_id: Optional[str] = None,
    parser: Optional[argparse.ArgumentParser] = None  # pylint: disable=unused-argument
) -> Callable[..., int]:
    def f() -> int:
        nonlocal parser
        if not parser:
            parser = _common_arguments('Remove videos from a playlist')
            parser.add_argument('set_video_ids', nargs='+')
        args = parser.parse_args()
        kwargs = _parse_common_arguments(args)
        yt = YouTube(**kwargs)
        try:
            yt.login()
        except Exception as e:
            if args.debug:
                raise e
            print(str(e), file=sys.stderr)
            return 1
        for svi in args.set_video_ids:
            yt.remove_set_video_id_from_playlist(
                playlist_id or args.playlist_id, svi)
        return 0

    return f


def remove_watchlater_setvideoid() -> int:
    parser = _common_arguments('Remove videos from your Watch Later queue')
    parser.add_argument('set_video_ids', nargs='+')
    return remove_svi_callback(playlist_id='WL')()


def remove_setvideoid() -> int:
    parser = _common_arguments('Remove videos from a playlist')
    parser.add_argument('playlist_id')
    parser.add_argument('set_video_ids', nargs='+')
    return remove_svi_callback(parser=parser)()


# pylint: disable=invalid-name
clear_favorites = _simple_method_call('clear_favorites',
                                      'Clear your favourites playlist')
clear_search_history = _simple_method_call('clear_search_history',
                                           'Clear your search history')
clear_watch_history = _simple_method_call('clear_watch_history',
                                          'Clear your watch history')
clear_watch_later = _simple_method_call('clear_watch_later',
                                        'Clear your Watch Later queue')
toggle_search_history = _simple_method_call('toggle_search_history',
                                            'Turn on/off your search history')
toggle_watch_history = _simple_method_call('toggle_watch_history',
                                           'Turn on/off your watch history')
