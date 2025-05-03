from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.client import NoFeedbackToken, YouTubeClient
from youtube_unofficial.constants import WATCH_HISTORY_URL
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from requests_mock import Mocker


def test_clear_watch_history_no_feedback_token(mocker: MockerFixture, requests_mock: Mocker,
                                               client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value={})
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {}
                             }
                         }
                     }
                 })

    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post(
        'https://www.youtube.com/youtubei/v1/feedback',
        json={'status': 'STATUS_SUCCEEDED'},
    )

    with pytest.raises(NoFeedbackToken):
        client.clear_watch_history()


def test_clear_watch_history_clear_button_disabled(mocker: MockerFixture, requests_mock: Mocker,
                                                   client: YouTubeClient) -> None:
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {
                                     'contents': [{
                                         'buttonRenderer': {
                                             'isDisabled': True,
                                         }
                                     }]
                                 }
                             }
                         }
                     }
                 })
    assert client.clear_watch_history() is False


def test_clear_watch_history(mocker: MockerFixture, requests_mock: Mocker,
                             client: YouTubeClient) -> None:
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/feedback',
                       json={'feedbackResponses': [{
                           'isProcessed': True
                       }]})
    mocker.patch('youtube_unofficial.client.Soup')
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0'
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value={
                     'contents': {
                         'twoColumnBrowseResultsRenderer': {
                             'secondaryContents': {
                                 'browseFeedActionsRenderer': {
                                     'contents': [{
                                         'buttonRenderer': {
                                             'isDisabled': False
                                         }
                                     }, {
                                         'buttonRenderer': {
                                             'navigationEndpoint': {
                                                 'confirmDialogEndpoint': {
                                                     'content': {
                                                         'confirmDialogRenderer': {
                                                             'confirmEndpoint': {
                                                                 'feedbackEndpoint': {
                                                                     'feedbackToken': '',
                                                                 },
                                                                 'commandMetadata': {
                                                                     'webCommandMetadata': {
                                                                         'apiUrl':
                                                                             '/youtubei/v1/feedback'
                                                                     }
                                                                 },
                                                             }
                                                         }
                                                     }
                                                 }
                                             }
                                         }
                                     }]
                                 }
                             }
                         }
                     }
                 })
    assert client.clear_watch_history() is True
