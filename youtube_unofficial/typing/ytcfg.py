from typing_extensions import TypedDict


class YtcfgDict(TypedDict, total=False):
    DELEGATED_SESSION_ID: str
    EVENT_ID: str
    ID_TOKEN: str
    INNERTUBE_API_KEY: str
    INNERTUBE_CONTEXT_CLIENT_NAME: int
    INNERTUBE_CONTEXT_CLIENT_VERSION: str
    LOGGED_IN: str
    PAGE_CL: int
    VARIANTS_CHECKSUM: str
    XSRF_TOKEN: str
