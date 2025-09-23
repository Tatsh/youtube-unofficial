"""Client library."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from operator import itemgetter
from typing import TYPE_CHECKING, Any, Literal, cast
import hashlib
import json
import logging

from bs4 import BeautifulSoup as Soup
from typing_extensions import overload
import yt_dlp_utils

from .constants import (
    EXTRACTED_THUMBNAIL_KEYS,
    HISTORY_ENTRY_KEYS_TO_SKIP,
    SIMPLE_TEXT_KEYS,
    TEXT_RUNS_KEYS,
    USER_AGENT,
    WATCH_HISTORY_URL,
    WATCH_LATER_URL,
)
from .download import download_page
from .typing.playlist import PlaylistVideoIDsEntry
from .utils import (
    context_client_body,
    extract_keys,
    find_ytcfg,
    get_text_runs,
    initial_data,
    ytcfg_headers,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from .typing.history import (
        DescriptionSnippet,
        HistoryVideoIDsEntry,
        MetadataBadgeRendererTop,
    )
    from .typing.playlist import PlaylistInfo, PlaylistVideoListRenderer
    from .typing.ytcfg import YtcfgDict

__all__ = ('NoFeedbackToken', 'YouTubeClient')

log = logging.getLogger(__name__)


class NoFeedbackToken(Exception):
    """No feedback token found."""
    def __init__(self) -> None:
        super().__init__('No feedback token found.')


class YouTubeClient:
    """YouTube client for managing playlists and history."""
    def __init__(self, browser: str, profile: str) -> None:
        """
        Initialise the client.

        Parameters
        ----------
        browser : str
            The browser to use.
        profile : str
            The profile to use.
        """
        self.session = yt_dlp_utils.setup_session(browser,
                                                  profile,
                                                  domains={'.youtube.com'},
                                                  setup_retry=True)
        """Requests :py:class:`requests.Session` instance."""
        self.session.headers.update({'User-Agent': USER_AGENT})
        self._rsvi_cache: dict[str, Any] | None = None

    def remove_video_id_from_playlist(self,
                                      playlist_id: str,
                                      video_id: str,
                                      *,
                                      cache_values: bool | None = False) -> bool:
        """
        Remove a video from a playlist.

        Parameters
        ----------
        playlist_id : str
            The ID of the playlist.
        video_id : str
            The ID of the video to remove.
        cache_values : bool | None
            If ``True``, cache the values of the page and ytcfg. This is useful for performance
            reasons, but may cause issues if updates are needed.

        Returns
        -------
        bool
            ``True`` if the operation was successful, ``False`` otherwise.
        """
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
        """
        Remove a video from a playlist by its *setVideoId*.

        Parameters
        ----------
        playlist_id : str
            The ID of the playlist.
        set_video_id : str
            The *setVideoId* of the video to remove.
        cache_values : bool | None
            If ``True``, cache the values of the page and ytcfg. This is useful for performance
            reasons, but may cause issues if updates are needed.

        Returns
        -------
        bool
            ``True`` if the operation was successful, ``False`` otherwise.
        """
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
                return_json=True)['status'] == 'STATUS_SUCCEEDED')

    def clear_watch_history(self) -> bool:
        """
        Clear watch history.

        Returns
        -------
        bool
            ``True`` if the operation was successful, ``False`` otherwise.

        Raises
        ------
        NoFeedbackToken
        """
        content = self._download_page_soup(WATCH_HISTORY_URL)
        ytcfg = find_ytcfg(content)
        init_data = initial_data(content)
        # If there are no videos, there is no search and index is 0.
        browse_feed_actions_renderer = (init_data['contents']['twoColumnBrowseResultsRenderer']
                                        ['secondaryContents']['browseFeedActionsRenderer'])
        try:
            if browse_feed_actions_renderer['contents'][0]['buttonRenderer']['isDisabled']:
                log.debug('Clear history button is disabled.')
                return False
        except (IndexError, KeyError):
            pass
        try:
            feedback_token = (
                browse_feed_actions_renderer['contents'][1]['buttonRenderer']['navigationEndpoint']
                ['confirmDialogEndpoint']['content']['confirmDialogRenderer']['confirmEndpoint']
                ['feedbackEndpoint']['feedbackToken'])
        except (IndexError, KeyError) as e:
            raise NoFeedbackToken from e
        return cast('bool', self._single_feedback_api_call(ytcfg, feedback_token))

    def get_playlist_info(self, playlist_id: str) -> Iterator[PlaylistInfo]:
        """
        Get playlist information.

        Parameters
        ----------
        playlist_id : str
            The ID of the playlist.

        Yields
        ------
        PlaylistInfo
            The playlist information.

        Raises
        ------
        KeyError
        """
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
                contents = self._single_feedback_api_call(ytcfg,
                                                          api_url=api_url,
                                                          merge_json={'continuation': continuation},
                                                          return_is_processed=False)
                assert isinstance(contents, dict)
                assert 'onResponseReceivedActions' in contents
                items = contents['onResponseReceivedActions'][0]['appendContinuationItemsAction'][
                    'continuationItems']
                for item in items:
                    if 'playlistVideoRenderer' in item:
                        yield item
                    elif 'continuationItemRenderer' in item:
                        endpoint = item['continuationItemRenderer']['continuationEndpoint']
                        continuation = endpoint['continuationCommand']['token']
                        break
                if 'continuationItemRenderer' not in items[-1]:
                    break

    @overload
    def get_playlist_video_ids(self, playlist_id: str) -> Iterator[str]:  # pragma: no cover
        ...

    @overload
    def get_playlist_video_ids(
            self, playlist_id: str, *,
            return_dict: Literal[True]) -> Iterator[PlaylistVideoIDsEntry]:  # pragma: no cover
        ...

    @overload
    def get_playlist_video_ids(self, playlist_id: str, *,
                               return_dict: Literal[False]) -> Iterator[str]:  # pragma: no cover
        ...

    def get_playlist_video_ids(
            self,
            playlist_id: str,
            *,
            return_dict: bool = False) -> Iterator[str] | Iterator[PlaylistVideoIDsEntry]:
        """
        Get video IDs from a playlist.

        Parameters
        ----------
        playlist_id : str
            The ID of the playlist.
        return_dict : bool
            If ``True``, yield dictionaries.

        Yields
        ------
        str | PlaylistVideoIDsEntry
            The video IDs or dictionaries with video information.
        """
        for item in self.get_playlist_info(playlist_id):
            renderer = item['playlistVideoRenderer']
            if 'videoId' not in renderer:
                continue
            owner = title = None
            if 'shortBylineText' in renderer:
                if 'runs' in renderer['shortBylineText']:
                    owner = ' - '.join(map(itemgetter('text'), renderer['shortBylineText']['runs']))
                elif 'text' in renderer['shortBylineText']:
                    owner = renderer['shortBylineText']['text']
            if 'title' in renderer:
                if 'simpleText' in renderer['title']:
                    title = renderer['title']['simpleText']
                elif 'runs' in renderer['title']:
                    title = ' - '.join(map(itemgetter('text'), renderer['title']['runs']))
            if return_dict:
                yield PlaylistVideoIDsEntry(
                    owner=owner,
                    title=title,
                    video_id=renderer['videoId'],
                    watch_url=f'https://www.youtube.com/watch?v={renderer["videoId"]}')
            else:
                yield renderer['videoId']

    def clear_playlist(self, playlist_id: str) -> None:
        """
        Remove all videos from the specified playlist.

        Use `WL` for Watch Later.

        Parameters
        ----------
        playlist_id : str
            The ID of the playlist.
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

    def get_history_info(self) -> Iterator[dict[str, Any]]:
        """
        Get information about the History playlist.

        Yields
        ------
        dict[str, Any]
            The history information.
        """
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
        while True:
            resp = self._single_feedback_api_call(
                ytcfg,
                api_url='/youtubei/v1/browse',
                merge_json={'continuation': params['continuation']},
                return_is_processed=False)
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
                        continuations = {
                            'continuation': (
                                section_list['continuationItemRenderer']['continuationEndpoint']
                                ['continuationCommand']['token']),
                            'clickTrackingParams': (section_list['continuationItemRenderer']
                                                    ['continuationEndpoint']['clickTrackingParams'])
                        }
                    break
            if not continuations:
                log.info('Likely hit the end of watch history.')
                break
            params['itct'] = continuations['clickTrackingParams']
            params['ctoken'] = continuations['continuation']
            params['continuation'] = continuations['continuation']

    @overload
    def get_history_video_ids(self) -> Iterator[str]:  # pragma: no cover
        ...

    @overload
    def get_history_video_ids(
            self,
            *,
            return_dict: Literal[True] = True
    ) -> Iterator[HistoryVideoIDsEntry]:  # pragma: no cover
        ...

    @overload
    def get_history_video_ids(self,
                              *,
                              return_dict: Literal[False] = False
                              ) -> Iterator[str]:  # pragma: no cover
        ...

    def get_history_video_ids(  # noqa: C901
            self, *, return_dict: bool = False) -> Iterator[str] | Iterator[HistoryVideoIDsEntry]:
        """
        Get video IDs from the History playlist.

        Yields
        ------
        str
            The video IDs.
        """
        def is_verified(owner_badges: Iterable[MetadataBadgeRendererTop]) -> bool:
            for badge in (x['metadataBadgeRenderer'] for x in owner_badges):
                if badge['style'] == 'BADGE_STYLE_TYPE_VERIFIED':
                    return True
            return False

        for entry in self.get_history_info():
            d: dict[str, Any] = {}
            if 'videoId' not in entry.get('videoRenderer', {}):
                continue
            if return_dict:
                for k, v in sorted(entry.get('videoRenderer', {}).items()):
                    if k in HISTORY_ENTRY_KEYS_TO_SKIP:
                        continue
                    if k == 'videoId':
                        assert isinstance(v, str)
                        d['video_id'] = v
                    elif isinstance(v, int | str | float | bool):
                        d[k] = v
                    elif k in TEXT_RUNS_KEYS and isinstance(v, Mapping):
                        d[TEXT_RUNS_KEYS[k]] = get_text_runs(cast('DescriptionSnippet', v))
                    elif k == 'richThumbnail' and isinstance(v, Mapping):
                        if 'moving_thumbnails' not in d:  # pragma: no cover
                            d['moving_thumbnails'] = []
                        d['moving_thumbnails'] += [
                            extract_keys(EXTRACTED_THUMBNAIL_KEYS, t) for t in
                            v['movingThumbnailRenderer']['movingThumbnailDetails']['thumbnails']
                        ]
                    elif k == 'channelThumbnailSupportedRenderers' and isinstance(v, Mapping):
                        if 'video_thumbnails' not in d:  # pragma: no cover
                            d['video_thumbnails'] = []
                        d['video_thumbnails'] += [
                            extract_keys(EXTRACTED_THUMBNAIL_KEYS, t) for t in
                            v['channelThumbnailWithLinkRenderer']['thumbnail']['thumbnails']
                        ]
                    elif k in SIMPLE_TEXT_KEYS and isinstance(v, Mapping):
                        d[SIMPLE_TEXT_KEYS[k]] = v['simpleText']
                    elif k == 'lengthText' and isinstance(v, Mapping):
                        d['length_accessible'] = v['accessibility']['accessibilityData']['label']
                        d['length'] = v['simpleText']
                    elif k == 'ownerBadges' and isinstance(v, Iterable):
                        d['verified'] = is_verified(v)
                    elif k == 'thumbnail' and isinstance(v, Mapping):
                        if 'video_thumbnails' not in d:  # pragma: no cover
                            d['video_thumbnails'] = []
                        d['video_thumbnails'] += [
                            extract_keys(EXTRACTED_THUMBNAIL_KEYS, t) for t in v['thumbnails']
                        ]
                d['watch_url'] = f'https://www.youtube.com/watch?v={d["video_id"]}'
                yield cast('HistoryVideoIDsEntry', d)
            else:
                yield entry['videoRenderer']['videoId']

    def remove_video_ids_from_history(self, video_ids: Sequence[str]) -> bool:
        """
        Delete a history entry by video ID.

        Parameters
        ----------
        video_ids : Sequence[str]
            The video IDs to delete.

        Returns
        -------
        bool
            ``True`` if the operation was successful, ``False`` otherwise.
        """
        if not video_ids:
            return False
        history_info = self.get_history_info()
        content = self._download_page_soup(WATCH_HISTORY_URL)
        ytcfg = find_ytcfg(content)
        entries = [x for x in history_info if x['videoRenderer']['videoId'] in video_ids]
        if not entries:
            return False
        return all(
            self._single_feedback_api_call(
                ytcfg, entry['videoRenderer']['menu']['menuRenderer']['topLevelButtons'][0]
                ['buttonRenderer']['serviceEndpoint']['feedbackEndpoint']['feedbackToken'])
            for entry in entries)

    def _authorization_sapisidhash_header(self, ytcfg: YtcfgDict | None = None) -> str:
        now = int(datetime.now(timezone.utc).timestamp())
        sapisid = self.session.cookies.get(
            '__Secure-3PAPISID',
            self.session.cookies.get('SAPISID', self.session.cookies.get('__Secure-1PAPISID')))
        assert sapisid is not None
        if ytcfg:
            session_id = ytcfg['USER_SESSION_ID']
            # session_id = ytcfg.get('DELEGATED_SESSION_ID', ytcfg.get('USER_SESSION_ID'))  # noqa: E501, ERA001
            # assert session_id is not None
            m = hashlib.sha1(' '.join(  # noqa: S324
                (session_id, str(now), sapisid, 'https://www.youtube.com')).encode())
            a = '_'.join((str(now), m.hexdigest(), 'u'))
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
        if ret.get('responseContext', {}).get('mainAppWebResponseContext', {}).get(
                'loggedOut', False):
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
        info = (initial_data(content)['contents']['twoColumnBrowseResultsRenderer']
                ['secondaryContents']['browseFeedActionsRenderer']['contents'][contents_index]
                ['buttonRenderer']['navigationEndpoint']['confirmDialogEndpoint']['content']
                ['confirmDialogRenderer']['confirmEndpoint'])
        return cast(
            'bool',
            self._single_feedback_api_call(ytcfg, info['feedbackEndpoint']['feedbackToken'],
                                           info['commandMetadata']['webCommandMetadata']['apiUrl']))

    def toggle_watch_history(self) -> bool:
        """
        Pauses or resumes watch history depending on the current state.

        Returns
        -------
        bool
            ``True`` if the operation was successful, ``False`` otherwise.
        """
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

    def _download_page(self,
                       url: str,
                       data: Any = None,
                       method: Literal['get', 'post'] = 'get',
                       headers: Mapping[str, str] | None = None,
                       params: Mapping[str, str] | None = None,
                       json: Any = None,
                       *,
                       return_json: bool = False) -> str | dict[str, Any]:
        return download_page(  # type: ignore[call-overload,no-any-return]
            self.session,
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
