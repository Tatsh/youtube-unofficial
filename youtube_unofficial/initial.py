from typing import Any, Mapping, cast
import json
import re

from bs4 import BeautifulSoup as Soup

from .typing.guide_data import GuideData
from .util import first


def initial_data(content: Soup) -> Mapping[str, Any]:
    text = first(
        filter(lambda x: '"ytInitialData"' in x.text,
               content.select('script'))).text.strip()
    if 'JSON.parse' in text:
        return cast(
            Mapping[str, Any],
            json.loads(
                first(json.JSONDecoder().raw_decode(
                    first(
                        re.sub(r'^window[^=]+= JSON\.parse\(', '',
                               text).split('\n'))[:-1]))))
    return cast(
        Mapping[str, Any],
        json.loads(first(re.sub('^window[^=]+= ', '', text).split('\n'))[:-1]))


def initial_guide_data(content: Soup) -> GuideData:
    return cast(
        GuideData,
        first(
            json.loads(
                re.sub(
                    '^var ytInitialGuideData = ', '',
                    first(
                        filter(lambda x: 'var ytInitialGuideData =' in x.text,
                               content.select('script'))).text.strip()).split(
                                   '\n')))[:-1])
