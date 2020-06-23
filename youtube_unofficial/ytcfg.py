from typing import Any, Dict, Mapping, cast
import json
import re

from bs4 import BeautifulSoup as Soup

from .constants import WATCH_LATER_URL


def find_ytcfg(soup: Soup) -> Mapping[str, Any]:
    return cast(
        Mapping[str, Any],
        json.JSONDecoder().raw_decode(
            re.sub(
                r'.+ytcfg.set\(\{', '{',
                list(
                    filter(
                        lambda x: '"INNERTUBE_CONTEXT_CLIENT_VERSION":' in x.
                        text, soup.select('script')))[0].text.strip()))[0])


def ytcfg_headers(ytcfg: Mapping[str, str]) -> Dict[str, str]:
    return {
        'x-youtube-page-cl': str(ytcfg['PAGE_CL']),
        'x-youtube-identity-token': ytcfg['ID_TOKEN'],
        'x-spf-referer': WATCH_LATER_URL,
        'x-youtube-utc-offset': '-240',
        'x-spf-previous': WATCH_LATER_URL,
        'x-youtube-client-version': ytcfg['INNERTUBE_CONTEXT_CLIENT_VERSION'],
        'x-youtube-variants-checksum': ytcfg['VARIANTS_CHECKSUM'],
        'x-youtube-client-name': str(ytcfg['INNERTUBE_CONTEXT_CLIENT_NAME'])
    }
