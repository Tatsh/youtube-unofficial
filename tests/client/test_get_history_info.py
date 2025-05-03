from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.constants import WATCH_HISTORY_URL

if TYPE_CHECKING:

    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient


def test_get_history_info_no_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                          client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
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
                                                         'videoRenderer': {
                                                             'videoId': 'test_video'
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
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    result = list(client.get_history_info())
    assert result == [{'videoRenderer': {'videoId': 'test_video'}}]


def test_get_history_info_with_continuation(mocker: MockerFixture, requests_mock: Mocker,
                                            client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
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
                                                         'videoRenderer': {
                                                             'videoId': 'test_video'
                                                         }
                                                     }]
                                                 }
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
                                     }
                                 }
                             }]
                         }
                     }
                 })
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/browse',
                       json={
                           'onResponseReceivedActions': [{
                               'appendContinuationItemsAction': {
                                   'continuationItems': [{
                                       'itemSectionRenderer': {
                                           'contents': [{
                                               'videoRenderer': {
                                                   'videoId': 'test_video_2'
                                               }
                                           }]
                                       }
                                   }]
                               }
                           }]
                       })
    result = list(client.get_history_info())
    assert result == [{
        'videoRenderer': {
            'videoId': 'test_video'
        }
    }, {
        'videoRenderer': {
            'videoId': 'test_video_2'
        }
    }]


def test_get_history_info_no_videos(mocker: MockerFixture, requests_mock: Mocker,
                                    client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'DELEGATED_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'tabs': [{
                                 'tabRenderer': {
                                     'content': {
                                         'sectionListRenderer': {
                                             'contents': []
                                         }
                                     }
                                 }
                             }]
                         }
                     }
                 })
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    result = list(client.get_history_info())
    assert result == []
