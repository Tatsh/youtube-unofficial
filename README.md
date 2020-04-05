# Unofficial YouTube API client

Use this library to do things the real YouTube API does not let you do. DO NOT USE THIS FOR ANY ACCOUNT OTHER THAN YOUR OWN!

This library supports Python 3.6+.

## Use a netrc file

_Please note for the time being, logging in is not working. For more details, see this [youtube-dl issue](https://github.com/ytdl-org/youtube-dl/issues/24508#issuecomment-609362963)._

Every command can take a `--username` and `--password` argument.

You should consider using a netrc file for your login. Example at `~/.netrc`:

```
machine youtube login LOGIN password YOUR_PASSWORD
```

You can specify a custom netrc file with the `--netrc` argument.

## Usage

### Command line

- `youtube-clear-favorites` - Clear your _Favourites_
- `youtube-clear-history` - Clear your _Watch History_
- `youtube-clear-watch-later` - Clear your _Watch Later_ queue

Every command takes a `--debug` argument.

You can use exported cookies (in Netscape format) with the `--cookies COOKIES_FILE` argument.

### In Python

```bash
git clone git@github.com:Tatsh/youtube-unofficial.git
cd youtube-unofficial
pip install -e .
```

```python
from youtube_unofficial import YouTube
yt = YouTube()

# Clear watch history
yt.clear_watch_history()

# Remove a single video ID from Watch Later queue
yt.remove_video_id_from_watch_later(video_id)

# Clear entire Watch Later queue
yt.clear_watch_later()
```

## Contributing

For a new feature to be accepted, it must be something that _cannot_ be achieved with Google's official API.

Code must run through `mypy` and `pylint` based on the project settings.
