# encoding: utf-8
from __future__ import print_function
from __future__ import unicode_literals
from os.path import expanduser
import argparse
import logging
import sys

from . import YouTube


def _common_arguments():
    parser = argparse.ArgumentParser(
        description='Clear your YouTube watch history')

    parser.add_argument('-u', '--username',
                        help='If not specified, a netrc file will be used')
    parser.add_argument('-p', '--password',
                        help='If not specified, a netrc file will be used')
    parser.add_argument('--netrc',
                        default=expanduser('~/.netrc'),
                        help='A netrc file to use')
    parser.add_argument('--cookies',
                        default=expanduser('~/.ytch-cookies.txt'),
                        help='Netscape cookies file to use')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Log and raise exceptions')

    return parser


def _parse_common_arguments(args):
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
        channel.setFormatter(logging.Formatter('%(asctime)s - %(name)s - '
                                               '%(levelname)s - %(message)s'))

        for logname in ('youtube-unofficial', 'requests',):
            log = logging.getLogger(logname)
            log.setLevel(logging.DEBUG)
            log.addHandler(channel)

    return kwargs


def _simple_method_call(method_name):
    def f():
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
            print(e.args[0], file=sys.stderr)
            return 1
    return f


clear_watch_history = _simple_method_call('clear_watch_history')
clear_watch_later = _simple_method_call('clear_watch_later')
clear_favorites = _simple_method_call('clear_favorites')
