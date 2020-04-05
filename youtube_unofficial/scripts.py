# pylint: disable=broad-except
from operator import itemgetter
from os.path import expanduser
from typing import Any, Callable, Mapping, Optional
import argparse
import logging
import sys

from . import YouTube

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
)


def _common_arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Clear your YouTube watch history')
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


def _simple_method_call(method_name: str) -> Callable[..., int]:
    def f() -> int:
        parser = _common_arguments()
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
            parser = _common_arguments()
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
            print('{} {}'.format(item['playlistVideoRenderer']['videoId'],
                                 item['playlistVideoRenderer']['setVideoId']))
        return 0

    return f


def print_watchlater_ids() -> int:
    return print_playlist_ids_callback(playlist_id='WL')()


def print_playlist_ids() -> int:
    parser = _common_arguments()
    parser.add_argument('playlist_id')
    return print_playlist_ids_callback(parser=parser)()


def print_history_ids() -> int:
    parser = _common_arguments()
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
    from pprint import pprint
    import json
    for item in yt.get_history_info():
        if 'videoRenderer' in item:
            if args.json:
                print(
                    json.dumps({
                        'owner':
                        ' - '.join(
                            map(itemgetter('text'),
                                item['videoRenderer']['ownerText']['runs'])),
                        'title':
                        ' - '.join(
                            map(itemgetter('text'),
                                item['videoRenderer']['title']['runs'])),
                        'videoId':
                        item['videoRenderer']['videoId']
                    }))
            else:
                print(item['videoRenderer']['videoId'])
    return 0


def remove_history_entry() -> int:
    parser = _common_arguments()
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
            parser = _common_arguments()
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
    parser = _common_arguments()
    parser.add_argument('set_video_ids', nargs='+')
    return remove_svi_callback(playlist_id='WL')()


def remove_setvideoid() -> int:
    parser = _common_arguments()
    parser.add_argument('playlist_id')
    parser.add_argument('set_video_ids', nargs='+')
    return remove_svi_callback(parser=parser)()


# pylint: disable=invalid-name
clear_favorites = _simple_method_call('clear_favorites')
clear_watch_history = _simple_method_call('clear_watch_history')
clear_watch_later = _simple_method_call('clear_watch_later')
