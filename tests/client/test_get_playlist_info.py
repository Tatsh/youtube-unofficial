from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient


def test_get_playlist_info(mocker: MockerFixture, requests_mock: Mocker,
                           client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'tabs': [{
                                 'tabRenderer': {
                                     'content': {
                                         'sectionListRenderer': {
                                             'contents': [{
                                                 'itemSectionRenderer': {
                                                     'contents': [{
                                                         'playlistVideoListRenderer': {
                                                             'contents': [{
                                                                 'playlistVideoRenderer': {}
                                                             }, {
                                                                 'continuationItemRenderer': {}
                                                             }]
                                                         }
                                                     }]
                                                 }
                                             }]
                                         }
                                     }
                                 }
                             }]
                         }
                     }
                 })
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    result = list(client.get_playlist_info(playlist_id='test_playlist'))
    assert result == [{'playlistVideoRenderer': {}}]


def test_get_playlist_info_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                        client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'tabs': [{
                                 'tabRenderer': {
                                     'content': {
                                         'sectionListRenderer': {
                                             'contents': [{
                                                 'itemSectionRenderer': {
                                                     'contents': [{
                                                         'playlistVideoListRenderer': {
                                                             'contents': [{}, {
                                                                 'playlistVideoRenderer': {}
                                                             }, {
                                                                 'continuationItemRenderer': {
                                                                     'continuationEndpoint': {
                                                                         'continuationCommand': {
                                                                             'token': 'test_token'
                                                                         },
                                                                         'commandMetadata': {
                                                                             'webCommandMetadata': {
                                                                                 'apiUrl':
                                                                                     '/test_url'
                                                                             }
                                                                         }
                                                                     }
                                                                 }
                                                             }]
                                                         }
                                                     }]
                                                 }
                                             }]
                                         }
                                     }
                                 }
                             }]
                         }
                     }
                 })
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    requests_mock.post('https://www.youtube.com/test_url?prettyPrint=false',
                       response_list=[
                           {
                               'json': {
                                   'onResponseReceivedActions': [{
                                       'appendContinuationItemsAction': {
                                           'continuationItems': [{
                                               'playlistVideoRenderer': {}
                                           }, {
                                               'continuationItemRenderer': {
                                                   'continuationEndpoint': {
                                                       'continuationCommand': {
                                                           'token': 'test_token'
                                                       }
                                                   }
                                               }
                                           }]
                                       }
                                   }]
                               }
                           },
                           {
                               'json': {
                                   'onResponseReceivedActions': [{
                                       'appendContinuationItemsAction': {
                                           'continuationItems': [{}, {
                                               'playlistVideoRenderer': {}
                                           }]
                                       }
                                   }]
                               }
                           },
                       ])
    result = list(client.get_playlist_info(playlist_id='test_playlist'))
    assert result == [{
        'playlistVideoRenderer': {}
    }, {
        'playlistVideoRenderer': {}
    }, {
        'playlistVideoRenderer': {}
    }]


def test_get_playlist_info_empty(mocker: MockerFixture, requests_mock: Mocker,
                                 client: YouTubeClient) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'tabs': [{
                                 'tabRenderer': {
                                     'content': {
                                         'sectionListRenderer': {
                                             'contents': [{
                                                 'itemSectionRenderer': {
                                                     'contents': [{}]
                                                 }
                                             }]
                                         }
                                     }
                                 }
                             }]
                         }
                     }
                 })
    with pytest.raises(KeyError, match=r'This playlist might be empty\.'):
        list(client.get_playlist_info(playlist_id='test_playlist'))


def test_get_playlist_info_empty_alt(mocker: MockerFixture, requests_mock: Mocker,
                                     client: YouTubeClient) -> None:
    requests_mock.get('https://www.youtube.com/playlist?list=test_playlist', text='<html></html>')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'VISITOR_DATA': 'test_visitor_data',
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'SESSION_INDEX': 0,
                 })
    mocker.patch('youtube_unofficial.client.initial_data', return_value={'contents': {}})
    with pytest.raises(KeyError, match=r'twoColumnBrowseResultsRenderer'):
        list(client.get_playlist_info(playlist_id='test_playlist'))
