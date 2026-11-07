from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FetchResponse:
    status_code: int
    content: str


class HttpFetcher(Protocol):
    async def fetch(self, url: str) -> FetchResponse:
        """Return the response for any HTTP status. Raise FetchError if no response was received."""
        ...


class ScrapeResultRepository(Protocol):
    async def save(self, *, url: str, status_code: int, content: str, success: bool) -> None: ...
