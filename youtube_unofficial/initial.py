from typing import Any, Mapping, cast
import json
import re

from bs4 import BeautifulSoup as Soup

from .typing.guide_data import GuideData
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


def initial_guide_data(content: Soup) -> GuideData:
    return cast(
        GuideData,
        first(
            json.loads(
                first(
                    first(x.text for x in content.select('script')
                          if 'var ytInitialGuideData =' in
                          x.text).strip().split('\n')[:-1]))))
