# encoding: utf-8
from __future__ import unicode_literals
from netrc import netrc
from os.path import expanduser
import json
import logging
import re
import sys

from bs4 import BeautifulSoup as Soup
from requests.exceptions import HTTPError
from six.moves.http_cookiejar import (
    LoadError as CookieJarLoadError,
    MozillaCookieJar,
)
from six.moves.urllib.parse import parse_qsl, urlparse
from youtube_dl.compat import compat_str
from youtube_dl.extractor.common import InfoExtractor
from youtube_dl.utils import remove_start, try_get
import requests

from .exceptions import (
    AuthenticationError,
    TwoFactorError,
    ValidationError,
    UnexpectedError,
)


class YouTube(object):
    _LOGIN_URL = 'https://accounts.google.com/ServiceLogin'
    _LOOKUP_URL = 'https://accounts.google.com/_/signin/sl/lookup'
    _CHALLENGE_URL = 'https://accounts.google.com/_/signin/sl/challenge'
    _TFA_URL = 'https://accounts.google.com/_/signin/challenge?hl=en&TL={0}'

    _NETRC_MACHINE = 'youtube'
    _USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/52.0.2743.41 Safari/537.36')

    _CLEAR_HISTORY_URL = ('https://www.youtube.com/feed_ajax?'
                          'action_clear_watch_history=1&clear_dialog_shown=0')
    _HISTORY_URL = 'https://www.youtube.com/feed/history?disable_polymer=true'
    _FEED_CHANGE_AJAX_URL = ('https://www.youtube.com/feed_change_ajax'
                             '?action_give_feedback=1')
    _WATCH_LATER_URL = ('https://www.youtube.com/playlist?list=WL&'
                        'disable_polymer=true')
    _PLAYLIST_REMOVE_AJAX_URL = ('https://www.youtube.com/playlist_edit_servi'
                                 'ce_ajax/?action_remove_video=1')

    netrc_file = None
    username = None
    password = None
    cookies_path = None

    _sess = None
    _cj = None
    _log = logging.getLogger('youtube-unofficial')
    _logged_in = False
    _favorites_playlist_id = None

    def __init__(self,
                 username=None,
                 password=None,
                 netrc_file=None,
                 cookies_path=None,
                 cookiejar_cls=MozillaCookieJar):
        if not netrc_file:
            self.netrc_file = expanduser('~/.netrc')
        if not cookies_path:
            cookies_path = expanduser('~/.ytch-cookies.txt')

        self.username = username
        self.password = password

        self._sess = requests.Session()
        self._init_cookiejar(cookies_path, cls=cookiejar_cls)
        self._sess.cookies = self._cj
        self._sess.headers.update({
            'User-Agent': self._USER_AGENT,
        })

    def _auth(self):
        if not self.username:
            self._log.debug('Reading netrc at {}'.format(self.netrc_file))

            try:
                (un, _, pw) = netrc(self.netrc_file).authenticators(
                    self._NETRC_MACHINE)
            except TypeError:
                raise AuthenticationError('No login info available')

            self.username = un
            self.password = pw
        else:
            self._log.debug('Username and password not from netrc')

        return (self.username, self.password,)

    def _init_cookiejar(self, path, cls=MozillaCookieJar):
        self._log.debug('Initialise cookie jar ({}) at {}'.format(
            cls.__name__, path))

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
                self._log.debug('File {} for cookies does not yet '
                                'exist'.format(path))

    def _stdin_tfa_code_callback(self):
        try:
            import __builtin__  # flake8: noqa
            input = getattr(__builtin__, 'raw_input')  # flake8: noqa
        except (ImportError, AttributeError):
            pass

        x = input('2FA code: ')
        return x.strip()

    def _download_page(self, url, data=None, method='get', headers=None):
        method = getattr(self._sess, method)

        if headers:
            self._sess.headers.update(headers)

        r = method(url, cookies=self._cj, data=data, headers=headers)
        r.raise_for_status()

        return r.content.decode('utf-8').strip()

    def _download_page_soup(self, *args, **kwargs):
        content = self._download_page(*args, **kwargs)
        parser = kwargs.pop('parser', 'html5lib')
        return Soup(content, parser)

    def login(self, tfa_code_callback=None):
        """
        This is heavily based on youtube-dl's code.
        See https://goo.gl/J3YFSe
        """
        if not tfa_code_callback:
            self._log.debug('Using default two-factor callback')
            tfa_code_callback = self._stdin_tfa_code_callback

        # Check if already logged in with cookies
        content = self._download_page('https://www.youtube.com/')
        if '{"key":"logged_in","value":"0"}' not in content:
            self._log.debug('Already logged in via cookies')
            self._logged_in = True

        if self._logged_in:
            return

        username, password = self._auth()

        login_page = self._download_page(self._LOGIN_URL)
        if not login_page:
            raise AuthenticationError('Failed to load login page')

        login_form = InfoExtractor._hidden_inputs(login_page)

        def req(url, f_req):
            data = login_form.copy()
            data.update({
                'pstMsg': 1,
                'checkConnection': 'youtube',
                'checkedDomains': 'youtube',
                'hl': 'en',
                'deviceinfo': ('[null,null,null,[],null,"US",null,null,[],'
                               '"GlifWebSignIn",null,[null,null,[]]]'),
                'f.req': json.dumps(f_req),
                'flowName': 'GlifWebSignIn',
                'flowEntry': 'ServiceLogin',
            })
            ret = self._download_page(url, data=data, method='post', headers={
                'Content-Type': ('application/x-www-form-urlencoded;'
                                 'charset=utf-8'),
                'Google-Accounts-XSRF': '1',
            })

            return json.loads(re.sub(r'^[^[]*', '', ret))

        lookup_req = [
            username,
            None, [], None, 'US', None, None, 2, False, True,
            [
                None, None,
                [2, 1, None, 1,
                 ('https://accounts.google.com/ServiceLogin?passive=true'
                  '&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fnext%3D'
                  '%252F%26action_handle_signin%3Dtrue%26hl%3Den%26app%3Ddesk'
                  'top%26feature%3Dsign_in_button&hl=en&service=youtube&uilel'
                  '=3&requestPath=%2FServiceLogin&Page=PasswordSeparationSign'
                  'In'),
                 None, [], 4],
                1, [None, None, []], None, None, None, True
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
            user_hash,
            None, 1, None, [1, None, None, None, [password, None, True]],
            [
                None, None, [2, 1, None, 1,
                             ('https://accounts.google.com/ServiceLogin?passi'
                              've=true&continue=https%3A%2F%2Fwww.youtube.com'
                              '%2Fsignin%3Fnext%3D%252F%26action_handle_signi'
                              'n%3Dtrue%26hl%3Den%26app%3Ddesktop%26feature%3'
                              'Dsign_in_button&hl=en&service=youtube&uilel=3&'
                              'requestPath=%2FServiceLogin&Page=PasswordSepar'
                              'ationSignIn'),
                             None, [], 4],
                1, [None, None, []], None, None, None, True
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

                check_cookie_url = try_get(
                    tfa_results, lambda x: x[0][-1][2], compat_str)
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

    def _find_post_headers(self, soup):
        # Retrieved by regex'ing the JS
        headers = {}
        mapping = {
            'INNERTUBE_CONTEXT_CLIENT_VERSION': 'X-YouTube-Client-Version',
            'PAGE_BUILD_LABEL': 'X-YouTube-Page-Label',
            # also set data['session_token']
            # NOTE It seems only X-Youtube-Identity-Token is required
            'XSRF_TOKEN': 'X-Youtube-Identity-Token',
            'PAGE_CL': 'X-YouTube-Page-CL',
            'VARIANTS_CHECKSUM': 'X-YouTube-Variants-Checksum',
        }

        for script in soup.select('script'):
            if 'src' in script:
                continue

            statements = [x.strip() for x in
                          ''.join(script.contents).split(';')]
            for stmt in statements:
                for const_name, header_name in mapping.items():
                    if header_name in headers:
                        continue

                    if const_name in stmt:
                        quoted = re.escape(const_name)
                        regex = (r'[\{,]?["\']?' + quoted +
                                 r'["\']?(?:[\:,])(?:\s+)([^\),\}]+)')
                        m = re.search(regex, stmt)
                        if not m:
                            self._log.error('Did not find value for {} when '
                                            'in statement: {}'.format(
                                                const_name, stmt))
                            continue
                        value = m.group(1).strip()
                        if value[0] in ("'", '"',):
                            value = value[1:]
                        if value[-1] in ("'", '"',):
                            value = value[:-1]

                        log_value = (value if len(value) < 24
                                     else value[0:24] + '...')
                        self._log.debug('Add header: {}: {}'.format(
                            header_name, log_value))
                        headers[header_name] = value

        if len(headers) != len(mapping):
            missing = []
            for k, v in mapping.items():
                if k not in headers:
                    missing.append(k)
            missing = ', '.join(missing)

            raise UnexpectedError('Expected to find all parameters. '
                                  'Missing: {}'.format(missing))

        return headers

    def remove_video_id_from_history(self, video_id):
        """Delete history entries by video ID. Only handles first page of
        history"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        headers = self._find_post_headers(content)
        lockups = content.select('[data-context-item-id="{}"]'.format(
            video_id))

        for lockup in lockups:
            try:
                button = lockup.select('button.dismiss-menu-choice')[0]
            except IndexError:
                continue

            feedback_token = button['data-feedback-token']
            itct = button['data-innertube-clicktracking']

            self._delete_history_entry_by_feedback_token(feedback_token,
                                                         itct,
                                                         headers)

    def _delete_history_entry_by_feedback_token(self,
                                                feedback_token,
                                                itct,
                                                headers):
        """Delete a single history entry by the feedback-token value found
        on the X button
        The feedback-token value is re-generated on every page load of
        _HISTORY_URL"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        headers = self._find_post_headers(content)
        post_data = dict(
            itct=itct,
            feedback_tokens=feedback_token,
            wait_for_response=1,
            session_token=headers['X-Youtube-Identity-Token'],
        )

        content = self._download_page_soup(self._FEED_CHANGE_AJAX_URL,
                                           data=post_data,
                                           method='post',
                                           headers=headers)
        self._cj.save()

    def clear_watch_history(self):
        """Clears watch history"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._HISTORY_URL)
        headers = self._find_post_headers(content)
        post_data = dict(
            session_token=headers['X-Youtube-Identity-Token'],
        )

        content = self._download_page_soup(self._CLEAR_HISTORY_URL,
                                           data=post_data,
                                           method='post',
                                           headers=headers)
        self._cj.save()

        selector = 'ol.section-list > li > ol.item-section > li > .yt-lockup'

        if len(content.select(selector)):
            raise UnexpectedError('Failed to clear history')
        else:
            self._log.info('Successfully cleared history')

    def remove_video_id_from_playlist(self,
                                      playlist_id,
                                      set_video_id,
                                      headers=None,
                                      session_token=None):
        """Removes a video from the 'Watch later' playlist
        set_video_id is taken from the data-set-video-id attribute on the table
        row (tr element)
        """
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        if not headers:
            content = self._download_page_soup(self._WATCH_LATER_URL)
            headers = self._find_post_headers(content)
        if not session_token:
            session_token = headers['X-Youtube-Identity-Token']

        post_data = dict(
            playlist_id=playlist_id,
            set_video_id=set_video_id,
            session_token=session_token,
        )
        try:
            s = self._download_page(self._PLAYLIST_REMOVE_AJAX_URL,
                                    data=post_data,
                                    method='post',
                                    headers=headers)
        except HTTPError:
            return False

        return 'header_html' in json.loads(s)

    def _get_favorites_playlist_id(self):
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')
        if self._favorites_playlist_id:
            return self._favorites_playlist_id

        content = self._download_page_soup(self._HISTORY_URL)
        link = content.select('li.guide-notification-item > '
                              'a[title="Favorites"]')

        href = link[0]['href']
        li = dict(parse_qsl(urlparse(href).query,
                            keep_blank_values=False,
                            strict_parsing=True))['list']
        self._favorites_playlist_id = li

        return self._favorites_playlist_id

    def remove_video_id_from_favorites(self,
                                       video_id,
                                       headers=None,
                                       session_token=None):
        favorites_playlist_id = self._get_favorites_playlist_id()

        return self.remove_video_id_from_playlist(favorites_playlist_id,
                                                  video_id,
                                                  headers=headers,
                                                  session_token=session_token)

    def clear_favorites(self):
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        playlist_id = self._get_favorites_playlist_id()
        url = ('https://www.youtube.com/playlist?list={}&'
               'disable_polymer=true').format(playlist_id)
        content = self._download_page_soup(url)
        headers = self._find_post_headers(content)
        session_token = headers['X-Youtube-Identity-Token']
        rows = content.select('#pl-video-list > table > tbody > tr')

        for row in rows:
            self.remove_video_id_from_favorites(row['data-set-video-id'],
                                                headers=headers,
                                                session_token=session_token)

    def clear_watch_later(self):
        """Removes all videos from the 'Watch Later' playlist"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        content = self._download_page_soup(self._WATCH_LATER_URL)
        headers = self._find_post_headers(content)
        session_token = headers['X-Youtube-Identity-Token']

        for row in content.select('[data-set-video-id]'):
            self.remove_video_id_from_playlist('WL',
                                               row['data-set-video-id'],
                                               headers=headers,
                                               session_token=session_token)
