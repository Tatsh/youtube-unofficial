from os import chdir, makedirs
from typing import Any, Dict, Optional, cast
import subprocess as sp
import sys

from youtube_unofficial.scripts import get_common_parser, parse_common_args

from . import YouTube

__all__ = ('download_history', 'download_playlist', 'download_watch_later')


def call_youtube_dl(video_id: str) -> sp.CompletedProcess:
    return sp.run(('youtube-dl', '--', video_id), check=True)


def download_history() -> int:
    parser = get_common_parser()
    parser.add_argument('-o', '--output-dir', nargs=1)
    parser.add_argument('-D',
                        '--delete-after',
                        action='store_true',
                        help='Delete each downloaded item from history')
    args = parser.parse_args()
    kwargs = cast(Dict[str, Any], parse_common_args(args))
    kwargs['logged_in'] = True
    yt = YouTube(**kwargs)
    try:
        yt.login()
    except Exception as e:  # pylint: disable=broad-except
        if args.debug:
            raise e
        print(str(e), file=sys.stderr)
        return 1
    makedirs(args.output_dir[0], exist_ok=True)
    chdir(args.output_dir[0])
    for item in yt.get_history_info():
        call_youtube_dl(item['videoRenderer']['videoId'])
        if args.delete_after:
            yt.remove_video_ids_from_history(item['videoRenderer']['videoId'])
    return 0


def download_playlist(playlist_id: Optional[str] = None) -> int:
    if playlist_id:
        sys.argv.append(playlist_id)
    parser = get_common_parser()
    parser.add_argument('-o', '--output-dir', nargs=1)
    parser.add_argument('-D',
                        '--delete-after',
                        action='store_true',
                        help='Delete each downloaded item from history')
    parser.add_argument('playlist_id', nargs=1, default=playlist_id)
    args = parser.parse_args()
    kwargs = cast(Dict[str, Any], parse_common_args(args))
    kwargs['logged_in'] = True
    yt = YouTube(**kwargs)
    try:
        yt.login()
    except Exception as e:  # pylint: disable=broad-except
        if args.debug:
            raise e
        print(str(e), file=sys.stderr)
        return 1
    if playlist_id == 'FAVORITES':
        args.playlist_id = [yt.get_favorites_playlist_id()]
    makedirs(args.output_dir[0], exist_ok=True)
    chdir(args.output_dir[0])
    for item in yt.get_playlist_info(args.playlist_id[0]):
        renderer = item['playlistVideoRenderer']
        call_youtube_dl(renderer['videoId'])
        if args.delete_after:
            yt.remove_set_video_id_from_playlist(args.playlist_id[0],
                                                 renderer['setVideoId'])
    return 0


def download_watch_later() -> int:
    return download_playlist('WL')


def download_liked() -> int:
    return download_playlist('LL')
