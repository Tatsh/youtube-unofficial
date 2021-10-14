from os import chdir, makedirs
from typing import Iterable, Optional
import subprocess as sp
import sys

from . import YouTube
from .scripts import get_common_parser, parse_common_args
from .util import first

__all__ = ('download_history', 'download_playlist', 'download_watch_later',
           'download_liked')


def call_youtube_dl(
        command: str,
        video_id: str,
        args: Optional[Iterable[str]] = None) -> sp.CompletedProcess:
    return sp.run(
        (command, ) + (tuple(args) if args else tuple()) + ('--', video_id),
        check=True,
        stderr=sp.PIPE)


def download_history() -> int:
    parser = get_common_parser()
    parser.add_argument('-o', '--output-dir', nargs=1, required=True)
    parser.add_argument('-D',
                        '--delete-after',
                        action='store_true',
                        help='Delete each downloaded item from history')
    parser.add_argument('--youtube-dl',
                        default='youtube-dl',
                        nargs=1,
                        help='youtube-dl command')
    args, ytdl_args = parser.parse_known_args()
    yt = YouTube(**{**parse_common_args(args), **{'logged_in': True}})
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
        print('{}: {}'.format(
            item['videoRenderer']['videoId'],
            item['videoRenderer']['title']['runs'][0]['text']))
        call_youtube_dl(args.youtube_dl[0], item['videoRenderer']['videoId'],
                        ytdl_args[1:])
        if args.delete_after:
            yt.remove_video_ids_from_history(item['videoRenderer']['videoId'])
        break
    return 0


def download_playlist(playlist_id: Optional[str] = None) -> int:
    if playlist_id:
        try:
            dd_index = sys.argv.index('--')
            sys.argv.insert(dd_index, playlist_id)
        except ValueError:
            sys.argv.append(playlist_id)
    parser = get_common_parser()
    parser.add_argument('-o', '--output-dir', nargs=1, required=True)
    parser.add_argument('-D',
                        '--delete-after',
                        action='store_true',
                        help='Delete each downloaded item from the playlist')
    parser.add_argument('playlist_id', nargs=1, default=playlist_id)
    parser.add_argument('--youtube-dl',
                        default='youtube-dl',
                        nargs=1,
                        help='youtube-dl command')
    args, ytdl_args = parser.parse_known_args()
    try:
        ytdl_args.remove('--')
    except ValueError:
        pass
    yt = YouTube(**{**parse_common_args(args), **{'logged_in': True}})
    try:
        yt.login()
    except Exception as e:  # pylint: disable=broad-except
        if args.debug:
            raise e
        print(str(e), file=sys.stderr)
        return 1
    makedirs(args.output_dir[0], exist_ok=True)
    chdir(args.output_dir[0])
    for item in yt.get_playlist_info(args.playlist_id[0]):
        assert 'playlistVideoRenderer' in item
        renderer = item['playlistVideoRenderer']
        assert 'menu' in renderer
        set_video_id = first(
            first(a for a in x['menuServiceItemRenderer']['serviceEndpoint']
                  ['playlistEditEndpoint']['actions']
                  if a['action'] == 'ACTION_REMOVE_VIDEO')['setVideoId']
            for x in renderer['menu']['menuRenderer']['items']
            if x['menuServiceItemRenderer']['icon']['iconType'] == 'DELETE')
        assert 'videoId' in renderer
        call_youtube_dl(args.youtube_dl[0], renderer['videoId'], ytdl_args)
        if args.delete_after:
            yt.remove_set_video_id_from_playlist(args.playlist_id[0],
                                                 set_video_id,
                                                 cache_values=True)
    return 0


def download_watch_later() -> int:
    return download_playlist('WL')


def download_liked() -> int:
    return download_playlist('LL')
