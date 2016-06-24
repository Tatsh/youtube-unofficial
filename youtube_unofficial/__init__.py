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

    netrc_file = None
    username = None
    password = None
    cookies_path = None

    _sess = None
    _cj = None
    _log = logging.getLogger('youtube')
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
            try:
                (username, _, password) = netrc(netrc_file).authenticators(
                    self._NETRC_MACHINE)
            except TypeError:
                raise AuthenticationError('No login info available')

            self.username = username
            self.password = password

        return (self.username, self.password,)

    def _init_cookiejar(self, path, cls=MozillaCookieJar):
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
                pass

    def _stdin_tfa_code_callback():
        x = input('2FA code: ')
        return x.strip()

    def _download_page(self, url, data=None, method='get'):
        method = getattr(self._sess, method)

        r = method(url, cookies=self._cj, data=data)
        r.raise_for_status()

        return r.content.decode('utf-8').strip()

    def login(self, tfa_code_callback=None):
        """This is heavily based on youtube-dl's code."""
        if not tfa_code_callback:
            tfa_code_callback = self._stdin_tfa_code_callback

        # Check if already logged in with cookies
        content = self._download_page('https://www.youtube.com/')
        if 'signin-container' not in content:
            self._logged_in = True

        if self._logged_in:
            return

        username, password = self._auth()

        login_page = _download_page(self._LOGIN_URL)
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
                return False

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

    def _find_post_headers(self, content):
        # These values are retrieved from yt.setConfig() calls
        headers = {
            # INNERTUBE_CONTEXT_CLIENT_VERSION
            'X-YouTube-Client-Version': '1.20160622',
            # PAGE_BUILD_LABEL
            'X-YouTube-Page-Label': 'youtube_20160622_RC1',
            # XSRF_TOKEN
            'X-Youtube-Identity-Token': '??',
            # PAGE_CL
            'X-YouTube-Page-CL': '125557905',
            # VARIANTS_CHECKSUM
            'X-YouTube-Variants-Checksum': '3a2c42bceff5b0797002a8c3bf9eb7dd',
        }
        mapping = {
            'INNERTUBE_CONTEXT_CLIENT_VERSION': 'X-YouTube-Client-Version',
            'PAGE_BUILD_LABEL': 'X-YouTube-Page-Label',
            # also set data['session_token']
            'XSRF_TOKEN': 'X-Youtube-Identity-Token',
            'PAGE_CL': 'X-YouTube-Page-CL',
            'VARIANTS_CHECKSUM': 'X-YouTube-Variants-Checksum',
        }

        for script in content.select('script'):
            if 'src' in script:
                continue

            statements = [x.strip() for x in
                          ''.join(script.contents).split(';')]
            for stmt in statements:
                if not stmt.startswith('yt.setConfig'):
                    continue

                args = stmt[13:-2]
                for const_name, header_name in mapping.items():
                    if const_name in args:
                        quoted = re.escape(const_name)
                        m = re.search('[\{,]?["\']?' + quoted +
                                      '["\']?(?:[\:,])(?:\s+)([^\),\}]+)',
                                      args)
                        if not m:
                            _log.error('Did not find value for {} when in '
                                       'statement: {}'.format(const_name,
                                                              stmt))
                            sys.exit(1)
                        value = m.group(1).strip()
                        if value[0] in ("'", '"',):
                            value = value[1:]
                        if value[-1] in ("'", '"',):
                            value = value[:-1]

                        headers[header_name] = value

        return headers

    def clear_watch_history(self):
        """Clears watch history"""
        if not self._logged_in:
            raise AuthenticationError('This method requires a call to '
                                      'login() first')

        self._download_page(self._HISTORY_URL)
        content = Soup(self._download_page(self._HISTORY_URL),
                       'html5lib')

        headers = self._find_post_headers(content)
        post_data = dict(
            session_token=headers['X-Youtube-Identity-Token'],
        )

        self._sess.headers.update(headers)
        content = self._download_page(self._CLEAR_HISTORY_URL,
                                      data=post_data,
                                      method='post')
        self._cj.save()

        content = Soup(content, 'html5lib')
        selector = 'ol.section-list > li > ol.item-section > li > .yt-lockup'

        if len(content.select(selector)):
            raise UnexpectedError('Failed to clear history')
