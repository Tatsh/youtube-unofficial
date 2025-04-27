from __future__ import annotations

from datetime import datetime, timezone
from time import sleep
from typing import TYPE_CHECKING, Any, Literal, cast
import hashlib
import json
import logging

from benedict import benedict
from bs4 import BeautifulSoup as Soup
from requests import HTTPError
from typing_extensions import overload
import yt_dlp_utils

from .constants import (
    USER_AGENT,
    WATCH_HISTORY_URL,
    WATCH_LATER_URL,
)
from .download import download_page
from .utils import context_client_body, find_ytcfg, initial_data, ytcfg_headers

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence

    from .typing.playlist import PlaylistInfo, PlaylistVideoListRenderer
    from .typing.ytcfg import YtcfgDict

__all__ = ('YouTubeClient',)

log = logging.getLogger(__name__)


class NoFeedbackToken(Exception):
    def __init__(self) -> None:
        super().__init__('No feedback token found.')


class YouTubeClient:
    """YouTube client for managing playlists and history."""

    HISTORY_MAX_RETRIES = 5
    """
    Max retries for history API calls. Used in :py:meth:`get_history_info`.


    :meta hide-value:
    """
    def __init__(self, browser: str, profile: str) -> None:
        self.session = yt_dlp_utils.setup_session(browser, profile, {'youtube.com', 'youtu.be'})
        """Requests session instance."""
        self.session.headers.update({'User-Agent': USER_AGENT})
        self._rsvi_cache: dict[str, Any] | None = None

    def remove_video_id_from_playlist(self,
                                      playlist_id: str,
                                      video_id: str,
                                      *,
                                      cache_values: bool | None = False) -> bool:
        """Remove a video from a playlist."""
        if cache_values and self._rsvi_cache:
            soup = self._rsvi_cache['soup']
            ytcfg = self._rsvi_cache['ytcfg']
            headers = self._rsvi_cache['headers']
        else:
            soup = self._download_page_soup(WATCH_LATER_URL)
            ytcfg = find_ytcfg(soup)
            headers = ytcfg_headers(ytcfg)
        if cache_values:
            self._rsvi_cache = {'soup': soup, 'ytcfg': ytcfg, 'headers': headers}

        action = {'removedVideoId': video_id, 'action': 'ACTION_REMOVE_VIDEO_BY_VIDEO_ID'}
        assert 'INNERTUBE_API_KEY' in ytcfg
        assert 'VISITOR_DATA' in ytcfg
        assert 'DELEGATED_SESSION_ID' in ytcfg or 'USER_SESSION_ID' in ytcfg
        delegated_session_id = ytcfg.get('DELEGATED_SESSION_ID')
        session_index = ytcfg.get('SESSION_INDEX')
        return cast(
            'bool',
            self._download_page(
                'https://www.youtube.com/youtubei/v1/browse/edit_playlist',
                method='post',
                params={'key': ytcfg['INNERTUBE_API_KEY']},
                headers={
                    'Authorization': self._authorization_sapisidhash_header(),
                    'x-goog-authuser': f'{session_index or 0}',
                    'x-origin': 'https://www.youtube.com',
                    'x-goog-visitor-id': ytcfg['VISITOR_DATA'],
                    'accept': '*/*',
                    'origin': 'https://www.youtube.com',
                    'referer': f'https://www.youtube.com/playlist?list={playlist_id}',
                } | ({
                    'x-goog-pageid': delegated_session_id
                } if delegated_session_id else {}),
                json={
                    'actions': [action],
                    'playlistId': playlist_id,
                    'params': 'CAFAAQ%3D%3D',
                    'context': {
                        'client': context_client_body(ytcfg),
                        'request': {
                            'consistencyTokenJars': [],
                            'internalExperimentFlags': []
                        },
                    }
                },
                return_json=True)['status'] == 'STATUS_SUCCEEDED')

    def remove_set_video_id_from_playlist(self,
                                          playlist_id: str,
                                          set_video_id: str,
                                          *,
                                          cache_values: bool | None = False) -> bool:
        """Remove a video from a playlist by its *setVideoId*."""
        if cache_values and self._rsvi_cache:
            soup = self._rsvi_cache['soup']
            ytcfg = self._rsvi_cache['ytcfg']
            headers = self._rsvi_cache['headers']
        else:
            soup = self._download_page_soup(WATCH_LATER_URL)
            ytcfg = find_ytcfg(soup)
            headers = ytcfg_headers(ytcfg)
        if cache_values:
            self._rsvi_cache = {'soup': soup, 'ytcfg': ytcfg, 'headers': headers}
        assert 'INNERTUBE_API_KEY' in ytcfg
        assert 'VISITOR_DATA' in ytcfg
        assert 'DELEGATED_SESSION_ID' in ytcfg or 'USER_SESSION_ID' in ytcfg
        return cast(
            'bool',
            benedict(
                self._download_page(
                    'https://www.youtube.com/youtubei/v1/browse/edit_playlist',
                    method='post',
                    params={'key': ytcfg['INNERTUBE_API_KEY']},
                    headers={
                        'Authorization': self._authorization_sapisidhash_header(),
                        'x-goog-authuser': f'{ytcfg.get("SESSION_INDEX", 0)}',
                        'x-origin': 'https://www.youtube.com',
                        'x-goog-visitor-id': ytcfg['VISITOR_DATA'],
                        'accept': '*/*',
                        'origin': 'https://www.youtube.com',
                        'referer': f'https://www.youtube.com/playlist?list={playlist_id}',
                    } | ({
                        'x-goog-pageid': ytcfg['DELEGATED_SESSION_ID']
                    } if ytcfg.get('DELEGATED_SESSION_ID') else {}),
                    json={
                        'actions': [{
                            'action': 'ACTION_REMOVE_VIDEO',
                            'setVideoId': set_video_id,
                        }],
                        'playlistId': playlist_id,
                        'params': 'CAFAAQ%3D%3D',
                        'context': {
                            'client': context_client_body(ytcfg),
                            'request': {
                                'consistencyTokenJars': [],
                                'internalExperimentFlags': [],
                                'useSsl': True
                            },
                            'user': {
                                'lockedSafetyMode': False
                            }
                        }
                    },
                    return_json=True))['status'] == 'STATUS_SUCCEEDED')

    def clear_watch_history(self) -> bool:
        """Clear watch history."""
        content = self._download_page_soup(WATCH_HISTORY_URL)
        ytcfg = find_ytcfg(content)
        init_data = benedict(initial_data(content))
        # If there are no videos, there is no search and index is 0.
        path_prefix = ('contents.twoColumnBrowseResultsRenderer.secondaryContents.'
                       'browseFeedActionsRenderer')
        if init_data.get(f'{path_prefix}.contents[0].buttonRenderer.isDisabled'):
            log.debug('Clear button is disabled.')
            return False
        feedback_endpoint_path = (
            f'{path_prefix}.contents[1].buttonRenderer.navigationEndpoint.'
            'confirmDialogEndpoint.content.confirmDialogRenderer.confirmEndpoint.'
            'feedbackEndpoint')
        expected_path = (f'{feedback_endpoint_path}.feedbackToken')
        try:
            init_data[expected_path]
        except KeyError as e:
            raise NoFeedbackToken from e
        return cast('bool', self._single_feedback_api_call(ytcfg, init_data[expected_path]))

    def get_playlist_info(self, playlist_id: str) -> Iterator[PlaylistInfo]:
        """Get playlist information."""
        url = f'https://www.youtube.com/playlist?list={playlist_id}'
        content = self._download_page_soup(url)
        ytcfg = find_ytcfg(content)
        ytcfg_headers(ytcfg)
        yt_init_data = initial_data(content)
        video_list_renderer: PlaylistVideoListRenderer | None = None
        try:
            video_list_renderer = (
                yt_init_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']
                ['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                [0]['playlistVideoListRenderer'])
        except KeyError as e:
            if e.args[0] == 'playlistVideoListRenderer':
                msg = 'This playlist might be empty.'
                raise KeyError(msg) from e
            raise
        assert video_list_renderer is not None
        try:
            for item in video_list_renderer['contents']:
                if 'playlistVideoRenderer' in item:
                    yield item
                elif 'continuationItemRenderer' in item:
                    break
        except KeyError:
            yield from []
        endpoint = continuation = api_url = None
        try:
            endpoint = (video_list_renderer['contents'][-1]['continuationItemRenderer']
                        ['continuationEndpoint'])
            api_url = endpoint['commandMetadata']['webCommandMetadata']['apiUrl']
            continuation = endpoint['continuationCommand']['token']
        except KeyError:
            pass
        if continuation and api_url:
            while True:
                contents = benedict(
                    self._single_feedback_api_call(ytcfg,
                                                   api_url=api_url,
                                                   merge_json={'continuation': continuation},
                                                   return_is_processed=False))
                assert 'onResponseReceivedActions' in contents
                items = contents['onResponseReceivedActions[0].appendContinuationItemsAction.'
                                 'continuationItems']
                for item in items:
                    if 'playlistVideoRenderer' in item:
                        yield item
                    elif 'continuationItemRenderer' in item:
                        try:
                            endpoint = (video_list_renderer['contents'][-1]
                                        ['continuationItemRenderer']['continuationEndpoint'])
                            continuation = endpoint['continuationCommand']['token']
                        except KeyError:
                            pass
                        break
                if 'continuationItemRenderer' not in items[-1]:
                    break

    def clear_playlist(self, playlist_id: str) -> None:
        """
        Remove all videos from the specified playlist.

        Use `WL` for Watch Later.
        """
        playlist_info = self.get_playlist_info(playlist_id)
        try:
            video_ids = [x['playlistVideoRenderer']['videoId'] for x in playlist_info]
        except KeyError:
            log.info('Caught KeyError. This probably means the playlist is empty.')
            return
        for video_id in video_ids:
            log.debug('Deleting from playlist: video_id = %s', video_id)
            self.remove_video_id_from_playlist(playlist_id, video_id)

    def clear_watch_later(self) -> None:
        """Remove all videos from the 'Watch Later' playlist."""
        self.clear_playlist('WL')

    def get_history_info(self) -> Iterator[Mapping[str, Any]]:
        """Get information about the History playlist."""
        content = self._download_page_soup(WATCH_HISTORY_URL)
        init_data = initial_data(content)
        ytcfg = find_ytcfg(content)
        section_list_renderer = (init_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]
                                 ['tabRenderer']['content']['sectionListRenderer'])
        next_continuation = None
        for section_list in section_list_renderer['contents']:
            try:
                yield from section_list['itemSectionRenderer']['contents']
            except KeyError:  # noqa: PERF203
                if 'continuationItemRenderer' in section_list:
                    next_continuation = {
                        'continuation': (section_list['continuationItemRenderer']
                                         ['continuationEndpoint']['continuationCommand']['token'])
                    }
                    break
        if not next_continuation:
            try:
                next_continuation = (
                    section_list_renderer['continuations'][0]['nextContinuationData'])
            except KeyError:
                return
        assert next_continuation is not None
        params = {
            'continuation': next_continuation['continuation'],
            'ctoken': next_continuation['continuation']
        }
        resp = None
        while True:
            tries = 0
            time = 0
            last_exception = None
            while tries < self.HISTORY_MAX_RETRIES:
                if time:
                    sleep(time)
                try:
                    resp = self._single_feedback_api_call(
                        ytcfg,
                        api_url='/youtubei/v1/browse',
                        merge_json={'continuation': params['continuation']},
                        return_is_processed=False)
                    break
                except HTTPError as e:
                    last_exception = e
                    tries += 1
                    time = 2 ** tries
            if last_exception:
                log.debug('Caught HTTP error: %s, text: %s', last_exception,
                          last_exception.response.text)
                break
            assert resp is not None
            contents = cast('dict[str, Any]', resp)
            try:
                section_list_renderer = (contents['onResponseReceivedActions'][0]
                                         ['appendContinuationItemsAction']['continuationItems'])
            except KeyError as e:
                log.debug('Caught KeyError: %s. Possible keys: %s', e, ', '.join(contents.keys()))
                break
            continuations = None
            for section_list in section_list_renderer:
                try:
                    yield from section_list['itemSectionRenderer']['contents']
                except KeyError:  # noqa: PERF203
                    if 'continuationItemRenderer' in section_list:
                        continuations = [{
                            'nextContinuationData': {
                                'continuation': (
                                    section_list['continuationItemRenderer']['continuationEndpoint']
                                    ['continuationCommand']['token']),
                                'clickTrackingParams': (
                                    section_list['continuationItemRenderer']['continuationEndpoint']
                                    ['clickTrackingParams'])
                            }
                        }]
                        break
                    raise
            if not continuations:
                try:
                    continuations = section_list_renderer['continuations']
                except KeyError as e:
                    # Probably the end of the history
                    log.debug('Caught KeyError: %s. Possible keys: %s', e,
                              ', '.join(section_list_renderer.keys()))
                    break
                except TypeError as e:
                    # Probably the end of the history
                    log.debug(
                        'Caught TypeError evaluating '
                        '"section_list_renderer[\'continuations\']": %s', e)
                    break
            assert continuations is not None
            next_cont = continuations[0]['nextContinuationData']
            params['itct'] = next_cont['clickTrackingParams']
            params['ctoken'] = next_cont['continuation']
            params['continuation'] = next_cont['continuation']

    def remove_video_ids_from_history(self, video_ids: Sequence[str]) -> bool:
        """Delete a history entry by video ID."""
        if not video_ids:
            return False
        history_info = self.get_history_info()
        content = self._download_page_soup(WATCH_HISTORY_URL)
        ytcfg = find_ytcfg(content)
        entries = [x for x in history_info if x['videoRenderer']['videoId'] in video_ids]
        if not entries:
            return False
        codes = [
            self._single_feedback_api_call(
                ytcfg,
                benedict(entry)['videoRenderer.menu.menuRenderer.topLevelButtons[0].'
                                'buttonRenderer.serviceEndpoint.feedbackEndpoint.'
                                'feedbackToken'],
            ) for entry in entries
        ]
        return all(codes)

    def _authorization_sapisidhash_header(self, ytcfg: YtcfgDict | None = None) -> str:
        now = int(datetime.now(timezone.utc).timestamp())
        sapisid = (self.session.cookies.get('SAPISID', domain='.youtube.com')
                   or self.session.cookies.get('__Secure-3PAPISID', domain='.youtube.com')
                   or self.session.cookies.get('__Secure-1PAPISID', domain='.youtube.com'))
        assert sapisid is not None
        if ytcfg:
            m = hashlib.sha1(' '.join(  # noqa: S324
                [ytcfg['USER_SESSION_ID'],
                 str(now), sapisid, 'https://www.youtube.com']).encode())
            a = '_'.join([str(now), m.hexdigest(), 'u'])
            return ' '.join(
                f'{type_} {a}' for type_ in ('SAPISIDHASH', 'SAPISID1PHASH', 'SAPISID3PHASH'))
        m = hashlib.sha1(f'{now} {sapisid} https://www.youtube.com'.encode())  # noqa: S324
        return f'SAPISIDHASH {now}_{m.hexdigest()}'

    def _single_feedback_api_call(self,
                                  ytcfg: YtcfgDict,
                                  feedback_token: str = '',
                                  api_url: str = '/youtubei/v1/feedback',
                                  merge_json: dict[str, Any] | None = None,
                                  click_tracking_params: str | None = None,
                                  *,
                                  return_is_processed: bool = True) -> dict[str, Any] | bool:
        if not merge_json:
            merge_json = {}
        feedback_token_part = {
            'feedbackTokens': [feedback_token],
            'isFeedbackTokenUnencrypted': False,
            'shouldMerge': False
        } if feedback_token else {}
        api_url = f'https://www.youtube.com{api_url}'
        log.debug('API URL: %s', api_url)
        assert 'DELEGATED_SESSION_ID' in ytcfg or 'USER_SESSION_ID' in ytcfg
        delegated_session_id = ytcfg.get('DELEGATED_SESSION_ID')
        headers = {
            'Authorization': self._authorization_sapisidhash_header(ytcfg),
            'x-goog-authuser': f'{ytcfg.get("SESSION_INDEX", 0)}',
            'x-origin': 'https://www.youtube.com',
            'X-Youtube-Bootstrap-Logged-In': 'true',
        } | ({
            'x-goog-pageid': delegated_session_id
        } if delegated_session_id else {})
        log.debug('Request headers: %s', headers)
        json_data = {
            'context': {
                'client': context_client_body(ytcfg),
            } | ({
                'clickTracking': {
                    'clickTrackingParams': click_tracking_params
                }
            } if click_tracking_params else {})
        } | feedback_token_part | merge_json
        log.debug('Request JSON: %s', json.dumps(json_data, indent=2, sort_keys=True))
        ret = self._download_page(api_url,
                                  method='post',
                                  params={'prettyPrint': 'false'},
                                  headers=headers,
                                  json=json_data,
                                  return_json=True)
        log.debug('Response JSON: %s', json.dumps(ret, indent=2, sort_keys=True))
        if benedict(ret).get('responseContext.mainAppWebResponseContext.loggedOut'):
            msg = ('Response indicates logged out. '
                   'Please check your cookies and try again.')
            raise RuntimeError(msg)
        if return_is_processed:
            try:
                return cast('bool', ret['feedbackResponses'][0]['isProcessed'])
            except KeyError:
                return False
        return ret

    def _toggle_history(self, page_url: str, contents_index: int) -> bool:
        content = self._download_page_soup(page_url)
        ytcfg = find_ytcfg(content)
        info = benedict(
            initial_data(content))['contents.twoColumnBrowseResultsRenderer.'
                                   'secondaryContents.browseFeedActionsRenderer.contents'
                                   f'[{contents_index}].buttonRenderer.navigationEndpoint.'
                                   'confirmDialogEndpoint.content.confirmDialogRenderer.'
                                   'confirmEndpoint']
        return cast(
            'bool',
            self._single_feedback_api_call(ytcfg, info['feedbackEndpoint']['feedbackToken'],
                                           info['commandMetadata']['webCommandMetadata']['apiUrl']))

    def toggle_watch_history(self) -> bool:
        """Pauses or resumes watch history depending on the current state."""
        return self._toggle_history(WATCH_HISTORY_URL, 2)

    @overload
    def _download_page(self,
                       url: str,
                       data: Any = None,
                       method: Literal['get', 'post'] = 'get',
                       headers: Mapping[str, str] | None = None,
                       params: Mapping[str, str] | None = None,
                       json: Any = None,
                       *,
                       return_json: Literal[False] = False) -> str:  # pragma: no cover
        ...

    @overload
    def _download_page(self,
                       url: str,
                       data: Any = None,
                       method: Literal['get', 'post'] = 'get',
                       headers: Mapping[str, str] | None = None,
                       params: Mapping[str, str] | None = None,
                       json: Any = None,
                       *,
                       return_json: Literal[True]) -> dict[str, Any]:  # pragma: no cover
        ...

    @overload
    def _download_page(self,
                       url: str,
                       data: Any = None,
                       method: Literal['get', 'post'] = 'get',
                       headers: Mapping[str, str] | None = None,
                       params: Mapping[str, str] | None = None,
                       json: Any = None,
                       *,
                       return_json: bool = False) -> str | dict[str, Any]:
        return download_page(self.session,
                             url,
                             data,
                             method,
                             headers,
                             params,
                             json,
                             return_json=return_json)

    def _download_page_soup(self, *args: Any, **kwargs: Any) -> Soup:
        return Soup(cast('str', self._download_page(*args, **kwargs)),
                    kwargs.pop('parser', 'html5lib'))
