# Unofficial YouTube API client

Use this library to do things the real YouTube API does not let you do. DO NOT USE THIS FOR ANY ACCOUNT OTHER THAN YOUR OWN!

This library supports Python 3.6+.

## Use a netrc file

_Please note for the time being, logging in is not working. For more details, see this [youtube-dl issue](https://github.com/ytdl-org/youtube-dl/issues/24508#issuecomment-609362963)._

Every command can take a `--username` and `--password` argument.

You should consider using a netrc file for your login. Example at `~/.netrc`:

```plain
machine youtube login LOGIN password YOUR_PASSWORD
```

You can specify a custom netrc file with the `--netrc` argument.

## Usage

### Command line

- `youtube-clear-history` - Clear your _Watch History_
- `youtube-clear-search-history` - Clear your _Search History_
- `youtube-clear-watch-later` - Clear your _Watch Later_ queue
- `youtube-print-history-ids` - Print _Watch History_ video IDs
- `youtube-print-playlist-ids` - Print video IDs from a specific playlist
- `youtube-print-watch-later-ids` - Print _Watch Later_ video IDs
- `youtube-remove-history-entries` - Remove videos from your _Watch History_
- `youtube-remove-setvideoid` - Remove a video from a playlist
- `youtube-remove-watch-later-setvideoid` - Remove a video from your _Watch Later_ queue
- `youtube-toggle-search-history` - Turn on/off _Search History_
- `youtube-toggle-watch-history` - Turn on/off _Watch History_

Every command takes a `--debug` argument.

You can use exported cookies in Netscape format with the `--cookies COOKIES_FILE` argument.

Some commands accept a `-j`/`--json` argument to print machine-readable output.

### Download commands

- `ytdl-history` - Use youtube-dl to download your history
- `ytdl-liked` - Use youtube-dl to download your liked videos
- `ytdl-playlist` - Use youtube-dl to download a playlist
- `ytdl-watch-later` - Use youtube-dl to download your Watch Later playlist

For downloads to work, `youtube-dl` must be in `PATH`. To pass arguments to `youtube-dl`, specify `--` before those arguments. Example with arguments to youtube-dl:

```shell
ytdl-history --output-dir ~/Downloads --delete-after -- --extract-audio --audio-format m4a --audio-quality 0
```

Each download command has a `-D`/`--delete-after` option, which makes the script delete the entry from the set of videos after a successful download.

### In Python

```python
from youtube_unofficial import YouTube

yt = YouTube(cookies=expanduser('~/my-cookies-file.txt'), logged_in=True)

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
