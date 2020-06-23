from typing import Any, Mapping, Optional, Sequence, Union, cast

from bs4 import BeautifulSoup as Soup
from requests import Request, Session
from typing_extensions import Literal

__all__ = ('download_page', 'DownloadMixin')


def download_page(
    sess: Session,
    url: str,
    data: Any = None,
    method: Literal['get', 'post'] = 'get',
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, str]] = None,
    return_json: bool = False
) -> Union[str, Sequence[Any], Mapping[str, Any]]:
    if headers:
        sess.headers.update(headers)
    req = Request(method.upper(), url, data=data, params=params)
    prepped = sess.prepare_request(req)  # type: ignore[no-untyped-call]
    del prepped.headers['accept-encoding']
    r = sess.send(prepped)  # type: ignore[no-untyped-call]
    r.raise_for_status()

    if not return_json:
        return cast(str, r.text.strip())

    return cast(Mapping[str, Any], r.json())


class DownloadMixin:
    _sess: Session

    def _download_page(
        self,
        url: str,
        data: Any = None,
        method: Literal['get', 'post'] = 'get',
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        return_json: bool = False
    ) -> Union[str, Sequence[Any], Mapping[str, Any]]:
        return download_page(self._sess, url, data, method, headers, params,
                             return_json)

    def _download_page_soup(self, *args: Any, **kwargs: Any) -> Soup:
        return Soup(self._download_page(*args, **kwargs),
                    kwargs.pop('parser', 'html5lib'))
