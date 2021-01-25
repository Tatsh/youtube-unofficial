from http.cookiejar import CookieJar
from netrc import netrc
from os.path import expanduser
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, cast
import json
import logging
import re
import sys

from typing_extensions import Final
import requests

from .constants import (CHALLENGE_URL, LOGIN_URL, LOOKUP_URL, NETRC_MACHINE,
                        TFA_URL)
from .download import DownloadMixin
from .exceptions import AuthenticationError, TwoFactorError
from .util import html_hidden_inputs, remove_start, try_get
from .ytcfg import find_ytcfg

__all__ = ('YouTubeLogin', )


def _stdin_tfa_code_callback() -> str:
    return input('2FA code: ').strip()


class YouTubeLogin(DownloadMixin):
    def __init__(self,
                 session: requests.Session,
                 cookies: CookieJar,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 netrc_file: Optional[str] = None,
                 logged_in: Optional[bool] = False):
        if not netrc_file:
            netrc_file = expanduser('~/.netrc')
        self.netrc_file = netrc_file
        self.username = username
        self.password = password
        self._cj = cookies
        self._sess = session
        self._log: Final[logging.Logger] = logging.getLogger(
            'youtube-unofficial')
        self.logged_in = bool(logged_in)

    def login(  # pylint: disable=too-many-branches,too-many-statements
            self,
            tfa_code_callback: Optional[Callable[..., str]] = None) -> None:
        """
        This is heavily based on youtube-dl's code.
        See https://goo.gl/J3YFSe
        """
        if self.logged_in:
            return
        if not tfa_code_callback:
            self._log.debug('Using default two-factor callback')
            tfa_code_callback = _stdin_tfa_code_callback
        # Check if already logged in with cookies
        content = self._download_page_soup('https://www.youtube.com/')
        ytcfg = find_ytcfg(content)
        if ytcfg['LOGGED_IN']:
            self._log.debug('Already logged in via cookies')
            self.logged_in = True
        if self.logged_in:
            return
        username, password = self._auth()
        login_page = cast(str, self._download_page(LOGIN_URL))
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
        lookup_results = req(LOOKUP_URL, lookup_req)
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
                CHALLENGE_URL, challenge_req)
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
        check_cookie_url = try_get(res, lambda x: x[2], str)
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
                tfa_code = cast(str, remove_start(tfa_code, 'G-'))
                if not tfa_code:
                    raise TwoFactorError('Two-factor authentication required')
                tfa_req = [
                    user_hash, None, 2, None,
                    [
                        9, None, None, None, None, None, None, None,
                        [None, tfa_code, True, 2]
                    ]
                ]
                tfa_results = req(TFA_URL.format(tl), tfa_req)
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
        if not check_cookie_url:
            raise AuthenticationError('Unable to extract CheckCookie URL')
        check_cookie_results = self._download_page(check_cookie_url)
        if not check_cookie_results:
            raise AuthenticationError('Unable to log in')
        if 'https://myaccount.google.com/' not in check_cookie_results:
            raise AuthenticationError('Unable to log in')
        if hasattr(self._cj, 'save'):
            self._cj.save()  # type: ignore[attr-defined]
        self.logged_in = True

    def _auth(self) -> Tuple[str, Optional[str]]:
        if not self.username:
            assert self.netrc_file is not None
            self._log.debug('Reading netrc at %s', self.netrc_file)
            data = netrc(self.netrc_file).authenticators(NETRC_MACHINE)
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
