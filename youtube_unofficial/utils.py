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
    yield from (''.join(list(x.children)) for x in soup.select('script'))  # type: ignore[arg-type]


def extract_keys(keys: Iterable[_K], obj: Mapping[_K, _V]) -> dict[_K, _V]:
    """Extract only the specified keys from a dictionary."""
    new = {}
    for key in keys:
        new[key] = obj[key]
    return new


def get_text_runs(desc: DescriptionSnippet) -> str:
    """Extract text from a description snippet."""
    return ''.join(x['text'] for x in desc['runs']).strip().replace('\n', ' - ')


def context_client_body(ytcfg: YtcfgDict) -> dict[str, str]:
    """Get the context client body for API requests."""
    assert 'INNERTUBE_CONTEXT_CLIENT_VERSION' in ytcfg
    return {
        'clientName': 'WEB',
        'clientVersion': ytcfg['INNERTUBE_CONTEXT_CLIENT_VERSION'],
    }


_YT_INITIAL_DATA_RE = r'^var ytInitialData(?:\s+)?='


def initial_data(content: Soup) -> dict[str, Any]:
    """Extract ytInitialData from a BeautifulSoup object."""
    return cast(
        'dict[str, Any]',
        json.loads(
            first(
                re.sub(
                    _YT_INITIAL_DATA_RE, '',
                    first(x for x in extract_script_content(content)
                          if re.match(_YT_INITIAL_DATA_RE, x))).split('\n'))[:-1]))


def find_ytcfg(soup: Soup) -> YtcfgDict:
    """Extract ytcfg from a BeautifulSoup object."""
    return cast(
        'YtcfgDict',
        first(json.JSONDecoder().raw_decode(
            re.sub(r'.+ytcfg.set\(\{',
                   '{',
                   first(x for x in extract_script_content(soup)
                         if '"INNERTUBE_CONTEXT_CLIENT_VERSION":' in x).strip().replace('\n', ''),
                   count=1))))


def ytcfg_headers(ytcfg: YtcfgDict) -> dict[str, str]:
    """Get headers required for API requests."""
    assert 'DELEGATED_SESSION_ID' in ytcfg or 'USER_SESSION_ID' in ytcfg
    return {
        'x-goog-authuser': '0',
        'x-goog-page-id': str(ytcfg.get('DELEGATED_SESSION_ID', ytcfg.get('USER_SESSION_ID', ''))),
        'x-origin': 'https://www.youtube.com'
    }
