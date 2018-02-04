Use this library to do things the real YouTube API does not let you do. DO NOT USE THIS FOR ANY ACCOUNT OTHER THAN YOUR OWN!

This library supports both Python 2.7.x and 3.4+.

# Use a netrc file

Every command can take a `--username` and `--password` argument.

You should consider using a netrc file for your login. Example at `~/.netrc`:

```
machine youtube login LOGIN password YOUR_PASSWORD
```

You can specify a custom netrc file with the `--netrc` argument.

# Usage

## Command line

* `youtube-clear-favorites` - Clear your *Favourites*
* `youtube-clear-history` - Clear your *Watch History*
* `youtube-clear-watch-later` - Clear your *Watch Later* queue

Every command takes a `--debug` argument.

You can use exported cookies (in Netscape format) with the `--cookies COOKIES_FILE` argument.

## In Python

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

# Contributing

For a new feature to be accepted, it must be something that *cannot* be achieved with Google's official API.

Code must run through `flake8` with default settings with no errors.

## `YouTube` class internals

* `_sess` - `requests.Session()` instance. If you must modify this object, clone it then make your modification (such as `self._sess.headers.update()`).
* `_log` - Logger instance
* `_logged_in` - Not all methods will need a login, so this is a boolean value indicating if authentication has already been established. Do *not* call `self.login()` (programmer must do this manually). Instead raise an `AuthenticationError` indicating that login is required for the method in question.
* `_download_page(self, url, data=None, method='get', headers=None)` - HTTP request on an absolute URL and return the content
* `_download_page_soup(self, *args, **kwargs)` - Same as `_download_page()` but returns a `BeautifulSoup` instance
* `_find_post_headers(self, soup)` - Some requests will need certain custom headers set. Use this to find them in the HTML content using a `BeautifulSoup` instance. The headers to find are pre-defined (such as `XSRF_TOKEN`).
