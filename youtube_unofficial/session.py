"""Async HTTP session setup with browser cookies."""

from __future__ import annotations

from asyncio import to_thread
from typing import TYPE_CHECKING, Any

from niquests_cache import cached_session
import yt_dlp_utils

if TYPE_CHECKING:
    from niquests_cache.session import AsyncCachedSession

from .constants import USER_AGENT

__all__ = ('build_youtube_session',)


async def build_youtube_session(browser: str, profile: str) -> AsyncCachedSession:
    """
    Build a cached async session with cookies from the browser profile.

    Browser cookie extraction runs in a worker thread so the event loop is not blocked.

    Parameters
    ----------
    browser : str
        Browser name for :func:`yt_dlp_utils.setup_session`.
    profile : str
        Browser profile name.

    Returns
    -------
    AsyncCachedSession
        Session ready for ``async with`` or immediate use.
    """
    def _sync_setup() -> Any:
        return yt_dlp_utils.setup_session(browser,
                                          profile,
                                          domains={'.youtube.com'},
                                          setup_retry=True)

    rs = await to_thread(_sync_setup)
    try:
        session = cached_session(aio=True, app_name='youtube-unofficial')
        session.cookies.update(rs.cookies)  # type: ignore[no-untyped-call]
        session.headers['User-Agent'] = USER_AGENT
        return session
    finally:
        rs.close()
