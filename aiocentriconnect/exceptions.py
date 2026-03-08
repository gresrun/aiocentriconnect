"""CentriConnect Exceptions"""


class CentriConnectError(Exception):
    """Generic CentriConnect exception."""


class CentriConnectDecodeError(CentriConnectError):
    """CentriConnect exception thrown when decoding a response fails."""

    def __init__(self, message, raw_body):
        """Init Decode error."""
        super().__init__(message)
        self.raw_body = raw_body

    def get_raw_body(self) -> str:
        """Return the raw body of the failing request."""
        return self.raw_body


class CentriConnectEmptyResponseError(CentriConnectError):
    """CentriConnect empty API response exception."""


class CentriConnectConnectionError(CentriConnectError):
    """CentriConnect connection exception."""


class CentriConnectConnectionTimeoutError(CentriConnectConnectionError):
    """CentriConnect connection timeout exception."""
