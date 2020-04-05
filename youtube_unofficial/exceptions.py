__all__ = (
    'AuthenticationError',
    'TwoFactorError',
    'UnexpectedError',
    'ValidationError',
)


class AuthenticationError(Exception):
    pass


class TwoFactorError(AuthenticationError):
    pass


class ValidationError(ValueError):
    pass


class UnexpectedError(RuntimeError):
    pass
