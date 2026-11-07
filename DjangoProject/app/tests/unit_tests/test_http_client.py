from unittest import IsolatedAsyncioTestCase

import httpx

from DjangoProject.app.Application.Scraper.exceptions import FetchError
from DjangoProject.app.Infrastructure.http_client import HttpxFetcher


def fetcher_for(handler, **kwargs) -> HttpxFetcher:
    return HttpxFetcher(transport=httpx.MockTransport(handler), **kwargs)


class HttpxFetcherTests(IsolatedAsyncioTestCase):
    async def test_returns_status_and_body(self):
        fetcher = fetcher_for(lambda request: httpx.Response(200, text="<html>hi</html>"))

        response = await fetcher.fetch("https://example.com")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "<html>hi</html>")

    async def test_non_2xx_is_returned_not_raised(self):
        fetcher = fetcher_for(lambda request: httpx.Response(404, text="not found"))

        response = await fetcher.fetch("https://example.com/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, "not found")

    async def test_follows_redirects(self):
        def handler(request):
            if request.url.path == "/old":
                return httpx.Response(301, headers={"Location": "https://example.com/new"})
            return httpx.Response(200, text="new page")

        response = await fetcher_for(handler).fetch("https://example.com/old")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "new page")

    async def test_body_is_capped_at_max_bytes(self):
        fetcher = fetcher_for(lambda request: httpx.Response(200, text="x" * 1000), max_content_bytes=100)

        response = await fetcher.fetch("https://example.com")

        self.assertEqual(len(response.content), 100)

    async def test_uses_charset_from_headers(self):
        body = "Grüße".encode("latin-1")
        fetcher = fetcher_for(lambda request: httpx.Response(
            200, content=body, headers={"Content-Type": "text/html; charset=latin-1"}
        ))

        response = await fetcher.fetch("https://example.com")

        self.assertEqual(response.content, "Grüße")

    async def test_transport_errors_become_fetch_error(self):
        def handler(request):
            raise httpx.ConnectError("connection refused")

        with self.assertRaises(FetchError):
            await fetcher_for(handler).fetch("https://example.com")

    async def test_timeouts_become_fetch_error(self):
        def handler(request):
            raise httpx.ReadTimeout("timed out")

        with self.assertRaises(FetchError):
            await fetcher_for(handler).fetch("https://example.com")
