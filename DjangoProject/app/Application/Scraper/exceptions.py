class FetchError(Exception):
    """The target could not be reached at all (DNS, connection, timeout, TLS)."""


class ScrapeFailedError(Exception):
    """Every attempt ended without an HTTP response."""

    def __init__(self, url: str, attempts: int, last_error: FetchError):
        self.url = url
        self.attempts = attempts
        self.last_error = last_error
        noun = "attempt" if attempts == 1 else "attempts"
        super().__init__(f"Could not fetch {url} after {attempts} {noun}: {last_error}")
