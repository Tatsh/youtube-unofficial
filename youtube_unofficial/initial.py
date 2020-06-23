from typing import Any, Mapping, cast
import json
import re

from bs4 import BeautifulSoup as Soup

from .typing.guide_data import GuideData


def initial_data(content: Soup) -> Mapping[str, Any]:
    text = list(
        filter(lambda x: '"ytInitialData"' in x.text,
               content.select('script')))[0].text.strip()
    if 'JSON.parse' in text:
        return cast(
            Mapping[str, Any],
            json.loads(json.JSONDecoder().raw_decode(
                re.sub(r'^window[^=]+= JSON\.parse\(', '',
                       text).split('\n')[0][:-1])[0]))
    return cast(
        Mapping[str, Any],
        json.loads(re.sub('^window[^=]+= ', '', text).split('\n')[0][:-1]))


def initial_guide_data(content: Soup) -> GuideData:
    return cast(
        GuideData,
        json.loads(
            re.sub(
                '^var ytInitialGuideData = ', '',
                list(
                    filter(lambda x: 'var ytInitialGuideData =' in x.text,
                           content.select('script')))[0].text.strip()).split(
                               '\n')[0][:-1]))
