class AuthenticationError(Exception):
    pass


class TwoFactorError(AuthenticationError):
    pass


class ValidationError(Exception):
    pass


class UnexpectedError(Exception):
    pass
