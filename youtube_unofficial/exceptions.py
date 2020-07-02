__all__ = ('AuthenticationError', 'TwoFactorError', 'UnexpectedError')


class AuthenticationError(Exception):
    pass


class TwoFactorError(AuthenticationError):
    pass


class UnexpectedError(RuntimeError):
    pass
