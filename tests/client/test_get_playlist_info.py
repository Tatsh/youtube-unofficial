from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from youtube_unofficial.client import YouTubeClient


def _ytcfg() -> dict[str, str | int]:
    return {
        'INNERTUBE_API_KEY': 'test_api_key',
        'VISITOR_DATA': 'test_visitor_data',
        'USER_SESSION_ID': 'test_session_id',
        'SESSION_INDEX': 0
    }


def _playlist_initial_with_continuation() -> dict[str, object]:
    return {
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
                                                    'playlistVideoRenderer': {
                                                        'videoId': 'v1'
                                                    }
                                                }, {
                                                    'continuationItemRenderer': {
                                                        'continuationEndpoint': {
                                                            'commandMetadata': {
                                                                'webCommandMetadata': {
                                                                    'apiUrl': '/youtubei/v1/test'
                                                                }
                                                            },
                                                            'continuationCommand': {
                                                                'token': 'tok'
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
    }


def _continuation_api_page(*, items: list[dict[str, object]]) -> dict[str, object]:
    return {
        'onResponseReceivedActions': [{
            'appendContinuationItemsAction': {
                'continuationItems': items
            }
        }]
    }


@pytest.mark.anyio
async def test_get_playlist_info_re_raises_non_playlist_key_error(mocker: MockerFixture,
                                                                  client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data', return_value={'contents': {}})
    with pytest.raises(KeyError) as exc_info:
        async for _ in client.get_playlist_info('PLx'):
            pass
    assert exc_info.value.args[0] == 'twoColumnBrowseResultsRenderer'


@pytest.mark.anyio
async def test_get_playlist_info_renderer_null(mocker: MockerFixture,
                                               client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
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
                                                         'playlistVideoListRenderer': None
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
    with pytest.raises(RuntimeError, match='Expected playlist video list renderer'):
        async for _ in client.get_playlist_info('PLx'):
            pass


@pytest.mark.anyio
async def test_get_playlist_info_continuation_response_not_dict(mocker: MockerFixture,
                                                                client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=_playlist_initial_with_continuation())
    mocker.patch.object(client, '_single_feedback_api_call', return_value=[])
    with pytest.raises(TypeError, match='Expected dict response from continuation API'):
        async for _ in client.get_playlist_info('PLx'):
            pass


@pytest.mark.anyio
async def test_get_playlist_info_yields_then_breaks_on_continuation_item(
        mocker: MockerFixture, client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
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
                                                                 'playlistVideoRenderer': {
                                                                     'videoId': 'head'
                                                                 }
                                                             }, {
                                                                 'continuationItemRenderer': {
                                                                     'continuationEndpoint': {
                                                                         'commandMetadata': {
                                                                             'webCommandMetadata': {
                                                                                 'apiUrl': '/x'
                                                                             }
                                                                         },
                                                                         'continuationCommand': {
                                                                             'token': 't0'
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
    mocker.patch.object(client,
                        '_single_feedback_api_call',
                        return_value=_continuation_api_page(items=[{
                            'playlistVideoRenderer': {
                                'videoId': 'from_api'
                            }
                        }]))
    out = [x async for x in client.get_playlist_info('PLx')]
    assert out == [{
        'playlistVideoRenderer': {
            'videoId': 'head'
        }
    }, {
        'playlistVideoRenderer': {
            'videoId': 'from_api'
        }
    }]


@pytest.mark.anyio
async def test_get_playlist_info_continuation_updates_token_then_stops(
        mocker: MockerFixture, client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=_playlist_initial_with_continuation())

    call_n = {'n': 0}

    def _responses(*_: object, **__: object) -> dict[str, object]:
        if call_n['n'] == 0:
            call_n['n'] += 1
            return _continuation_api_page(items=[{}, {
                'playlistVideoRenderer': {
                    'videoId': 'page1'
                }
            }, {
                'continuationItemRenderer': {
                    'continuationEndpoint': {
                        'continuationCommand': {
                            'token': 'tok2'
                        }
                    }
                }
            }])
        call_n['n'] += 1
        return _continuation_api_page(items=[{'playlistVideoRenderer': {'videoId': 'page2'}}])

    mocker.patch.object(client, '_single_feedback_api_call', side_effect=_responses)
    out = [x async for x in client.get_playlist_info('PLx')]
    assert [x['playlistVideoRenderer']['videoId'] for x in out] == ['v1', 'page1', 'page2']


@pytest.mark.anyio
async def test_get_playlist_info_breaks_when_continuation_first(mocker: MockerFixture,
                                                                client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
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
                                                                 'continuationItemRenderer': {
                                                                     'continuationEndpoint': {
                                                                         'commandMetadata': {
                                                                             'webCommandMetadata': {
                                                                                 'apiUrl': '/x'
                                                                             }
                                                                         },
                                                                         'continuationCommand': {
                                                                             'token': 't'
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
    mocker.patch.object(client,
                        '_single_feedback_api_call',
                        return_value={
                            'onResponseReceivedActions': [{
                                'appendContinuationItemsAction': {
                                    'continuationItems': [{
                                        'playlistVideoRenderer': {
                                            'videoId': 'c1'
                                        }
                                    }]
                                }
                            }]
                        })
    out = [x async for x in client.get_playlist_info('PLx')]
    assert out == [{'playlistVideoRenderer': {'videoId': 'c1'}}]


@pytest.mark.anyio
async def test_get_playlist_info_continuation_missing_actions(mocker: MockerFixture,
                                                              client: YouTubeClient) -> None:
    mocker.patch('youtube_unofficial.client.find_ytcfg', return_value=_ytcfg())
    mocker.patch('youtube_unofficial.client.download_page',
                 new_callable=AsyncMock,
                 return_value='<html></html>')
    mocker.patch('youtube_unofficial.client.initial_data',
                 return_value=_playlist_initial_with_continuation())
    mocker.patch.object(client, '_single_feedback_api_call', return_value={})
    with pytest.raises(KeyError, match='onResponseReceivedActions'):
        async for _ in client.get_playlist_info('PLx'):
            pass
