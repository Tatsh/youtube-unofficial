from __future__ import annotations

from typing import TYPE_CHECKING

from youtube_unofficial.constants import WATCH_HISTORY_URL

if TYPE_CHECKING:

    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient


def test_toggle_history(mocker: MockerFixture, client: YouTubeClient,
                        requests_mock: Mocker) -> None:
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/feedback',
                       json={'feedbackResponses': [{
                           'isProcessed': True
                       }]})
    mock_session = mocker.MagicMock()
    mocker.patch('yt_dlp_utils.setup_session', return_value=mock_session)
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
                                     'contents': [{}, {}, {
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
    result = client.toggle_watch_history()
    assert result is True
