"""Download utility function."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
import logging

from typing_extensions import overload

if TYPE_CHECKING:
    from collections.abc import Mapping

    import niquests

__all__ = ('download_page',)
log = logging.getLogger(__name__)


@overload
async def download_page(sess: niquests.AsyncSession,
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
async def download_page(sess: niquests.AsyncSession,
                        url: str,
                        data: Any = None,
                        method: Literal['get', 'post'] = 'get',
                        headers: Mapping[str, str] | None = None,
                        params: Mapping[str, str] | None = None,
                        json: Any = None,
                        *,
                        return_json: Literal[True]) -> dict[str, Any]:  # pragma: no cover
    ...


async def download_page(sess: niquests.AsyncSession,
                        url: str,
                        data: Any = None,
                        method: Literal['get', 'post'] = 'get',
                        headers: Mapping[str, str] | None = None,
                        params: Mapping[str, str] | None = None,
                        json: Any = None,
                        *,
                        return_json: bool = False) -> str | dict[str, Any]:
    """
    Download a page using the provided session.

    Parameters
    ----------
    sess : niquests.AsyncSession
        Niquests async session to use.
    url : str
        Target URL.
    data : Any
        Optional form body for the request.
    method : str
        HTTP method, ``get`` or ``post``.
    headers : Mapping[str, str] | None
        Extra headers for this request only.
    params : Mapping[str, str] | None
        Query string parameters.
    json : Any
        Optional JSON body for the request.
    return_json : bool
        If ``True``, parse the response as JSON.

    Returns
    -------
    str | dict[str, Any]
        Response body text, or parsed JSON when ``return_json`` is ``True``.
    """
    merged: dict[str, str] = {str(k): str(v) for k, v in dict(sess.headers).items()}
    if headers:
        merged.update(headers)
    merged.pop('Accept-Encoding', None)
    r = await sess.request(method, url, data=data, params=params, json=json, headers=merged)
    r.raise_for_status()
    if not return_json:
        text = r.text
        return text.strip() if text else ''
    return cast('dict[str, Any]', r.json())
