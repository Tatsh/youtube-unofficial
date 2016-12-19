from __future__ import unicode_literals


class AuthenticationError(Exception):
    pass


class TwoFactorError(AuthenticationError):
    pass


class ValidationError(ValueError):
    pass


class UnexpectedError(Exception):
    pass
