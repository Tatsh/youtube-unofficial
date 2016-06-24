# encoding: utf-8
from __future__ import print_function

from . import YouTube


def clear_watch_history():
    yt = YouTube()

    try:
        yt.login()
        yt.clear_watch_history()
    except Exception as e:
        print(e.args[0], file=sys.stderr)
        return 1
