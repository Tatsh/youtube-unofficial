# encoding: utf-8
from __future__ import unicode_literals

from netrc import netrc
from os.path import expanduser
import json
import logging
import re

from bs4 import BeautifulSoup as Soup
from requests import Request
from six.moves.http_cookiejar import LoadError as CookieJarLoadError
from six.moves.http_cookiejar import MozillaCookieJar
import requests

from .exceptions import AuthenticationError, TwoFactorError, UnexpectedError
from .util import compat_str, html_hidden_inputs, remove_start, try_get


class YouTube(object):
    _LOGIN_URL = 'https://accounts.google.com/ServiceLogin'
    _LOOKUP_URL = 'https://accounts.google.com/_/signin/sl/lookup'
    _CHALLENGE_URL = 'https://accounts.google.com/_/signin/sl/challenge'
    _TFA_URL = 'https://accounts.google.com/_/signin/challenge?hl=en&TL={0}'

    _NETRC_MACHINE = 'youtube'
    _USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36')

    _HOMEPAGE_URL = 'https://www.youtube.com'
    _HISTORY_URL = 'https://www.youtube.com/feed/history'
    _FEED_CHANGE_AJAX_URL = ('https://www.youtube.com/feed_change_ajax'
                             '?action_give_feedback=1')
    _WATCH_LATER_URL = 'https://www.youtube.com/playlist?list=WL'
    _BROWSE_AJAX_URL = 'https://www.youtube.com/browse_ajax'
    _SERVICE_AJAX_URL = 'https://www.youtube.com/service_ajax'

    def __init__(self,
                 username=None,
                 password=None,
                 netrc_file=None,
                 cookies_path=None,
                 cookiejar_cls=MozillaCookieJar):
        if not netrc_file:
            self.netrc_file = expanduser('~/.netrc')
        else:
            self.netrc_file = netrc_file
        if not cookies_path:
            cookies_path = expanduser('~/.ytch-cookies.txt')

        self.username = username
        self.password = password

        self._log = logging.getLogger('youtube-unofficial')
        self._logged_in = False
        self._favorites_playlist_id = None

        self._sess = requests.Session()
        self._init_cookiejar(cookies_path, cls=cookiejar_cls)
        self._sess.cookies = self._cj
        self._sess.headers.update({
            'User-Agent': self._USER_AGENT,
        })

    def _auth(self):
        if not self.username:
            self._log.debug('Reading netrc at %s', self.netrc_file)

            try:
                (un, _, pw) = netrc(self.netrc_file).authenticators(
                    self._NETRC_MACHINE)
            except TypeError:
                raise AuthenticationError('No login info available')

            self.username = un
            self.password = pw
        else:
            self._log.debug('Username and password not from netrc')

        return self.username, self.password

    def _init_cookiejar(self, path, cls=MozillaCookieJar):
        self._log.debug('Initialising cookie jar (%s) at %s', cls.__name__,
                        path)

        try:
            with open(path):
                pass
        except IOError:
            with open(path, 'wb+'):
                pass
        self._cj = cls(path)

        if hasattr(self._cj, 'load'):
            try:
                self._cj.load()
            except CookieJarLoadError:
                self._log.debug('File %s for cookies does not yet exist', path)

    def _stdin_tfa_code_callback(self):
        try:
            import __builtin__  # flake8: noqa
            inp = getattr(__builtin__, 'raw_input')  # flake8: noqa
        except (ImportError, AttributeError):
            inp = input

        x = inp('2FA code: ')
        return x.strip()

    def _download_page(self,
                       url,
                       data=None,
                       method='get',
                       headers=None,
                       params=None,
                       json=False):
        if headers:
            self._sess.headers.update(headers)
        req = Request(method.upper(),
                      url,
                      cookies=self._cj,
                      data=data,
                      params=params)
        prepped = self._sess.prepare_request(req)
        del prepped.headers['accept-encoding']
        r = self._sess.send(prepped)
        r.raise_for_status()

        if not json:
            return r.content.decode('utf-8').strip()

        return r.json()

    def _download_page_soup(self, *args, **kwargs):
        return Soup(self._download_page(*args, **kwargs),
                    kwargs.pop('parser', 'html5lib'))

    def _remove_set_video_id_from_playlist(self,
                                           playlist_id,
                                           set_video_id,
                                           csn,
                                           xsrf_token,
                                           headers=None):
        """Removes a video from a playlist. The set_video_id is NOT the same as
        the video ID."""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        if not headers:
            content = self._download_page_soup(self._WATCH_LATER_URL)
            headers = self._ytcfg_headers(content)

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
            csn or '',
            'session_token':
            xsrf_token or ''
        }
        self._log.debug('Form data: %s', form_data)
        data = self._download_page(self._SERVICE_AJAX_URL,
                                   method='post',
                                   data=form_data,
                                   params=params,
                                   json=True,
                                   headers=headers)
        if data['code'] != 'SUCCESS':
            raise UnexpectedError(
                'Failed to delete video from Watch Later playlist')

    def _find_ytcfg(self, soup):
        return json.JSONDecoder().raw_decode(
            re.sub(
                r'.+ytcfg.set\(\{', '{',
                list(
                    filter(
                        lambda x: '"INNERTUBE_CONTEXT_CLIENT_VERSION":' in x.
                        text, soup.select('script')))[0].text.strip()))[0]

    def _ytcfg_headers(self, ytcfg):
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

    def _initial_data(self, content):
        return json.loads(
            re.sub(
                '^window[^=]+= ', '',
                list(
                    filter(lambda x: '"ytInitialData"' in x.text,
                           content.select('script')))[0].text.strip()).split(
                               '\n')[0][:-1])

    def _initial_guide_data(self, content):
        return json.loads(
            re.sub(
                '^var ytInitialGuideData = ', '',
                list(
                    filter(lambda x: 'var ytInitialGuideData =' in x.text,
                           content.select('script')))[0].text.strip()).split(
                               '\n')[0][:-1])

    def login(self, tfa_code_callback=None):
        """
        This is heavily based on youtube-dl's code.
        See https://goo.gl/J3YFSe
        """
        if self._logged_in:
            return

        if not tfa_code_callback:
            self._log.debug('Using default two-factor callback')
            tfa_code_callback = self._stdin_tfa_code_callback

        # Check if already logged in with cookies
        content = self._download_page('https://www.youtube.com/')
        if "'LOGGED_IN': true" in content:
            self._log.debug('Already logged in via cookies')
            self._logged_in = True

        if self._logged_in:
            return

        username, password = self._auth()

        login_page = self._download_page(self._LOGIN_URL)
        if not login_page:
            raise AuthenticationError('Failed to load login page')

        login_form = html_hidden_inputs(login_page)

        def req(url, f_req):
            data = login_form.copy()
            data.update({
                'pstMsg':
                1,
                'checkConnection':
                'youtube',
                'checkedDomains':
                'youtube',
                'hl':
                'en',
                'deviceinfo': ('[null,null,null,[],null,"US",null,null,[],'
                               '"GlifWebSignIn",null,[null,null,[]]]'),
                'f.req':
                json.dumps(f_req, allow_nan=False, separators=(','
                                                               ':')),
                'flowName':
                'GlifWebSignIn',
                'flowEntry':
                'ServiceLogin',
            })
            ret = self._download_page(url,
                                      data=data,
                                      method='post',
                                      headers={
                                          'Content-Type':
                                          ('application/x-www-form-urlencoded;'
                                           'charset=utf-8'),
                                          'Google-Accounts-XSRF':
                                          '1',
                                      })

            return json.loads(re.sub(r'^[^[]*', '', ret))

        lookup_req = [
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
                None, None,
                [
                    2, 1, None, 1,
                    ('https://accounts.google.com/ServiceLogin?passive=true'
                     '&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fnext%'
                     '3D%252F%26action_handle_signin%3Dtrue%26hl%3Den%26app%3D'
                     'desktop%26feature%3Dsign_in_button&hl=en&service=youtube'
                     '&uilel=3&requestPath=%2FServiceLogin&Page=PasswordSepara'
                     'tionSignIn'), None, [], 4
                ], 1, [None, None, []], None, None, None, True
            ],
            username,
        ]

        lookup_results = req(self._LOOKUP_URL, lookup_req)
        if not lookup_results:
            raise AuthenticationError('Failed to look up account information')

        user_hash = try_get(lookup_results, lambda x: x[0][2], compat_str)
        if not user_hash:
            raise AuthenticationError('Unable to extract user hash')

        challenge_req = [
            user_hash, None, 1, None,
            [1, None, None, None, [password, None, True]],
            [
                None, None,
                [
                    2, 1, None, 1,
                    ('https://accounts.google.com/ServiceLogin?passi'
                     've=true&continue=https%3A%2F%2Fwww.youtube.com'
                     '%2Fsignin%3Fnext%3D%252F%26action_handle_signi'
                     'n%3Dtrue%26hl%3Den%26app%3Ddesktop%26feature%3'
                     'Dsign_in_button&hl=en&service=youtube&uilel=3&'
                     'requestPath=%2FServiceLogin&Page=PasswordSepar'
                     'ationSignIn'), None, [], 4
                ], 1, [None, None, []], None, None, None, True
            ]
        ]

        challenge_results = req(self._CHALLENGE_URL, challenge_req)
        if not challenge_results:
            raise AuthenticationError('Challenge failed')

        login_res = try_get(challenge_results, lambda x: x[0][5], list)
        if login_res:
            login_msg = try_get(login_res, lambda x: x[5], compat_str)
            if login_msg == 'INCORRECT_ANSWER_ENTERED':
                raise AuthenticationError('Incorrect password')
            raise AuthenticationError('Other login error')

        res = try_get(challenge_results, lambda x: x[0][-1], list)
        if not res:
            raise AuthenticationError('Unable to extract result entry')

        tfa = try_get(res, lambda x: x[0][0], list)
        if tfa:
            tfa_str = try_get(tfa, lambda x: x[2], compat_str)
            if tfa_str == 'TWO_STEP_VERIFICATION':
                # SEND_SUCCESS - TFA code has been successfully sent to phone
                # QUOTA_EXCEEDED - reached the limit of TFA codes
                status = try_get(tfa, lambda x: x[5], compat_str)
                if status == 'QUOTA_EXCEEDED':
                    raise TwoFactorError('Exceeded the limit of TFA codes; '
                                         'try later')

                tl = try_get(challenge_results, lambda x: x[1][2], compat_str)
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
                    tfa_msg = try_get(tfa_res, lambda x: x[5], compat_str)
                    if tfa_msg == 'INCORRECT_ANSWER_ENTERED':
                        raise TwoFactorError('Unable to finish TFA: '
                                             'Invalid TFA code')
                    raise TwoFactorError(tfa_msg)

                check_cookie_url = try_get(tfa_results, lambda x: x[0][-1][2],
                                           compat_str)
        else:
            check_cookie_url = try_get(res, lambda x: x[2], compat_str)

        if not check_cookie_url:
            raise AuthenticationError('Unable to extract CheckCookie URL')

        check_cookie_results = self._download_page(check_cookie_url)

        if not check_cookie_results:
            raise AuthenticationError('Unable to log in')

        if 'https://myaccount.google.com/' not in check_cookie_results:
            raise AuthenticationError('Unable to log in')

        self._cj.save()
        self._logged_in = True

    def clear_watch_history(self):
        """Clears watch history"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        ytcfg = self._find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)
        headers['x-spf-previous'] = self._HISTORY_URL
        headers['x-spf-referer'] = self._HISTORY_URL
        init_data = self._initial_data(content)
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
                            json=True,
                            method='post')
        self._log.info('Successfully cleared history')

    def get_favorites_playlist_id(self):
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')
        if self._favorites_playlist_id:
            return self._favorites_playlist_id

        def check_section_items(items):
            for item in items:
                has_match = re.match(
                    r'^Favou?rites',  # FIXME This only works with English
                    item['guideEntryRenderer']['formattedTitle']['simpleText'])
                if has_match:
                    return (item['guideEntryRenderer']['entryData']
                            ['guideEntryData']['guideEntryId'])

        content = self._download_page_soup(self._HOMEPAGE_URL)
        gd = self._initial_guide_data(content)
        section_items = (
            gd['items'][0]['guideSectionRenderer']['items'][4]
            ['guideCollapsibleSectionEntryRenderer']['sectionItems'])

        found = check_section_items(section_items)
        if found:
            self._favorites_playlist_id = found
            return self._favorites_playlist_id

        section_items = (section_items[-1]['guideCollapsibleEntryRenderer']
                         ['expandableItems'])
        found = check_section_items(section_items)
        if not found:
            raise ValueError('Could not determine favourites playlist ID')

        self._favorites_playlist_id = found
        self._log.debug('Got favourites playlist ID: %s',
                        self._favorites_playlist_id)

        return self._favorites_playlist_id

    def clear_favorites(self):
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        self.clear_playlist(self.get_favorites_playlist_id())

    def get_playlist_info(self, playlist_id):
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        url = 'https://www.youtube.com/playlist?list={}'.format(playlist_id)
        content = self._download_page_soup(url)
        ytcfg = self._find_ytcfg(content)
        headers = self._ytcfg_headers(ytcfg)
        yt_init_data = self._initial_data(content)

        plvlr = (yt_init_data['contents']['twoColumnBrowseResultsRenderer']
                 ['tabs'][0]['tabRenderer']['content']['sectionListRenderer']
                 ['contents'][0]['itemSectionRenderer']['contents'][0]
                 ['playlistVideoListRenderer'])
        first_contents = plvlr['contents']

        next_cont = continuation = itct = None
        try:
            next_cont = plvlr['continuations'][0]['nextContinuationData']
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
                contents = self._download_page(self._BROWSE_AJAX_URL,
                                               params=params,
                                               json=True,
                                               headers=headers)
                response = contents[1]['response']
                first_contents += (
                    response['continuationContents']
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

        return first_contents

    def clear_playlist(self, playlist_id):
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
        ytcfg = self._find_ytcfg(content)
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
            self._remove_set_video_id_from_playlist(playlist_id,
                                                    set_video_id,
                                                    csn,
                                                    xsrf_token,
                                                    headers=headers)

    def clear_watch_later(self):
        self.clear_playlist('WL')

    def remove_video_id_from_favorites(self,
                                       video_id,
                                       headers=None,
                                       session_token=None):
        playlist_id = self.get_favorites_playlist_id()
        playlist_info = self.get_playlist_info(playlist_id)
        url = 'https://www.youtube.com/playlist?list={}'.format(playlist_id)
        content = self._download_page_soup(url)
        ytcfg = self._find_ytcfg(content)
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

        self._remove_set_video_id_from_playlist(playlist_id,
                                                set_video_id,
                                                ytcfg['EVENT_ID'],
                                                ytcfg['XSRF_TOKEN'],
                                                headers=headers)

    """FIXME Make the following methods work again"""

    def remove_video_id_from_history(self, video_id):
        """Delete history entries by video ID. Only handles first page of
        history"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        headers = self._ytcfg_headers(content)
        lockups = content.select(
            '[data-context-item-id="{}"]'.format(video_id))

        for lockup in lockups:
            try:
                button = lockup.select('button.dismiss-menu-choice')[0]
            except IndexError:
                continue

            feedback_token = button['data-feedback-token']
            itct = button['data-innertube-clicktracking']

            self._delete_history_entry_by_feedback_token(
                feedback_token, itct, headers)

    def _delete_history_entry_by_feedback_token(self, feedback_token, itct,
                                                headers):
        """Delete a single history entry by the feedback-token value found
        on the X button
        The feedback-token value is re-generated on every page load of
        _HISTORY_URL"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        headers = self._ytcfg_headers(content)
        post_data = dict(
            itct=itct,
            feedback_tokens=feedback_token,
            wait_for_response=1,
            session_token=headers['X-Youtube-Identity-Token'],
        )

        self._download_page_soup(self._FEED_CHANGE_AJAX_URL,
                                 data=post_data,
                                 method='post',
                                 headers=headers)
        self._cj.save()
