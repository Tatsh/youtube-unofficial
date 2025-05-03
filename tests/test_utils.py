from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from youtube_unofficial.utils import (
    context_client_body,
    extract_keys,
    extract_script_content,
    find_ytcfg,
    get_text_runs,
    initial_data,
    ytcfg_headers,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from youtube_unofficial.typing.history import DescriptionSnippet
    from youtube_unofficial.typing.ytcfg import YtcfgDict


def test_extract_keys() -> None:
    keys = ['a', 'b']
    obj = {'a': 1, 'b': 2, 'c': 3}
    result = extract_keys(keys, obj)
    assert result == {'a': 1, 'b': 2}


def test_get_text_runs() -> None:
    desc: DescriptionSnippet = {'runs': [{'text': 'Hello'}, {'text': 'World'}]}
    result = get_text_runs(desc)
    assert result == 'HelloWorld'


def test_context_client_body() -> None:
    ytcfg: YtcfgDict = {'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.20230101'}
    result = context_client_body(ytcfg)
    assert result == {'clientName': 'WEB', 'clientVersion': '1.20230101'}


def test_initial_data(mocker: MockerFixture) -> None:
    mock_content = mocker.MagicMock(spec=BeautifulSoup)
    mock_script = 'var ytInitialData = {"key": "value"};'
    mocker.patch('youtube_unofficial.utils.extract_script_content', return_value=[mock_script])
    result = initial_data(mock_content)
    assert result == {'key': 'value'}


def test_find_ytcfg(mocker: MockerFixture) -> None:
    mock_soup = mocker.MagicMock(spec=BeautifulSoup)
    mock_script = '<script>ytcfg.set({"INNERTUBE_CONTEXT_CLIENT_VERSION": "1.20230101"});</script>'
    mocker.patch('youtube_unofficial.utils.extract_script_content', return_value=[mock_script])
    result = find_ytcfg(mock_soup)
    assert result == {'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.20230101'}


def test_ytcfg_headers() -> None:
    ytcfg: YtcfgDict = {'USER_SESSION_ID': '12345'}
    result = ytcfg_headers(ytcfg)
    assert result == {
        'x-goog-authuser': '0',
        'x-goog-page-id': '12345',
        'x-origin': 'https://www.youtube.com',
    }


def test_extract_script_content(mocker: MockerFixture) -> None:
    mock_soup = mocker.MagicMock(spec=BeautifulSoup)
    mock_script_tags = [
        mocker.MagicMock(children=['var ytInitialData = {"key": "value"};']),
        mocker.MagicMock(children=['<script>console.log("test");</script>']),
    ]
    mock_soup.select.return_value = mock_script_tags

    result = list(extract_script_content(mock_soup))

    assert result == [
        'var ytInitialData = {"key": "value"};',
        '<script>console.log("test");</script>',
    ]
    mock_soup.select.assert_called_once_with('script')
