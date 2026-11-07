import json
from unittest.mock import patch

import httpx
from django.test import TestCase

from DjangoProject.app.Application.Scraper.service import ScraperService
from DjangoProject.app.Infrastructure.http_client import HttpxFetcher
from DjangoProject.app.Infrastructure.repositories import DjangoScrapeResultRepository
from DjangoProject.app.models import ScrapeResult

SERVICE_FACTORY = "DjangoProject.app.API.Views.scrape_view.build_scraper_service"


def service_with(handler) -> ScraperService:
    """Real service and repository, only the network is replaced."""
    return ScraperService(
        fetcher=HttpxFetcher(transport=httpx.MockTransport(handler)),
        repository=DjangoScrapeResultRepository(),
    )


class ScrapeViewTests(TestCase):
    async def post(self, payload, **extra):
        body = payload if isinstance(payload, str) else json.dumps(payload)
        return await self.async_client.post("/scrape/", body, content_type="application/json", **extra)

    async def test_successful_scrape_returns_201_and_persists(self):
        html = "<html>" + "a" * 1000 + "</html>"
        with patch(SERVICE_FACTORY, return_value=service_with(lambda r: httpx.Response(200, text=html))):
            response = await self.post({"url": "https://example.com", "call_count": 3})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"status": 200, "success": True, "content": html})

        record = await ScrapeResult.objects.aget()
        self.assertEqual(record.url, "https://example.com")
        self.assertEqual(record.status_code, 200)
        self.assertTrue(record.success)
        self.assertEqual(record.content_preview, html[:500])
        self.assertIsNotNone(record.created_at)

    async def test_failed_upstream_still_returns_201_with_success_false(self):
        calls = []

        def handler(request):
            calls.append(request)
            return httpx.Response(503, text="unavailable")

        with patch(SERVICE_FACTORY, return_value=service_with(handler)):
            response = await self.post({"url": "https://example.com", "call_count": 3})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"status": 503, "success": False, "content": "unavailable"})
        self.assertEqual(len(calls), 3)
        record = await ScrapeResult.objects.aget()
        self.assertFalse(record.success)
        self.assertEqual(record.status_code, 503)

    async def test_unreachable_host_returns_422(self):
        def handler(request):
            raise httpx.ConnectError("Name or service not known")

        with patch(SERVICE_FACTORY, return_value=service_with(handler)):
            response = await self.post({"url": "https://does-not-exist.invalid", "call_count": 2})

        self.assertEqual(response.status_code, 422)
        self.assertIn("after 2 attempts", response.json()["error"])
        self.assertEqual(await ScrapeResult.objects.acount(), 0)

    async def test_invalid_json_returns_400(self):
        response = await self.post("{not json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Request body must be valid JSON."})

    async def test_non_object_json_returns_400(self):
        response = await self.post("[1, 2]")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Request body must be a JSON object."})

    async def test_validation_errors_return_422(self):
        cases = [
            ({"call_count": 1}, "url"),
            ({"url": "https://example.com"}, "call_count"),
            ({"url": "not a url", "call_count": 1}, "url"),
            ({"url": "ftp://example.com", "call_count": 1}, "url"),
            ({"url": "https://example.com", "call_count": 0}, "call_count"),
            ({"url": "https://example.com", "call_count": 11}, "call_count"),
            ({"url": "https://example.com", "call_count": "three"}, "call_count"),
            ({"url": "https://example.com", "call_count": 1.5}, "call_count"),
        ]
        for payload, field in cases:
            with self.subTest(payload=payload):
                response = await self.post(payload)
                self.assertEqual(response.status_code, 422)
                self.assertIn(field, response.json()["error"])

    async def test_unexpected_error_returns_generic_500(self):
        class BrokenService:
            async def scrape(self, url, call_count):
                raise RuntimeError("database is locked")

        with patch(SERVICE_FACTORY, return_value=BrokenService()), self.assertLogs(
            "DjangoProject.app.API.Views.scrape_view", level="ERROR"
        ):
            response = await self.post({"url": "https://example.com", "call_count": 1})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"error": "Internal server error"})

    async def test_get_is_not_allowed(self):
        response = await self.async_client.get("/scrape/")
        self.assertEqual(response.status_code, 405)

    async def test_cors_allows_frontend_origin(self):
        response = await self.async_client.options(
            "/scrape/",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3000")
