from http.cookiejar import CookieJar, LoadError, MozillaCookieJar
from netrc import netrc
from os.path import expanduser
from typing import (Any, Callable, Dict, Iterable, Iterator, Mapping, Optional,
                    Sequence, Tuple, Type, Union, cast)
import json
import logging
import re
import warnings
import sys

from bs4 import BeautifulSoup as Soup
from requests import Request
from typing_extensions import Final, Literal, overload
import requests

from .exceptions import AuthenticationError, TwoFactorError, UnexpectedError
from .typing import HasStringCode
from .typing.browse_ajax import BrowseAJAXSequence
from .typing.guide_data import GuideData, SectionItemDict
from .typing.playlist import PlaylistInfo
from .util import html_hidden_inputs, remove_start, try_get

__all__ = ('YouTube', )


def _stdin_tfa_code_callback() -> str:
    return input('2FA code: ').strip()


def _find_ytcfg(soup: Soup) -> Mapping[str, Any]:
    return cast(
        Mapping[str, Any],
        json.JSONDecoder().raw_decode(
            re.sub(
                r'.+ytcfg.set\(\{', '{',
                list(
                    filter(
                        lambda x: '"INNERTUBE_CONTEXT_CLIENT_VERSION":' in x.
                        text, soup.select('script')))[0].text.strip()))[0])


def _initial_data(content: Soup) -> Mapping[str, Any]:
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


def _initial_guide_data(content: Soup) -> GuideData:
    return cast(
        GuideData,
        json.loads(
            re.sub(
                '^var ytInitialGuideData = ', '',
                list(
                    filter(lambda x: 'var ytInitialGuideData =' in x.text,
                           content.select('script')))[0].text.strip()).split(
                               '\n')[0][:-1]))


