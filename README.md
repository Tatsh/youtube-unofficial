# youtube-unofficial

[![Python versions](https://img.shields.io/pypi/pyversions/youtube-unofficial.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/youtube-unofficial)](https://pypi.org/project/youtube-unofficial/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/youtube-unofficial)](https://github.com/Tatsh/youtube-unofficial/tags)
[![License](https://img.shields.io/github/license/Tatsh/youtube-unofficial)](https://github.com/Tatsh/youtube-unofficial/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/youtube-unofficial/v0.3.0/master)](https://github.com/Tatsh/youtube-unofficial/compare/v0.3.0...master)
[![QA](https://github.com/Tatsh/youtube-unofficial/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/youtube-unofficial/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/youtube-unofficial/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/youtube-unofficial/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/youtube-unofficial/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/youtube-unofficial?branch=master)
[![Documentation Status](https://readthedocs.org/projects/youtube-unofficial/badge/?version=latest)](https://youtube-unofficial.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pytest](https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black)](https://docs.pytest.org/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/youtube-unofficial/month)](https://pepy.tech/project/youtube-unofficial)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/youtube-unofficial?logo=github&style=flat)](https://github.com/Tatsh/youtube-unofficial/stargazers)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)

Access parts of your account unavailable through normal YouTube API access.

## Installation

### Poetry

```shell
poetry add youtube-unofficial
```

### Pip

```shell
pip install youtube-unofficial
```

## Usage

This uses a browser cookie storage to be able to access authorised endpoints. There is no feature to
log in. You must be logged on in a supported browser. This supports any browser that yt-dlp
supports.

### Command line

```plain
Usage: youtube [OPTIONS] COMMAND [ARGS]...

  Unofficial YouTube CLI.

Options:
  -h, --help  Show this message and exit.

Commands:
  clear-watch-history          Clear watch history.
  clear-watch-later            Clear watch later queue.
  print-history                Print your watch history.
  print-playlist               Print a playlist.
  print-watch-later            Print your Watch Later playlist.
  remove-history-entries       Remove videos from Watch History.
  remove-video-id              Remove videos from a playlist.
  remove-watch-later-video-id  Remove videos from your Watch Later queue.
  toggle-watch-history         Disable or enable watch history
```

Every command takes a `--debug` or `-d` argument to show very verbose logs.

Some commands accept a `-j`/`--json` argument to print machine-readable output as JSON lines.

### In Python

```python
from youtube_unofficial import YouTubeClient

# Arguments are the browser name and profile.
yt = YouTubeClient('chrome', 'Default')

# Clear watch history
yt.clear_watch_history()

# Remove a single video ID from Watch Later queue
yt.remove_video_id_from_playlist('WL', video_id)

# Clear entire Watch Later queue
yt.clear_watch_later()
```

## Contributing

For a new feature to be accepted, it must be something that _cannot_ be achieved with Google's
official API. It also has to be on the youtube.com/youtu.be website or app and not a place like
_My Activity_.

Code must run through `yarn qa` and have zero issues.
