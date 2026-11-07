import asyncio
import logging
from dataclasses import dataclass

from .exceptions import FetchError, ScrapeFailedError
from .interfaces import FetchResponse, HttpFetcher, ScrapeResultRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScrapeOutcome:
    url: str
    status_code: int
    success: bool
    content: str
    attempts: int


def is_success_status(status_code: int) -> bool:
    return 200 <= status_code <= 299


class ScraperService:
    def __init__(
        self,
        fetcher: HttpFetcher,
        repository: ScrapeResultRepository,
        backoff_base_seconds: float = 0.0,
        backoff_max_seconds: float = 0.0,
    ):
        self._fetcher = fetcher
        self._repository = repository
        self._backoff_base = backoff_base_seconds
        self._backoff_max = backoff_max_seconds

    async def scrape(self, url: str, call_count: int) -> ScrapeOutcome:
        """
        Fetch `url` up to `call_count` times, stopping at the first 2xx response.

        The final response is persisted whether it succeeded or not. If no attempt
        produced an HTTP response, nothing is persisted and ScrapeFailedError is raised.
        """
        if call_count < 1:
            raise ValueError("call_count must be at least 1")

        last_response: FetchResponse | None = None
        last_error: FetchError | None = None
        attempts = 0

        for attempt in range(1, call_count + 1):
            attempts = attempt
            try:
                last_response = await self._fetcher.fetch(url)
                last_error = None
            except FetchError as exc:
                last_error = exc
                logger.info("Attempt %d/%d for %s failed: %s", attempt, call_count, url, exc)
            else:
                if is_success_status(last_response.status_code):
                    break
                logger.info(
                    "Attempt %d/%d for %s returned %d",
                    attempt, call_count, url, last_response.status_code,
                )

            if attempt < call_count:
                await self._wait_before_retry(attempt)

        if last_response is None:
            assert last_error is not None
            raise ScrapeFailedError(url, attempts, last_error)

        success = is_success_status(last_response.status_code)
        await self._repository.save(
            url=url,
            status_code=last_response.status_code,
            content=last_response.content,
            success=success,
        )
        return ScrapeOutcome(
            url=url,
            status_code=last_response.status_code,
            success=success,
            content=last_response.content,
            attempts=attempts,
        )

    async def _wait_before_retry(self, attempt: int) -> None:
        if self._backoff_base <= 0:
            return
        delay = min(self._backoff_base * 2 ** (attempt - 1), self._backoff_max)
        await asyncio.sleep(delay)
