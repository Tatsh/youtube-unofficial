from typing import Any, Mapping, cast
import json
import re

from bs4 import BeautifulSoup as Soup

from .util import first

YT_INITIAL_DATA_RE = r'^var ytInitialData(?:\s+)?='


def initial_data(content: Soup) -> Mapping[str, Any]:
    return cast(
        Mapping[str, Any],
        json.loads(
            first(
                re.sub(
                    YT_INITIAL_DATA_RE, '',
                    first(x.text.strip() for x in content.select('script')
                          if re.match(YT_INITIAL_DATA_RE,
                                      x.text.strip()))).split('\n'))[:-1]))
