# encoding: utf-8
from __future__ import print_function
from netrc import netrc
from os.path import expanduser
import logging
import re
import sys

from bs4 import BeautifulSoup as Soup
from six.moves.http_cookiejar import (
    LoadError as CookieJarLoadError,
    MozillaCookieJar,
)
import requests

from .exceptions import (
    AuthenticationError,
    TwoFactorError,
    ValidationError,
    UnexpectedError,
)


class YouTube(object):
    _LOGIN_URL = 'https://accounts.google.com/ServiceLogin'
    _TWOFACTOR_URL = 'https://accounts.google.com/signin/challenge'
    _NETRC_MACHINE = 'youtube'
    _USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/52.0.2743.41 Safari/537.36')

    _CLEAR_HISTORY_URL = ('https://www.youtube.com/feed_ajax?'
                          'action_clear_watch_history=1&clear_dialog_shown=0')
    _HISTORY_URL = 'https://www.youtube.com/feed/history'
    _FEED_CHANGE_AJAX_URL = ('https://www.youtube.com/feed_change_ajax'
                             '?action_give_feedback=1')

    netrc_file = None
    username = None
    password = None
    cookies_path = None

    _sess = None
    _cj = None
    _log = logging.getLogger('youtube-unofficial')
    _logged_in = False

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
                (username, _, password) = netrc(netrc_file).authenticators(
                    self._NETRC_MACHINE)
            except TypeError:
                raise AuthenticationError('No login info available')

            self.username = username
            self.password = password
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
        """This is heavily based on youtube-dl's code."""
        if not tfa_code_callback:
            self._log.debug('Using default two-factor callback')
            tfa_code_callback = self._stdin_tfa_code_callback

        # Check if already logged in with cookies
        content = self._download_page('https://www.youtube.com/')
        if 'signin-container' not in content:
            self._log.debug('Already logged in via cookies')
            self._logged_in = True

        if self._logged_in:
            return

        username, password = self._auth()

        login_page = self._download_page(self._LOGIN_URL)
        if not login_page:
            raise AuthenticationError('Failed to load login page')

        galx = re.search(r'(?s)<input.+?name="GALX".+?value="(.+?)"',
                         login_page).group(1)
        login_data = {
            'continue': 'https://www.youtube.com/signin?action_handle_signin='
                        'true&feature=sign_in_button&hl=en_US&nomobiletemp=1',
            'Email': username,
            'GALX': galx,
            'Passwd': password,

            'PersistentCookie': 'yes',
            '_utf8': '霱',
            'bgresponse': 'js_disabled',
            'checkConnection': '',
            'checkedDomains': 'youtube',
            'dnConn': '',
            'pstMsg': '0',
            'rmShown': '1',
            'secTok': '',
            'signIn': 'Sign in',
            'timeStmp': '',
            'service': 'youtube',
            'uilel': '3',
            'hl': 'en_US',
        }

        login_results = self._download_page(self._LOGIN_URL,
                                            data=login_data,
                                            method='post')
        if not login_results:
            raise AuthenticationError('Failed to POST to login URL')

        try:
            if re.search(r'<[^>]+id="errormsg_0_Passwd"[^>]*>([^<]+)<',
                         login_results).group(1):
                raise AuthenticationError('Unable to login')
        except AttributeError:
            pass

        if re.search(r'id="errormsg_0_Passwd"', login_results):
            raise AuthenticationError('Please use your account password and '
                                      'a two-factor code instead of an '
                                      'application-specific password.')

        if re.search(r'(?i)<form[^>]* id="challenge"', login_results):
            if not tfa_code_callback:
                raise ValidationError('Must pass callback for 2FA challenge')
            tfa_code = re.sub(r'^G\-', '', tfa_code_callback())

            s = Soup(login_results, 'html5lib')
            challenge_form = s.select('#challenge')[0]

            tfa_form_strs = {}
            for el in challenge_form.select('[type="hidden"]'):
                tfa_form_strs[el['name']] = el['value']

            tfa_form_strs.update({
                'Pin': tfa_code,
                'TrustDevice': 'on',
            })

            tfa_results = self._download_page(self._TWOFACTOR_URL,
                                              data=tfa_form_strs,
                                              method='post')
            if not tfa_results:
                raise TwoFactorError('Unable to load results after POST of '
                                     'two-factor data')

            if re.search(r'(?i)<form[^>]* id="challenge"', tfa_results):
                raise TwoFactorError('Two-factor code expired or invalid '
                                     '(after some time). Please try again, '
                                     'or use a one-use backup code instead.')

            if re.search(r'(?i)<form[^>]* id="gaia_loginform"', tfa_results):
                raise TwoFactorError('unable to log in - did the page '
                                     'structure change?')

            if re.search(r'smsauth-interstitial-reviewsettings', tfa_results):
                raise TwoFactorError('Your Google account has a security '
                                     'notice. Please log in on your web '
                                     'browser, resolve the notice, and try '
                                     'again.')

        if re.search(r'(?i)<form[^>]* id="gaia_loginform"', login_results):
            raise AuthenticationError('unable to log in: bad username or '
                                      'password')

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
        lockups = content.select('[data-context-item-id="{}"]')

        for lockup in lockups:
            try:
                button = lockup.select('button.dismiss-menu-choice')[0]
            except IndexError:
                continue

            feedback_token = button['data-feedback-token']
            itct = button['data-feedback-token']

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
