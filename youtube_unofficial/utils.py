"""Utility functions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast
import json
import logging
import re

from more_itertools import first

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping

    from bs4 import BeautifulSoup as Soup

    from .typing.history import DescriptionSnippet
    from .typing.ytcfg import YtcfgDict

__all__ = ('context_client_body', 'extract_keys', 'find_ytcfg', 'get_text_runs', 'initial_data',
           'ytcfg_headers')

_K = TypeVar('_K')
_V = TypeVar('_V')
log = logging.getLogger(__name__)


def extract_script_content(soup: Soup) -> Iterator[str]:
    yield from (''.join(cast('list[str]', list(x.children))) for x in soup.select('script'))


def extract_keys(keys: Iterable[_K], obj: Mapping[_K, _V]) -> dict[_K, _V]:
    """
    Extract only the specified keys from a dictionary.

    Parameters
    ----------
    keys : Iterable[_K]
        Keys to include.
    obj : Mapping[_K, _V]
        Source mapping.

    Returns
    -------
    dict[_K, _V]
        A new mapping with only the requested keys.
    """
    new = {}
    for key in keys:
        new[key] = obj[key]
    return new


def get_text_runs(desc: DescriptionSnippet) -> str:
    """
    Extract text from a description snippet.

    Parameters
    ----------
    desc : DescriptionSnippet
        Snippet containing runs.

    Returns
    -------
    str
        Flattened text.
    """
    return ''.join(x['text'] for x in desc['runs']).strip().replace('\n', ' - ')


def context_client_body(ytcfg: YtcfgDict) -> dict[str, str]:
    """
    Get the context client body for API requests.

    Parameters
    ----------
    ytcfg : YtcfgDict
        YouTube configuration from the page.

    Returns
    -------
    dict[str, str]
        Client name and version for the Innertube context.

    Raises
    ------
    KeyError
        If ``INNERTUBE_CONTEXT_CLIENT_VERSION`` is missing.
    """
    if 'INNERTUBE_CONTEXT_CLIENT_VERSION' not in ytcfg:
        msg = 'Missing INNERTUBE_CONTEXT_CLIENT_VERSION in ytcfg.'
        raise KeyError(msg)
    return {'clientName': 'WEB', 'clientVersion': ytcfg['INNERTUBE_CONTEXT_CLIENT_VERSION']}


_YT_INITIAL_DATA_RE = r'^var ytInitialData(?:\s+)?='


def initial_data(content: Soup) -> dict[str, Any]:
    """
    Extract ytInitialData from a BeautifulSoup object.

    Parameters
    ----------
    content : Soup
        Parsed HTML document.

    Returns
    -------
    dict[str, Any]
        Parsed ytInitialData payload.
    """
    return cast(
        'dict[str, Any]',
        json.loads(
            first(
                re.sub(
                    _YT_INITIAL_DATA_RE, '',
                    first(x for x in extract_script_content(content)
                          if re.match(_YT_INITIAL_DATA_RE, x))).split('\n'))[:-1]))


def find_ytcfg(soup: Soup) -> YtcfgDict:
    """
    Extract ytcfg from a BeautifulSoup object.

    Parameters
    ----------
    soup : Soup
        Parsed HTML document.

    Returns
    -------
    YtcfgDict
        Parsed ytcfg configuration.
    """
    return cast(
        'YtcfgDict',
        first(json.JSONDecoder().raw_decode(
            re.sub(r'.+ytcfg.set\(\{',
                   '{',
                   first(x for x in extract_script_content(soup)
                         if '"INNERTUBE_CONTEXT_CLIENT_VERSION":' in x).strip().replace('\n', ''),
                   count=1))))


def ytcfg_headers(ytcfg: YtcfgDict) -> dict[str, str]:
    """
    Get headers required for API requests.

    Parameters
    ----------
    ytcfg : YtcfgDict
        YouTube configuration from the page.

    Returns
    -------
    dict[str, str]
        Headers including the authorisation page identifier.

    Raises
    ------
    KeyError
        If neither ``DELEGATED_SESSION_ID`` nor ``USER_SESSION_ID`` is present.
    """
    if 'DELEGATED_SESSION_ID' not in ytcfg and 'USER_SESSION_ID' not in ytcfg:
        msg = 'Missing DELEGATED_SESSION_ID or USER_SESSION_ID in ytcfg.'
        raise KeyError(msg)
    return {
        'x-goog-authuser': '0',
        'x-goog-page-id': str(ytcfg.get('DELEGATED_SESSION_ID', ytcfg.get('USER_SESSION_ID', ''))),
        'x-origin': 'https://www.youtube.com'
    }
