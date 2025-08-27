"""Typed dictionary for YouTube configuration (ytcfg)."""
from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ('YtcfgDict',)


class YtcfgDict(TypedDict, total=False):
    """Configuration dictionary for YouTube site."""
    DELEGATED_SESSION_ID: str
    """Delegated session ID for a brand account."""
    EVENT_ID: str
    """Unknown."""
    ID_TOKEN: str
    """Unknown."""
    INNERTUBE_API_KEY: str
    """API key."""
    INNERTUBE_CONTEXT_CLIENT_NAME: str
    """Client name."""
    INNERTUBE_CONTEXT_CLIENT_VERSION: str
    """Client version."""
    INNERTUBE_CONTEXT_GL: str
    """Geolocation."""
    INNERTUBE_CONTEXT_HL: str
    """Language code."""
    LOGGED_IN: str
    """Logged in status."""
    SESSION_INDEX: int
    """Session index."""
    PAGE_CL: int
    """Unknown."""
    USER_SESSION_ID: str
    """User session ID."""
    VARIANTS_CHECKSUM: str
    """Checksum for variants."""
    VISITOR_DATA: str
    """Visitor data."""
    XSRF_TOKEN: str
    """Cross-site request forgery token."""
