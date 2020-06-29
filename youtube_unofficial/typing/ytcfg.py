from typing_extensions import TypedDict


class YtcfgDict(TypedDict, total=False):
    DELEGATED_SESSION_ID: str
    EVENT_ID: str
    ID_TOKEN: str
    INNERTUBE_API_KEY: str
    INNERTUBE_CONTEXT_CLIENT_NAME: int
    INNERTUBE_CONTEXT_CLIENT_VERSION: str
    INNERTUBE_CONTEXT_GL: str
    INNERTUBE_CONTEXT_HL: str
    LOGGED_IN: str
    PAGE_CL: int
    VARIANTS_CHECKSUM: str
    VISITOR_DATA: str
    XSRF_TOKEN: str
