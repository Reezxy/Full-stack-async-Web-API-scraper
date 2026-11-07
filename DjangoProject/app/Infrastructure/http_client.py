import httpx

from DjangoProject.app.Application.Scraper.exceptions import FetchError
from DjangoProject.app.Application.Scraper.interfaces import FetchResponse

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AsyncWebScraper/1.0)",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}


class HttpxFetcher:
    """HttpFetcher implementation backed by httpx.AsyncClient."""

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_content_bytes: int = 5 * 1024 * 1024,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._timeout = httpx.Timeout(timeout_seconds)
        self._max_content_bytes = max_content_bytes
        self._transport = transport

    async def fetch(self, url: str) -> FetchResponse:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers=DEFAULT_HEADERS,
                transport=self._transport,
            ) as client:
                async with client.stream("GET", url) as response:
                    body = await self._read_limited(response)
                    return FetchResponse(
                        status_code=response.status_code,
                        content=self._decode(body, response.encoding),
                    )
        except (httpx.HTTPError, httpx.InvalidURL) as exc:
            raise FetchError(str(exc) or type(exc).__name__) from exc

    async def _read_limited(self, response: httpx.Response) -> bytes:
        # Stop reading once the limit is hit so a huge document cannot exhaust memory.
        chunks: list[bytes] = []
        size = 0
        async for chunk in response.aiter_bytes():
            remaining = self._max_content_bytes - size
            if len(chunk) >= remaining:
                chunks.append(chunk[:remaining])
                break
            chunks.append(chunk)
            size += len(chunk)
        return b"".join(chunks)

    @staticmethod
    def _decode(body: bytes, encoding: str | None) -> str:
        try:
            return body.decode(encoding or "utf-8", errors="replace")
        except LookupError:
            return body.decode("utf-8", errors="replace")
