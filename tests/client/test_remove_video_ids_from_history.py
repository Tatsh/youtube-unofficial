from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
import json

from youtube_unofficial.constants import WATCH_HISTORY_URL

if TYPE_CHECKING:

    from pytest_mock import MockerFixture
    from requests_mock import Mocker
    from youtube_unofficial.client import YouTubeClient

DATA_PATH = Path(__file__).parent / 'remove-video-ids-data'


def test_remove_video_ids_from_history(mocker: MockerFixture, requests_mock: Mocker,
                                       client: YouTubeClient, data_path: Path) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg',
                 return_value={
                     'USER_SESSION_ID': 'test_session_id',
                     'INNERTUBE_API_KEY': 'test_api_key',
                     'INNERTUBE_CONTEXT_CLIENT_VERSION': '1.0',
                     'SESSION_INDEX': 0,
                     'VISITOR_DATA': 'test_visitor_data',
                 })
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=json.loads((data_path / 'remove-video-ids-00.json').read_text()))
    requests_mock.get(WATCH_HISTORY_URL, text='<html></html>')
    requests_mock.post('https://www.youtube.com/youtubei/v1/feedback',
                       json={'feedbackResponses': [{
                           'isProcessed': True
                       }]})
    result = client.remove_video_ids_from_history(['test_video', 'test_video2'])
    assert result is True
