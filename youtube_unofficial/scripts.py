# encoding: utf-8
from __future__ import print_function
from os.path import expanduser
import argparse
import logging
import sys

from . import YouTube


def clear_watch_history():
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

    args = parser.parse_args()
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

    yt = YouTube(**kwargs)

    try:
        yt.login()
        yt.clear_watch_history()
    except Exception as e:
        if args.debug:
            raise e
        print(e.args[0], file=sys.stderr)
        return 1
