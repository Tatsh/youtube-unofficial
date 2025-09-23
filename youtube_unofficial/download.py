"""Download utility function."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
import logging

from requests import Request, Session
from typing_extensions import overload

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ('download_page',)
log = logging.getLogger(__name__)


@overload
def download_page(sess: Session,
                  url: str,
                  data: Any = None,
                  method: Literal['get', 'post'] = 'get',
                  headers: Mapping[str, str] | None = None,
                  params: Mapping[str, str] | None = None,
                  json: Any = None,
                  *,
                  return_json: Literal[False]) -> str:  # pragma: no cover
    ...


@overload
def download_page(sess: Session,
                  url: str,
                  data: Any = None,
                  method: Literal['get', 'post'] = 'get',
                  headers: Mapping[str, str] | None = None,
                  params: Mapping[str, str] | None = None,
                  json: Any = None,
                  *,
                  return_json: Literal[True]) -> dict[str, Any]:  # pragma: no cover
    ...


def download_page(sess: Session,
                  url: str,
                  data: Any = None,
                  method: Literal['get', 'post'] = 'get',
                  headers: Mapping[str, str] | None = None,
                  params: Mapping[str, str] | None = None,
                  json: Any = None,
                  *,
                  return_json: bool = False) -> str | dict[str, Any]:
    """Download a page using the provided session."""
    if headers:
        sess.headers.update(headers)
    req = Request(method, url, data=data, params=params, json=json)
    prepped = sess.prepare_request(req)
    del prepped.headers['accept-encoding']
    r = sess.send(prepped)
    r.raise_for_status()
    if not return_json:
        return r.text.strip()
    return cast('dict[str, Any]', r.json())