class YouTube:
    _LOGIN_URL: Final = 'https://accounts.google.com/ServiceLogin'
    _LOOKUP_URL: Final = 'https://accounts.google.com/_/signin/sl/lookup'
    _CHALLENGE_URL: Final = 'https://accounts.google.com/_/signin/sl/challenge'
    _TFA_URL: Final = ('https://accounts.google.com/_/signin/challenge?hl=en&'
                       'TL={0}')

    _NETRC_MACHINE: Final = 'youtube'
    _USER_AGENT: Final = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36')

    _HOMEPAGE_URL: Final = 'https://www.youtube.com'
    _HISTORY_URL: Final = 'https://www.youtube.com/feed/history'
    _WATCH_LATER_URL: Final = 'https://www.youtube.com/playlist?list=WL'
    _BROWSE_AJAX_URL: Final = 'https://www.youtube.com/browse_ajax'
    _SERVICE_AJAX_URL: Final = 'https://www.youtube.com/service_ajax'

    def __init__(self,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 netrc_file: Optional[str] = None,
                 cookies_path: Optional[str] = None,
                 cookiejar_cls: Type[CookieJar] = MozillaCookieJar):
        if not netrc_file:
            self.netrc_file = expanduser('~/.netrc')
        else:
            self.netrc_file = netrc_file
        if not cookies_path:
            cookies_path = expanduser('~/.config/ytch-cookies.txt')

        self.username = username
        self.password = password

        self._log: Final = logging.getLogger('youtube-unofficial')
        self._logged_in = False
        self._favorites_playlist_id: Optional[str] = None

        self._sess: Final = requests.Session()
        self._init_cookiejar(cookies_path, cls=cookiejar_cls)
        self._sess.cookies = self._cj  # type: ignore[assignment]
        self._sess.headers.update({
            'User-Agent': self._USER_AGENT,
        })

    def _auth(self) -> Tuple[str, Optional[str]]:
        if not self.username:
            self._log.debug('Reading netrc at %s', self.netrc_file)
            data = netrc(self.netrc_file).authenticators(self._NETRC_MACHINE)
            un, _, pw = data if data else (None, None, None)
            if data:
                un, _, pw = data
            else:
                raise AuthenticationError('No login info available')
            self.username = un
            self.password = pw
        else:
            self._log.debug('Username and password not from netrc')

        return self.username, self.password

    def _init_cookiejar(self,
                        path: str,
                        cls: Type[CookieJar] = MozillaCookieJar) -> None:
        self._log.debug('Initialising cookie jar (%s) at %s', cls.__name__,
                        path)

        try:
            with open(path):
                pass
        except IOError:
            with open(path, 'wb+'):
                pass
        try:
            self._cj = cls(path)  # type: ignore[arg-type]
        except TypeError:
            self._cj = cls()

        if hasattr(self._cj, 'load'):
            try:
                self._cj.load()  # type: ignore[attr-defined]
            except LoadError:
                self._log.debug('File %s for cookies does not yet exist', path)

    def _download_page(
        self,
        url: str,
        data: Any = None,
        method: Literal['get', 'post'] = 'get',
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        return_json: bool = False
    ) -> Union[str, Sequence[Any], Mapping[str, Any]]:
        if headers:
            self._sess.headers.update(headers)
        req = Request(method.upper(),
                      url,
                      cookies=self._cj,
                      data=data,
                      params=params)
        prepped = self._sess.prepare_request(
            req)  # type: ignore[no-untyped-call]
        del prepped.headers['accept-encoding']
        r = self._sess.send(prepped)  # type: ignore[no-untyped-call]
        r.raise_for_status()

        if not return_json:
            return cast(str, r.text.strip())

        return cast(Mapping[str, Any], r.json())

    def _download_page_soup(self, *args: Any, **kwargs: Any) -> Soup:
        return Soup(self._download_page(*args, **kwargs),
                    kwargs.pop('parser', 'html5lib'))

    def _ytcfg_headers(self, ytcfg: Mapping[str, str]) -> Dict[str, str]:
        return {
            'x-youtube-page-cl': str(ytcfg['PAGE_CL']),
            'x-youtube-identity-token': ytcfg['ID_TOKEN'],
            'x-spf-referer': self._WATCH_LATER_URL,
            'x-youtube-utc-offset': '-240',
            'x-spf-previous': self._WATCH_LATER_URL,
            'x-youtube-client-version':
            ytcfg['INNERTUBE_CONTEXT_CLIENT_VERSION'],
            'x-youtube-variants-checksum': ytcfg['VARIANTS_CHECKSUM'],
            'x-youtube-client-name':
            str(ytcfg['INNERTUBE_CONTEXT_CLIENT_NAME'])
        }

    def login(  # pylint: disable=too-many-branches,too-many-statements
            self,
            tfa_code_callback: Optional[Callable[..., str]] = None) -> None:
        """
        This is heavily based on youtube-dl's code.
        See https://goo.gl/J3YFSe
        """
        if self._logged_in:
            return

        if not tfa_code_callback:
            self._log.debug('Using default two-factor callback')
            tfa_code_callback = _stdin_tfa_code_callback

        # Check if already logged in with cookies
        content = self._download_page_soup('https://www.youtube.com/')
        ytcfg = _find_ytcfg(content)
        if ytcfg['LOGGED_IN']:
            self._log.debug('Already logged in via cookies')
            self._logged_in = True

        if self._logged_in:
            return

        username, password = self._auth()

        login_page = cast(str, self._download_page(self._LOGIN_URL))
        if not login_page:
            raise AuthenticationError('Failed to load login page')

        login_form = html_hidden_inputs(login_page)

        def req(url: str, f_req: Any) -> Mapping[str, Any]:
            data = login_form.copy()
            data.update({
                'pstMsg':
                '1',
                'checkConnection':
                'youtube',
                'checkedDomains':
                'youtube',
                'hl':
                'en',
                'deviceinfo': ('[null,null,null,[],null,"US",null,null,[],'
                               '"GlifWebSignIn",null,[null,null,[]]]'),
                'f.req':
                json.dumps(f_req, allow_nan=False, separators=(',', ':')),
                'flowName':
                'GlifWebSignIn',
                'flowEntry':
                'ServiceLogin',
            })
            ret = cast(
                str,
                self._download_page(url,
                                    data=data,
                                    method='post',
                                    headers={
                                        'Content-Type':
                                        ('application/x-www-form-urlencoded;'
                                         'charset=utf-8'),
                                        'Google-Accounts-XSRF':
                                        '1',
                                    }))

            return cast(Mapping[str, Any],
                        json.loads(re.sub(r'^[^[]*', '', ret)))

        lookup_req: Sequence[Any] = [
            username,
            None,
            [],
            None,
            'US',
            None,
            None,
            2,
            False,
            True,
            [
                None,
                None,
                [
                    2,
                    1,
                    None,
                    1,
                    # cSpell: disable
                    ('https://accounts.google.com/ServiceLogin?passive=true'
                     '&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fnext%'
                     '3D%252F%26action_handle_signin%3Dtrue%26hl%3Den%26app%3D'
                     'desktop%26feature%3Dsign_in_button&hl=en&service=youtube'
                     '&uilel=3&requestPath=%2FServiceLogin&Page=PasswordSepara'
                     'tionSignIn'),
                    # cSpell: enable
                    None,
                    [],
                    4
                ],
                1,
                [None, None, []],
                None,
                None,
                None,
                True
            ],
            username,
        ]

        lookup_results = req(self._LOOKUP_URL, lookup_req)
        if not lookup_results:
            raise AuthenticationError('Failed to look up account information')

        user_hash = try_get(lookup_results, lambda x: x[0][2], str)
        if not user_hash:
            raise AuthenticationError('Unable to extract user hash')

        challenge_req = [
            user_hash,
            None,
            1,
            None,
            [1, None, None, None, [password, None, True]],
            [
                None,
                None,
                [
                    2,
                    1,
                    None,
                    1,
                    # cSpell: disable
                    ('https://accounts.google.com/ServiceLogin?passi'
                     've=true&continue=https%3A%2F%2Fwww.youtube.com'
                     '%2Fsignin%3Fnext%3D%252F%26action_handle_signi'
                     'n%3Dtrue%26hl%3Den%26app%3Ddesktop%26feature%3'
                     'Dsign_in_button&hl=en&service=youtube&uilel=3&'
                     'requestPath=%2FServiceLogin&Page=PasswordSepar'
                     'ationSignIn'),
                    # cSpell: enable
                    None,
                    [],
                    4
                ],
                1,
                [None, None, []],
                None,
                None,
                None,
                True
            ]
        ]

        try:
            challenge_results: Optional[Mapping[str, Any]] = req(
                self._CHALLENGE_URL, challenge_req)
        except requests.HTTPError:
            print(
                'Log in is broken. See '
                'https://github.com/ytdl-org/youtube-dl/issues/24508. For '
                'now, extract cookies from your browser in Netscape format '
                'and use the --cookies argument.',
                file=sys.stderr)
            challenge_results = None
        if not challenge_results:
            raise AuthenticationError('Challenge failed')

        login_res = try_get(challenge_results, lambda x: x[0][5], list)
        if login_res:
            login_msg = try_get(login_res, lambda x: x[5], str)
            if login_msg == 'INCORRECT_ANSWER_ENTERED':
                raise AuthenticationError('Incorrect password')
            raise AuthenticationError('Other login error')

        res = try_get(challenge_results, lambda x: x[0][-1], list)
        if not res:
            raise AuthenticationError('Unable to extract result entry')

        tfa = try_get(res, lambda x: x[0][0], list)
        if tfa:
            tfa_str = try_get(tfa, lambda x: x[2], str)
            if tfa_str == 'TWO_STEP_VERIFICATION':
                # SEND_SUCCESS - TFA code has been successfully sent to phone
                # QUOTA_EXCEEDED - reached the limit of TFA codes
                status = try_get(tfa, lambda x: x[5], str)
                if status == 'QUOTA_EXCEEDED':
                    raise TwoFactorError('Exceeded the limit of TFA codes; '
                                         'try later')

                tl = try_get(challenge_results, lambda x: x[1][2], str)
                if not tl:
                    raise TwoFactorError('Unable to extract TL')

                tfa_code = tfa_code_callback()
                tfa_code = remove_start(tfa_code, 'G-')

                if not tfa_code:
                    raise TwoFactorError('Two-factor authentication required')

                tfa_req = [
                    user_hash, None, 2, None,
                    [
                        9, None, None, None, None, None, None, None,
                        [None, tfa_code, True, 2]
                    ]
                ]

                tfa_results = req(self._TFA_URL.format(tl), tfa_req)

                if not tfa_results:
                    raise TwoFactorError('TFA code was not accepted')

                tfa_res = try_get(tfa_results, lambda x: x[0][5], list)
                if tfa_res:
                    tfa_msg = try_get(tfa_res, lambda x: x[5], str)
                    if tfa_msg == 'INCORRECT_ANSWER_ENTERED':
                        raise TwoFactorError('Unable to finish TFA: '
                                             'Invalid TFA code')
                    raise TwoFactorError(tfa_msg)

                check_cookie_url = try_get(tfa_results, lambda x: x[0][-1][2],
                                           str)
        else:
            check_cookie_url = try_get(res, lambda x: x[2], str)

        if not check_cookie_url:
            raise AuthenticationError('Unable to extract CheckCookie URL')

        check_cookie_results = self._download_page(check_cookie_url)

        if not check_cookie_results:
            raise AuthenticationError('Unable to log in')

        if 'https://myaccount.google.com/' not in check_cookie_results:
            raise AuthenticationError('Unable to log in')

        if hasattr(self._cj, 'save'):
            self._cj.save()  # type: ignore[attr-defined]
        self._logged_in = True

    def remove_set_video_id_from_playlist(
            self,
            playlist_id: str,
            set_video_id: str,
            csn: Optional[str] = None,
            xsrf_token: Optional[str] = None,
            headers: Optional[Mapping[str, str]] = None) -> None:
        """Removes a video from a playlist. The set_video_id is NOT the same as
        the video ID."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        if not headers or not csn or not xsrf_token:
            soup = self._download_page_soup(self._WATCH_LATER_URL)
            ytcfg = _find_ytcfg(soup)
            headers = self._ytcfg_headers(ytcfg)

        params = {'name': 'playlistEditEndpoint'}
        form_data = {
            'sej':
            json.dumps({
                'clickTrackingParams': '',
                'commandMetadata': {
                    'webCommandMetadata': {
                        'url': '/service_ajax',
                        'sendPost': True
                    }
                },
                'playlistEditEndpoint': {
                    'playlistId':
                    playlist_id,
                    'actions': [{
                        'setVideoId': set_video_id,
                        'action': 'ACTION_REMOVE_VIDEO'
                    }],
                    'params':
                    'CAE%3D',
                    'clientActions': [{
                        'playlistRemoveVideosAction': {
                            'setVideoIds': [set_video_id]
                        }
                    }]
                }
            }),
            'csn':
            csn or ytcfg['EVENT_ID'],
            'session_token':
            xsrf_token or ytcfg['XSRF_TOKEN']
        }
        data = cast(
            HasStringCode,
            self._download_page(self._SERVICE_AJAX_URL,
                                method='post',
                                data=form_data,
                                params=params,
                                return_json=True,
                                headers=headers))
        if data['code'] != 'SUCCESS':
            raise UnexpectedError(
                'Failed to delete video from Watch Later playlist')

    def clear_watch_history(self) -> None:
        """Clears watch history."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        ytcfg = _find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)
        headers['x-spf-previous'] = self._HISTORY_URL
        headers['x-spf-referer'] = self._HISTORY_URL
        init_data = _initial_data(content)
        params = {'name': 'feedbackEndpoint'}
        try:
            data = {
                'sej':
                json.dumps(
                    init_data['contents']['twoColumnBrowseResultsRenderer']
                    ['secondaryContents']['browseFeedActionsRenderer']
                    ['contents'][2]['buttonRenderer']['navigationEndpoint']
                    ['confirmDialogEndpoint']['content']
                    ['confirmDialogRenderer']['confirmButton']
                    ['buttonRenderer']['serviceEndpoint']),
                'csn':
                ytcfg['EVENT_ID'],
                'session_token':
                ytcfg['XSRF_TOKEN']
            }
        except KeyError:
            self._log.debug('Clear button is likely disabled. History is '
                            'likely empty')
            return

        self._download_page(self._SERVICE_AJAX_URL,
                            params=params,
                            data=data,
                            headers=headers,
                            return_json=True,
                            method='post')
        self._log.info('Successfully cleared history')

    def get_favorites_playlist_id(self) -> str:
        """Get the Favourites playlist ID."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')
        if self._favorites_playlist_id:
            return self._favorites_playlist_id

        def check_section_items(
                items: Iterable[SectionItemDict]) -> Optional[str]:
            for item in items:
                has_match = re.match(
                    r'^Favou?rites',  # FIXME This only works with English
                    item['guideEntryRenderer']['formattedTitle']['simpleText'])
                if has_match:
                    return (item['guideEntryRenderer']['entryData']
                            ['guideEntryData']['guideEntryId'])
            return None

        content = self._download_page_soup(self._HOMEPAGE_URL)
        gd = _initial_guide_data(content)
        section_items = (
            gd['items'][0]['guideSectionRenderer']['items'][4]
            ['guideCollapsibleSectionEntryRenderer']['sectionItems'])

        found = check_section_items(section_items)
        if found:
            self._favorites_playlist_id = found
            return self._favorites_playlist_id

        expandable_items = (section_items[-1]['guideCollapsibleEntryRenderer']
                            ['expandableItems'])
        found = check_section_items(expandable_items)
        if not found:
            raise ValueError('Could not determine favourites playlist ID')

        self._favorites_playlist_id = found
        self._log.debug('Got favourites playlist ID: %s',
                        self._favorites_playlist_id)

        return self._favorites_playlist_id

    def clear_favorites(self) -> None:
        """Removes all videos from the Favourites playlist."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        self.clear_playlist(self.get_favorites_playlist_id())

    def get_playlist_info(self, playlist_id: str) -> Iterator[PlaylistInfo]:
        """Get playlist information given a playlist ID."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        url = 'https://www.youtube.com/playlist?list={}'.format(playlist_id)
        content = self._download_page_soup(url)
        ytcfg = _find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)
        yt_init_data = _initial_data(content)

        video_list_renderer = (
            yt_init_data['contents']['twoColumnBrowseResultsRenderer']['tabs']
            [0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]
            ['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']
        )
        try:
            yield from video_list_renderer['contents']
        except KeyError:
            yield from []

        next_cont = continuation = itct = None
        try:
            next_cont = video_list_renderer['continuations'][0][
                'nextContinuationData']
            continuation = next_cont['continuation']
            itct = next_cont['clickTrackingParams']
        except KeyError:
            pass

        if continuation and itct:
            while True:
                params = {
                    'ctoken': continuation,
                    'continuation': continuation,
                    'itct': itct
                }
                contents = cast(
                    BrowseAJAXSequence,
                    self._download_page(self._BROWSE_AJAX_URL,
                                        params=params,
                                        return_json=True,
                                        headers=headers))
                response = contents[1]['response']
                yield from (response['continuationContents']
                            ['playlistVideoListContinuation']['contents'])

                try:
                    continuations = (
                        response['continuationContents']
                        ['playlistVideoListContinuation']['continuations'])
                except KeyError:
                    break
                next_cont = continuations[0]['nextContinuationData']
                itct = next_cont['clickTrackingParams']
                continuation = next_cont['continuation']

    def clear_playlist(self, playlist_id: str) -> None:
        """
        Removes all videos from the specified playlist.

        Use `WL` for Watch Later.
        """
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        playlist_info = self.get_playlist_info(playlist_id)
        url = 'https://www.youtube.com/playlist?list={}'.format(playlist_id)
        content = self._download_page_soup(url)
        ytcfg = _find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)
        csn = ytcfg['EVENT_ID']
        xsrf_token = ytcfg['XSRF_TOKEN']

        try:
            set_video_ids = list(
                map(lambda x: x['playlistVideoRenderer']['setVideoId'],
                    playlist_info))
        except KeyError:
            self._log.info('Caught KeyError. This probably means the playlist '
                           'is empty.')
            return

        for set_video_id in set_video_ids:
            self._log.debug('Deleting from playlist: set_video_id = %s',
                            set_video_id)
            self.remove_set_video_id_from_playlist(playlist_id,
                                                   set_video_id,
                                                   csn,
                                                   xsrf_token,
                                                   headers=headers)

    def clear_watch_later(self) -> None:
        """Removes all videos from the 'Watch Later' playlist."""
        self.clear_playlist('WL')

    def remove_video_id_from_favorites(
            self,
            video_id: str,
            headers: Optional[Mapping[str, str]] = None) -> None:
        """Removes a video from Favourites by video ID."""
        playlist_id = self.get_favorites_playlist_id()
        playlist_info = self.get_playlist_info(playlist_id)
        url = 'https://www.youtube.com/playlist?list={}'.format(playlist_id)
        content = self._download_page_soup(url)
        ytcfg = _find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)

        try:
            entry = list(
                filter(
                    lambda x: (x['playlistVideoRenderer']['navigationEndpoint']
                               ['watchEndpoint']['videoId']) == video_id,
                    playlist_info))[0]
        except IndexError:
            return

        set_video_id = entry['playlistVideoRenderer']['setVideoId']

        self.remove_set_video_id_from_playlist(playlist_id,
                                               set_video_id,
                                               ytcfg['EVENT_ID'],
                                               ytcfg['XSRF_TOKEN'],
                                               headers=headers)

    def get_history_info(self) -> Iterator[Mapping[str, Any]]:
        """Get information about the History playlist."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        init_data = _initial_data(content)
        ytcfg = _find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)

        section_list_renderer = (
            init_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]
            ['tabRenderer']['content']['sectionListRenderer'])
        for section_list in section_list_renderer['contents']:
            yield from section_list['itemSectionRenderer']['contents']
        try:
            next_continuation = (section_list_renderer['continuations'][0]
                                 ['nextContinuationData'])
        except KeyError:
            return

        continuation = next_continuation['continuation']
        itct = next_continuation['clickTrackingParams']

        params = {
            'ctoken': continuation,
            'continuation': continuation,
            'itct': itct
        }
        xsrf = ytcfg['XSRF_TOKEN']

        while True:
            resp = cast(
                BrowseAJAXSequence,
                self._download_page(self._BROWSE_AJAX_URL,
                                    return_json=True,
                                    headers=headers,
                                    data={'session_token': xsrf},
                                    method='post',
                                    params=params))
            contents = resp[1]['response']
            section_list_renderer = (
                contents['continuationContents']['sectionListContinuation'])
            for section_list in section_list_renderer['contents']:
                yield from section_list['itemSectionRenderer']['contents']

            try:
                continuations = section_list_renderer['continuations']
            except KeyError as e:
                self._log.debug('Caught KeyError: %s. Possible keys: %s', e,
                                ', '.join(section_list.keys()))
                break
            xsrf = resp[1]['xsrf_token']
            next_cont = continuations[0]['nextContinuationData']
            params['itct'] = next_cont['clickTrackingParams']
            params['ctoken'] = next_cont['continuation']
            params['continuation'] = next_cont['continuation']

    def remove_video_id_from_history(self, video_id: str) -> bool:
        """Delete a history entry by video ID."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        history_info = self.get_history_info()
        content = self._download_page_soup(self._HISTORY_URL)
        ytcfg = _find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)

        try:
            entry = list(
                filter(
                    lambda x: 'videoRenderer' in x and x['videoRenderer'][
                        'videoId'] == video_id, history_info))[0]
        except IndexError:
            return False

        form_data = {
            'sej':
            json.dumps(
                entry['videoRenderer']['menu']['menuRenderer']
                ['topLevelButtons'][0]['buttonRenderer']['serviceEndpoint']),
            'csn':
            ytcfg['EVENT_ID'],
            'session_token':
            ytcfg['XSRF_TOKEN'],
        }
        resp = cast(
            HasStringCode,
            self._download_page(self._SERVICE_AJAX_URL,
                                return_json=True,
                                data=form_data,
                                method='post',
                                headers=headers,
                                params={'name': 'feedbackEndpoint'}))

        return resp['code'] == 'SUCCESS'
