from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ('YtcfgDict',)


class YtcfgDict(TypedDict, total=False):
    """Configuration dictionary for YouTube site."""
    DELEGATED_SESSION_ID: str
    """Delegated session ID for a brand account."""
    EVENT_ID: str
    ID_TOKEN: str
    INNERTUBE_API_KEY: str
    """API key."""
    INNERTUBE_CONTEXT_CLIENT_NAME: str
    """Client name."""
    INNERTUBE_CONTEXT_CLIENT_VERSION: str
    """Client version."""
    INNERTUBE_CONTEXT_GL: str
    INNERTUBE_CONTEXT_HL: str
    LOGGED_IN: str
    """Logged in status."""
    SESSION_INDEX: int
    """Session index."""
    PAGE_CL: int
    USER_SESSION_ID: str
    """User session ID."""
    VARIANTS_CHECKSUM: str
    VISITOR_DATA: str
    """Visitor data."""
    XSRF_TOKEN: str
